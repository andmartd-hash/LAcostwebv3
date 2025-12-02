import streamlit as st
import urllib.parse # Necesario para convertir el texto a formato de enlace web

# --- 1. CONFIGURACIÓN Y LÓGICA (BACKEND) ---

def calcular_precio_servicio(costo, dias_pago, switch_riesgo, switch_financiero, target_gp):
    # Variables globales
    TASA_MENSUAL = 0.015
    PCT_RIESGO = 0.02
    
    sobrecostos = 0.0
    
    if switch_riesgo:
        sobrecostos += PCT_RIESGO
        
    if switch_financiero:
        meses = dias_pago / 30
        costo_financiero = meses * TASA_MENSUAL
        sobrecostos += costo_financiero

    costo_ajustado = costo * (1 + sobrecostos)
    divisor = 1 - target_gp
    
    if divisor <= 0: return 0
    return costo_ajustado / divisor

# --- 2. INTERFAZ DE USUARIO ---

st.set_page_config(page_title="LACOSTWEBV3 TLS", page_icon="🔵")

st.title("🔵 LACOSTWEBV3 TLS")
st.markdown("**Usuario:** Andresma | **Destino:** andresma@co.ibm.com")

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

# -- SECCIÓN B: CÁLCULO EN VIVO --
precio_calculado = calcular_precio_servicio(costo_base, dias_pago, riesgo, financiero, target_gp)

st.markdown("---")
st.metric(label="💰 Precio Final Sugerido", value=f"USD ${precio_calculado:,.2f}")

# -- SECCIÓN C: GENERAR CORREO --
st.markdown("### 📤 Acciones")

if not cliente:
    st.warning("⚠️ Ingresa el nombre del cliente para habilitar el envío.")
else:
    # 1. Preparamos el asunto y el cuerpo del correo
    destinatario = "andresma@co.ibm.com"
    asunto = f"Aprobación Cotización: {cliente}"
    
    cuerpo_mensaje = f"""
    Hola Andresma,
    
    Aquí están los detalles de la nueva cotización generada:
    
    --------------------------------------
    CLIENTE: {cliente}
    PRECIO VENTA: USD ${precio_calculado:,.2f}
    --------------------------------------
    
    Detalles Técnicos:
    - Costo Base: ${costo_base}
    - Plazo Pago: {dias_pago} días
    - Margen GP: {target_gp:.0%}
    - Riesgo: {'Sí' if riesgo else 'No'}
    - Financiero: {'Sí' if financiero else 'No'}
    
    Saludos,
    Tu Asistente Virtual
    """
    
    # 2. Codificamos el texto para que funcione en un enlace (URL Encode)
    asunto_codificado = urllib.parse.quote(asunto)
    cuerpo_codificado = urllib.parse.quote(cuerpo_mensaje)
    
    # 3. Creamos el enlace mágico "mailto"
    link_correo = f"mailto:{destinatario}?subject={asunto_codificado}&body={cuerpo_codificado}"
    
    # 4. Mostramos el botón
    st.success("✅ Cálculo listo.")
    st.markdown(f'''
        <a href="{link_correo}" target="_blank">
            <button style="
                background-color: #0F62FE; 
                color: white; 
                padding: 10px 24px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;">
                📧 Enviar a andresma@co.ibm.com
            </button>
        </a>
        ''', unsafe_allow_html=True)
    
    st.caption("Al hacer clic, se abrirá tu correo corporativo con el borrador listo.")