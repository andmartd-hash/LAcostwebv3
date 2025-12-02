import streamlit as st
import time

# --- 1. CONFIGURACIÓN Y LÓGICA (BACKEND) ---

def calcular_precio_servicio(costo, dias_pago, switch_riesgo, switch_financiero, target_gp):
    # Variables globales (simulando la base de datos de config)
    TASA_MENSUAL = 0.015
    PCT_RIESGO = 0.02
    
    sobrecostos = 0.0
    
    # Lógica de Riesgo
    if switch_riesgo:
        sobrecostos += PCT_RIESGO
        
    # Lógica Financiera (AD)
    if switch_financiero:
        meses = dias_pago / 30
        costo_financiero = meses * TASA_MENSUAL
        sobrecostos += costo_financiero

    # Cálculo final
    costo_ajustado = costo * (1 + sobrecostos)
    divisor = 1 - target_gp
    
    if divisor <= 0: return 0
    return costo_ajustado / divisor

def simular_guardado_y_envio(cliente, precio, dias):
    """
    Simula que guarda en BD y manda el correo interno.
    """
    time.sleep(1) # Simula el tiempo de procesamiento
    # Aquí iría el código real de SQL y SMTP
    return True

# --- 2. INTERFAZ DE USUARIO (FRONTEND) ---

st.set_page_config(page_title="Cotizador Interno IBM", page_icon="📊")

st.title("📊 Cotizador de Servicios (Interno)")
st.markdown("Herramienta para cálculo rápido de márgenes y precios.")

# -- SECCIÓN A: INPUTS --
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        cliente = st.text_input("Cliente / Proyecto")
        costo_base = st.number_input("Costo Unitario Base ($)", value=100.0, step=10.0)
        dias_pago = st.slider("Días de Pago", 0, 120, 60, step=15)
    
    with col2:
        st.write("Configuración de Sobrecostos:")
        riesgo = st.checkbox("Aplicar Contingencia (2%)", value=True)
        financiero = st.checkbox("Aplicar Costo Financiero (1.5%/mes)", value=True)
        
        st.markdown("---")
        target_gp = st.slider("Target GP (%)", 0.0, 0.99, 0.64)

# -- SECCIÓN B: PRE-VISUALIZACIÓN --
precio_calculado = calcular_precio_servicio(costo_base, dias_pago, riesgo, financiero, target_gp)

st.info(f"💰 **Precio Calculado en vivo:** USD ${precio_calculado:,.2f}")

# -- SECCIÓN C: ACCIÓN FINAL --
st.markdown("---")
col_btn, col_info = st.columns([1, 3])

with col_btn:
    # Este es el botón que "Cierra" el trato
    procesar = st.button("💾 Guardar y Notificar", type="primary")

if procesar:
    if not cliente:
        st.error("⚠️ Por favor ingresa el nombre del cliente.")
    else:
        with st.spinner("Conectando con base de datos interna..."):
            resultado = simular_guardado_y_envio(cliente, precio_calculado, dias_pago)
            
        st.success("✅ ¡Proceso Exitoso!")
        
        # Feedback visual de lo que "ocurrió" por detrás
        st.json({
            "Estado": "Guardado en DB",
            "Notificación": "Enviada a managers@ibm.com",
            "Detalle": f"Cliente: {cliente} | Precio Final: ${precio_calculado:,.2f}"
        })