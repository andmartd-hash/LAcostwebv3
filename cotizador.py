import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# ==========================================
# 1. BASE DE DATOS (Incrustada para facilidad)
# ==========================================

# TABLA PAÍSES (Extraída de tu hoja "countries")
DB_COUNTRIES = pd.DataFrame({
    "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Ecuador", "Peru", "Mexico", "Uruguay", "Venezuela"],
    "Currency_Code": ["ARS", "BRL", "CLP", "COP", "USD", "PEN", "MXN", "UYU", "VES"],
    "Exchange_Rate": [1428.95, 5.34, 934.70, 3775.22, 1.0, 3.37, 18.42, 39.73, 235.28]
})

# TABLA RIESGOS (Extraída de tu hoja "QA Risk")
DB_RISK = pd.DataFrame({
    "Risk_Level": ["Low", "Medium", "High"],
    "Contingency": [0.02, 0.05, 0.08]
})

# TABLA OFERTAS (Muestra simplificada de tu hoja "Offering")
# He puesto algunos ejemplos, el sistema buscará aquí.
DB_OFFERINGS = pd.DataFrame([
    {"Offering": "IBM Hardware Resell for Server and Storage-Lenovo", "L40": "6942-1BT", "Conga": "Location Based Services"},
    {"Offering": "1-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Conga": "Conga by CSV"},
    {"Offering": "SWMA MVS SPT other Prod", "L40": "6942-76O", "Conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat", "L40": "6948-B73", "Conga": "Conga by CSV"},
    {"Offering": "Support for Red Hat", "L40": "6949-66K", "Conga": "Location Based Services"}
])

# ==========================================
# 2. LÓGICA DE NEGOCIO (El Cerebro)
# ==========================================

def calcular_duracion_meses(start_date, end_date):
    """Calcula la duración en meses entre dos fechas."""
    if start_date > end_date:
        return 0
    # Cálculo aproximado de meses
    delta = end_date - start_date
    return round(delta.days / 30.44, 1) # Promedio días mes

def obtener_tasa_cambio(pais, moneda_seleccionada):
    """Busca la TRM correcta según el país y moneda."""
    if moneda_seleccionada == "USD":
        return 1.0
    
    # Caso especial Ecuador (Siempre es USD aunque digan Local)
    if pais == "Ecuador":
        return 1.0
        
    # Buscar en la BD
    dato = DB_COUNTRIES[DB_COUNTRIES["Country"] == pais]
    if not dato.empty:
        return float(dato["Exchange_Rate"].iloc[0])
    return 1.0

# ==========================================
# 3. INTERFAZ DE USUARIO (Streamlit)
# ==========================================

st.set_page_config(page_title="Cotizador V2 - IBM", layout="wide", page_icon="🌎")

st.title("🌎 Cotizador Internacional de Servicios V2")
st.markdown("**Usuario:** Andresma | **Versión:** 2.0 (Full Data)")

# --- SECCIÓN 1: DATOS DEL CLIENTE Y REGIÓN ---
st.subheader("1. Configuración General")
col1, col2, col3, col4 = st.columns(4)

with col1:
    cliente_nombre = st.text_input("Nombre del Cliente")
    cliente_numero = st.text_input("Número de Cliente (ID)")

with col2:
    # Dropdown de Países
    pais_sel = st.selectbox("País", DB_COUNTRIES["Country"])
    
with col3:
    # Dropdown de Moneda
    moneda_sel = st.radio("Moneda de Cotización", ["USD", "Local"], horizontal=True)

with col4:
    # Tasa de Cambio Automática
    tasa_cambio = obtener_tasa_cambio(pais_sel, moneda_sel)
    st.metric("Tasa de Cambio (E/R)", f"{tasa_cambio:,.2f}")
    if moneda_sel == "Local" and pais_sel != "Ecuador":
        st.caption(f"Calculando en moneda local de {pais_sel}")

st.markdown("---")

# --- SECCIÓN 2: DETALLE DEL SERVICIO (OFFERING) ---
st.subheader("2. Definición del Servicio")

c_off1, c_off2, c_off3 = st.columns([2, 1, 1])

with c_off1:
    # Dropdown inteligente de Ofertas
    oferta_nombre = st.selectbox("Seleccionar Offering (Servicio)", DB_OFFERINGS["Offering"])
    
    # Buscamos los datos automáticos (L40 y Conga)
    info_oferta = DB_OFFERINGS[DB_OFFERINGS["Offering"] == oferta_nombre].iloc[0]
    
with c_off2:
    st.text_input("L40 Code", value=info_oferta["L40"], disabled=True)
    
with c_off3:
    st.text_input("Load in Conga", value=info_oferta["Conga"], disabled=True)

desc_servicio = st.text_area("Descripción Adicional del Servicio", height=68)

st.markdown("---")

# --- SECCIÓN 3: TIEMPOS Y COSTOS ---
st.subheader("3. Cálculo Económico")

# Fila de Fechas
f1, f2, f3, f4 = st.columns(4)
with f1:
    fecha_inicio = st.date_input("Inicio del Servicio", value=date.today())
with f2:
    fecha_fin = st.date_input("Fin del Servicio", value=date.today().replace(year=date.today().year + 1))
with f3:
    # Cálculo automático de duración
    duracion = calcular_duracion_meses(fecha_inicio, fecha_fin)
    st.number_input("Duración (Meses)", value=duracion, disabled=True)
with f4:
    cantidad = st.number_input("Cantidad (QTY)", min_value=1, value=1)

# Fila de Precios
p1, p2, p3, p4 = st.columns(4)

with p1:
    costo_unitario = st.number_input("Costo Unitario (Base USD)", value=100.0)

with p2:
    # Selección de Riesgo
    riesgo_nivel = st.selectbox("Nivel de Riesgo (QA Risk)", DB_RISK["Risk_Level"])
    # Buscamos el % de contingencia
    riesgo_pct = float(DB_RISK[DB_RISK["Risk_Level"] == riesgo_nivel]["Contingency"].iloc[0])
    st.caption(f"Contingencia aplicada: {riesgo_pct:.0%}")

with p3:
    gp_target = st.slider("GP Target (Margen %)", 0.0, 0.99, 0.20)

with p4:
    # --- FORMULAS MAESTRAS (Input CSV Logic) ---
    
    # 1. Total Cost: Unit * Qty * Duration (* ER si es Local)
    # Nota: Asumimos que el Costo Unitario ingresado SIEMPRE es USD base.
    costo_total_base = costo_unitario * cantidad * duracion
    costo_total_final = costo_total_base * tasa_cambio
    
    # 2. Price: Total Cost * (1 + Risk) / (1 - GP)
    divisor = 1 - gp_target
    precio_venta = 0
    if divisor > 0:
        precio_venta = (costo_total_final * (1 + riesgo_pct)) / divisor
        
    st.metric("PRECIO DE VENTA FINAL", f"${precio_venta:,.2f}")
    if moneda_sel == "Local":
        st.caption("Valor en Moneda Local")
    else:
        st.caption("Valor en USD")

# --- SECCIÓN 4: ACCIÓN FINAL ---
st.markdown("---")

if st.button("📧 Generar Correo de Aprobación", type="primary"):
    if not cliente_nombre:
        st.error("Falta el nombre del cliente")
    else:
        # Preparar mail
        asunto = f"Cotización V2: {cliente_nombre} - {oferta_nombre[:30]}..."
        cuerpo = f"""
        Hola Andresma,
        
        Resumen de Cotización (V2 Estructura Base):
        -------------------------------------------
        Cliente: {cliente_nombre} (ID: {cliente_numero})
        País: {pais_sel}
        Oferta: {oferta_nombre}
        L40: {info_oferta['L40']}
        
        Económicos:
        -----------
        Moneda: {moneda_sel} (Tasa: {tasa_cambio})
        Costo Unitario Base: ${costo_unitario}
        Duración: {duracion} meses
        Riesgo QA: {riesgo_nivel} ({riesgo_pct:.0%})
        GP Target: {gp_target:.0%}
        
        TOTAL PRECIO VENTA: ${precio_venta:,.2f}
        -------------------------------------------
        """
        
        link = f"mailto:andresma@co.ibm.com?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
        
        st.markdown(f'<a href="{link}" target="_blank"><button style="background-color:#0F62FE;color:white;padding:10px;border-radius:5px;border:none;font-weight:bold;">Abrir en Outlook ↗</button></a>', unsafe_allow_html=True)
        st.success("Enlace generado. Haz clic arriba para enviar.")