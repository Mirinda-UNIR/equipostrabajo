import streamlit as st
import pandas as pd
from collections import defaultdict
from io import BytesIO

# --- Configuración ---
REGIONES = {
    "Todas": None,
    "LATAM": ["Argentina", "México", "Colombia", "Chile", "Perú", "Uruguay", "Ecuador"],
    "Europa": ["España", "Francia", "Alemania", "Italia", "Portugal"],
}

GRUPO_MIN = 4
GRUPO_MAX = 5

# --- Funciones ---
def formar_grupos(lista_estudiantes):
    grupos = []
    i = 0
    while i < len(lista_estudiantes):
        grupo = lista_estudiantes[i:i + GRUPO_MAX]
        if len(grupo) >= GRUPO_MIN:
            grupos.append(grupo)
        i += GRUPO_MAX
    return grupos

def pertenece_a_region(pais, region):
    return pais in region if region else True

def generar_grupos(df, region_nombre):
    estudiantes = defaultdict(lambda: {'nombre': '', 'email': '', 'pais': '', 'asignaturas': set()})
    for _, row in df.iterrows():
        sid = row['estudiante_id']
        estudiantes[sid]['nombre'] = row['nombre']
        estudiantes[sid]['email'] = row['email']
        estudiantes[sid]['pais'] = row['país']
        estudiantes[sid]['asignaturas'].add(row['asignatura'])

    region = REGIONES.get(region_nombre)
    estudiantes_filtrados = {
        sid: data for sid, data in estudiantes.items()
        if pertenece_a_region(data['pais'], region)
    }

    agrupados = defaultdict(list)
    for sid, data in estudiantes_filtrados.items():
        key = frozenset(data['asignaturas'])
        agrupados[key].append((sid, data))

    salida = []
    grupo_id = 1
    for asignaturas, estudiantes_conj in agrupados.items():
        grupos = formar_grupos(estudiantes_conj)
        for grupo in grupos:
            for sid, data in grupo:
                salida.append({
                    "grupo_id": grupo_id,
                    "estudiante_id": sid,
                    "nombre": data['nombre'],
                    "email": data['email'],
                    "pais": data['pais'],
                    "asignaturas": ", ".join(sorted(asignaturas))
                })
            grupo_id += 1

    return pd.DataFrame(salida)

# --- Interfaz ---
st.title("Formador de Grupos para Máster")
st.markdown("Sube un archivo Excel con las matrículas de estudiantes y genera grupos de 4 a 5 personas con asignaturas en común.")

archivo = st.file_uploader("📂 Sube tu archivo Excel (.xlsx)", type=["xlsx"])
region = st.selectbox("🌍 Filtrar por región geográfica:", list(REGIONES.keys()))

if archivo:
    try:
        df = pd.read_excel(archivo)
        if st.button("🚀 Generar Grupos"):
            df_resultado = generar_grupos(df, region)

            st.success("Grupos generados correctamente ✅")

            output = BytesIO()
            df_resultado.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="📥 Descargar archivo Excel con los grupos",
                data=output,
                file_name="grupos_generados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.dataframe(df_resultado)

    except Exception as e:
        st.error(f"❌ Error procesando el archivo: {e}")