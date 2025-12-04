import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cotizador V3 - IBM", layout="wide")
st.title("Cotizador Web V3")
st.write("Carga tu archivo V3-BASE (Excel o CSV) para procesar los costos.")

# --- LÓGICA DE NEGOCIO (Aquí está el ajuste del Unit Loc 10) ---
def calcular_costo_real(row):
    # 1. Obtenemos datos de la fila con seguridad
    costo = pd.to_numeric(row.get('Unit Cost', 0), errors='coerce') or 0.0
    moneda = str(row.get('Currency', '')).strip().upper()
    er = pd.to_numeric(row.get('ER', 1), errors='coerce') or 1.0
    
    # 2. Limpieza del Unit Loc (Maneja "10", 10, "10.0" o "Ecuador")
    raw_loc = str(row.get('Unit Loc', '')).strip()
    if raw_loc.endswith('.0'): 
        raw_loc = raw_loc[:-2] # Convierte "10.0" en "10"
    
    unit_loc = raw_loc.upper()

    # 3. REGLA DE EXCEPCIÓN:
    # Si la ubicación es '10' o 'ECUADOR', NO dividimos (aunque sea US).
    es_excepcion = unit_loc in ["10", "ECUADOR"]

    # 4. Cálculo Final
    if moneda == 'US' and not es_excepcion:
        if er == 0: return costo # Evitar división por cero
        return costo / er
    else:
        return costo

# --- INTERFAZ DE CARGA ---
uploaded_file = st.file_uploader("Subir archivo V3-BASE", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Cargar según formato
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"Archivo cargado: {len(df)} filas.")

        if st.button("Calcular Costos"):
            # Validamos que estén las columnas
            required_cols = ['Unit Cost', 'Currency', 'ER', 'Unit Loc']
            if all(col in df.columns for col in required_cols):
                
                # APLICAMOS LA FÓRMULA FILA POR FILA
                df['Calculated Cost'] = df.apply(calcular_costo_real, axis=1)
                
                # Muestra resultados
                st.dataframe(df.head())
                
                # Botón de descarga
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Descargar CSV Procesado",
                    csv,
                    "V3_Procesado.csv",
                    "text/csv"
                )
            else:
                st.error(f"Faltan columnas en el archivo. Se requiere: {required_cols}")

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")