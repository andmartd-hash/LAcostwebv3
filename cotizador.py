import streamlit as st
import pandas as pd
import io

# --- 1. LÓGICA DE NEGOCIO (EL CORAZÓN DEL SISTEMA) ---
def calcular_costo_real(row):
    """
    Función fila por fila para aplicar reglas de negocio.
    """
    # 1. Extracción segura de datos (evita errores si falta el dato)
    costo = pd.to_numeric(row.get('Unit Cost', 0), errors='coerce') or 0.0
    moneda = str(row.get('Currency', '')).strip().upper()
    er = pd.to_numeric(row.get('ER', 1), errors='coerce') or 1.0
    
    # Manejo robusto de Unit Loc (puede venir como número 10 o texto "10")
    raw_loc = row.get('Unit Loc', '')
    # Convertimos a string, quitamos espacios y decimales extra (ej: "10.0" -> "10")
    unit_loc = str(raw_loc).split('.')[0].strip().upper()

    # 2. Regla de Excepción: Ecuador o Código 10
    es_ecuador = unit_loc in ["ECUADOR", "10"]

    # 3. Cálculo
    # SI es Dólares (US) Y NO es Ecuador/10 -> Dividimos por ER
    if moneda == 'US' and not es_ecuador:
        if er == 0: return 0.0 # Protección div/0
        return costo / er
    else:
        # Si es local o es Ecuador, el costo queda igual
        return costo

# --- 2. INTERFAZ WEB (STREAMLIT) ---
st.set_page_config(page_title="Cotizador V3 - IBM Style", layout="wide")

st.title("☁️ Cotizador Web: Procesamiento V3")
st.markdown("""
Esta aplicación procesa el archivo **V3-BASE** aplicando la regla de negocio:
- Si Moneda es **US** y Unit Loc **NO** es Ecuador/10: `Costo / ER`
- Caso contrario: `Costo`
""")

# --- 3. CARGA DE ARCHIVO ---
uploaded_file = st.file_uploader("Sube tu archivo Excel o CSV (V3-BASE)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Detectar si es Excel o CSV
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"Archivo cargado: {len(df)} filas detectadas.")

        # --- 4. PROCESAMIENTO ---
        if st.button("Ejecutar Cálculo de Costos"):
            with st.spinner('Procesando lógica de negocio...'):
                
                # Validar que existan las columnas necesarias
                cols_necesarias = ['Unit Cost', 'Currency', 'ER', 'Unit Loc']
                if not all(col in df.columns for col in cols_necesarias):
                    st.error(f"Error: Al archivo le faltan columnas. Se requiere: {cols_necesarias}")
                else:
                    # Aplicar la función a cada fila
                    df['Costo Final Calculado'] = df.apply(calcular_costo_real, axis=1)
                    
                    # Mostrar resultados (Vista previa)
                    st.subheader("Vista Previa de Resultados")
                    # Mostramos columnas clave para que valides visualmente
                    st.dataframe(df[['Unit Loc', 'Currency', 'Unit Cost', 'ER', 'Costo Final Calculado']].head(10))
                    
                    # --- 5. DESCARGA ---
                    # Convertir DF a CSV para descargar
                    csv_buffer = df.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="📥 Descargar Archivo Procesado (CSV)",
                        data=csv_buffer,
                        file_name="V3_Procesado_Final.csv",
                        mime="text/csv",
                    )

    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo: {e}")