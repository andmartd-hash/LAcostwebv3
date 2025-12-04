import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import math

# ==========================================
# 0. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="LAcostWeb V15", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .stNumberInput input, .stTextInput input { padding: 0px 5px; height: auto; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1rem; font-weight: 600; }
    h1 { color: #0F62FE; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS (Cargada desde tus Archivos V2)
# ==========================================

# 1.1 CONFIGURACIÓN DE LA UI (El Cerebro)
# Define qué campos se muestran y dónde.
DB_UI_CONFIG = pd.DataFrame([
    {"Sección": "Header", "Etiqueta": "Customer Name", "Tipo": "Texto", "Origen": None, "Key": "cust_name", "Mandatory": "Sí"},
    {"Sección": "Header", "Etiqueta": "Customer ID", "Tipo": "Texto", "Origen": None, "Key": "cust_id", "Mandatory": "No"},
    {"Sección": "Header", "Etiqueta": "Quote Date", "Tipo": "Fecha", "Origen": None, "Key": "quote_date", "Mandatory": "No"},
    {"Sección": "Header", "Etiqueta": "Contract Start", "Tipo": "Fecha", "Origen": None, "Key": "contract_start", "Mandatory": "Sí"},
    {"Sección": "Header", "Etiqueta": "Contract End", "Tipo": "Fecha", "Origen": None, "Key": "contract_end", "Mandatory": "Sí"},
    {"Sección": "Sidebar", "Etiqueta": "Country", "Tipo": "Lista", "Origen": "Sheet: countries", "Key": "country", "Mandatory": "Sí"},
    {"Sección": "Sidebar", "Etiqueta": "Risk Level", "Tipo": "Lista", "Origen": "Sheet: QA Risk", "Key": "risk", "Mandatory": "Sí"},
    {"Sección": "Sidebar", "Etiqueta": "Currency", "Tipo": "Lógica", "Origen": "Auto", "Key": "currency", "Mandatory": "Sí"},
    {"Sección": "Services", "Etiqueta": "Offering Name", "Tipo": "Lista", "Origen": "Sheet: Offering", "Key": "offering", "Mandatory": "Sí"},
    {"Sección": "Services", "Etiqueta": "Description", "Tipo": "Texto", "Origen": None, "Key": "desc", "Mandatory": "No"},
    {"Sección": "Services", "Etiqueta": "Service Start", "Tipo": "Fecha", "Origen": None, "Key": "svc_start", "Mandatory": "Sí"},
    {"Sección": "Services", "Etiqueta": "Service End", "Tipo": "Fecha", "Origen": None, "Key": "svc_end", "Mandatory": "Sí"},
    {"Sección": "Services", "Etiqueta": "Quantity", "Tipo": "Número", "Origen": None, "Key": "qty", "Mandatory": "Sí"},
    {"Sección": "Services", "Etiqueta": "Unit Cost", "Tipo": "Moneda", "Origen": None, "Key": "unit_cost", "Mandatory": "Sí"},
    {"Sección": "Services", "Etiqueta": "GP Target %", "Tipo": "Porcentaje", "Origen": None, "Key": "gp_target", "Mandatory": "Sí"}
])

# 1.2 DATOS DE PAÍSES (countries.csv)
DB_COUNTRIES = pd.DataFrame([
    {"countries": "Argentina", "E/R": 1428.95, "Currency": "ARS", "Taxes/deduc": 0.0529},
    {"countries": "Brazil",    "E/R": 5.34,    "Currency": "BRL", "Taxes/deduc": 0.1425},
    {"countries": "Chile",     "E/R": 934.70,  "Currency": "CLP", "Taxes/deduc": 0.0},
    {"countries": "Chile",     "E/R": 0.02358, "Currency": "CLF", "Taxes/deduc": 0.0},
    {"countries": "Colombia",  "E/R": 3775.22, "Currency": "COP", "Taxes/deduc": 0.01},
    {"countries": "Ecuador",   "E/R": 1.0,     "Currency": "USD", "Taxes/deduc": 0.0},
    {"countries": "Peru",      "E/R": 3.37,    "Currency": "PEN", "Taxes/deduc": 0.0},
    {"countries": "Mexico",    "E/R": 18.42,   "Currency": "MXN", "Taxes/deduc": 0.0},
    {"countries": "Uruguay",   "E/R": 39.73,   "Currency": "UYU", "Taxes/deduc": 0.0},
    {"countries": "Venezuela", "E/R": 235.28,  "Currency": "VES", "Taxes/deduc": 0.0155}
])

# 1.3 DATOS DE RIESGO (QA Risk.csv)
DB_RISK = pd.DataFrame([
    {"Risk": "Low", "Contingency": 0.02},
    {"Risk": "Medium", "Contingency": 0.05},
    {"Risk": "High", "Contingency": 0.08}
])

# 1.4 CATÁLOGO DE SERVICIOS (Offering.csv)
DB_OFFERINGS = pd.DataFrame([
    {"Offering": "IBM Hardware Resell for Server and Storage-Lenovo", "L40": "6942-1BT", "Load in conga": "Location Based Services"},
    {"Offering": "1-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Load in conga": "Conga by CSV"},
    {"Offering": "2-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Load in conga": "Conga by CSV"},
    {"Offering": "SWMA MVS SPT other Prod", "L40": "6942-76O", "Load in conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat", "L40": "6948-B73", "Load in conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat - Enterprise Linux Subscription", "L40": "6942-42T", "Load in conga": "Location Based Services"},
    {"Offering": "Subscription for Red Hat", "L40": "6948-66J", "Load in conga": "Location Based Services"},
    {"Offering": "Support for Red Hat", "L40": "6949-66K", "Load in conga": "Location Based Services"},
    {"Offering": "IBM Support for Oracle", "L40": "6942-42E", "Load in conga": "Location Based Services"},
    {"Offering": "IBM Customized Support for Multivendor Hardware Services", "L40": "6942-76T", "Load in conga": "Location Based Services"},
    {"Offering": "IBM Customized Support for Multivendor Software Services", "L40": "6942-76U", "Load in conga": "Location Based Services"},
    {"Offering": "IBM Customized Support for Hardware Services-Logo", "L40": "6942-76V", "Load in conga": "Location Based Services"},
    {"Offering": "IBM Customized Support for Software Services-Logo", "L40": "6942-76W", "Load in conga": "Location Based Services"},
    {"Offering": "HWMA MVS SPT other Loc", "L40": "6942-0ID", "Load in conga": "Location Based Services"},
    {"Offering": "SWMA MVS SPT other Loc", "L40": "6942-0IG", "Load in conga": "Location Based Services"},
    {"Offering": "Relocation Services - Packaging", "L40": "6942-54E", "Load in conga": "Location Based Services"},
    {"Offering": "Relocation Services - Movers Charge", "L40": "6942-54F", "Load in conga": "Location Based Services"},
    {"Offering": "Relocation Services - Travel and Living", "L40": "6942-54R", "Load in conga": "Location Based Services"},
    {"Offering": "Relocation Services - External Vendor's Charge", "L40": "6942-78O", "Load in conga": "Location Based Services"}
])

# ==========================================
# 2. FUNCIONES DE LÓGICA
# ==========================================

def calculate_months(start, end):
    if not start or not end or start > end: return 0.0
    return round((end - start).days / 30.44, 1)

def get_country_data(country, currency_code):
    # Si es USD, tasa es 1, pero buscamos tax del país
    if currency_code == "USD":
        row = DB_COUNTRIES[DB_COUNTRIES["countries"] == country].iloc[0]
        return 1.0, float(row["Taxes/deduc"])
    
    # Si es local, buscamos match exacto
    row = DB_COUNTRIES[(DB_COUNTRIES["countries"] == country) & (DB_COUNTRIES["Currency"] == currency_code)]
    if not row.empty:
        return float(row["E/R"].iloc[0]), float(row["Taxes/deduc"].iloc[0])
    return 1.0, 0.0

def get_list_options(source_str):
    """Parsea el campo 'Origen' del Excel para sacar la lista correcta."""
    if pd.isna(source_str): return []
    if "Sheet: countries" in source_str:
        return sorted(DB_COUNTRIES["countries"].unique())
    if "Sheet: QA Risk" in source_str:
        return DB_RISK["Risk"].tolist()
    if "Sheet: Offering" in source_str:
        return DB_OFFERINGS["Offering"].tolist()
    return []

if 'lines' not in st.session_state:
    st.session_state.lines = []

def add_line():
    # Estructura base para nueva línea
    new_line = {}
    # Valores por defecto inteligentes
    new_line["qty"] = 1
    new_line["unit_cost"] = 0.0
    new_line["gp_target"] = 40
    new_line["svc_start"] = date.today()
    new_line["svc_end"] = date.today().replace(year=date.today().year + 1)
    st.session_state.lines.append(new_line)

def remove_line(index):
    st.session_state.lines.pop(index)

# ==========================================
# 3. RENDERIZADOR DINÁMICO DE UI
# ==========================================
def render_dynamic_field(row, col_container, idx_suffix=None):
    """
    Crea el widget de Streamlit basado en la fila de configuración.
    idx_suffix: se usa para las líneas repetibles (servicios) para que las keys sean únicas (ej: qty_0).
    """
    label = row['Etiqueta']
    key = f"{row['Key']}_{idx_suffix}" if idx_suffix is not None else row['Key']
    tipo = row['Tipo']
    
    # Manejo de valores iniciales para líneas de servicio
    default_val = None
    if idx_suffix is not None:
        # Intentamos recuperar el valor guardado en session_state.lines
        line_data = st.session_state.lines[int(idx_suffix)]
        default_val = line_data.get(row['Key'])

    with col_container:
        if tipo == "Texto":
            val = st.text_input(label, value=default_val if default_val else "", key=key)
            
        elif tipo == "Fecha":
            val = st.date_input(label, value=default_val if default_val else date.today(), key=key)
            
        elif tipo == "Número":
            val = st.number_input(label, min_value=1, value=int(default_val) if default_val else 1, key=key)
            
        elif tipo == "Moneda":
            # Input de texto para moneda limpio
            val_str = st.text_input(label + " ($)", value=str(default_val) if default_val else "0.0", key=key)
            try: val = float(val_str)
            except: val = 0.0
            
        elif tipo == "Porcentaje":
            val_str = st.text_input(label, value=str(default_val) if default_val else "40", key=key)
            try: val = float(val_str)
            except: val = 0.0
            
        elif tipo == "Lista":
            options = get_list_options(row['Origen'])
            # Recuperar índice si existe valor previo
            idx = 0
            if default_val and default_val in options:
                idx = options.index(default_val)
            val = st.selectbox(label, options, index=idx, key=key)
            
        else:
            val = None

        # Guardar valor en session_state.lines si estamos en una línea
        if idx_suffix is not None and val is not None:
            st.session_state.lines[int(idx_suffix)][row['Key']] = val
            
        return val


# ==========================================
# 4. LAYOUT PRINCIPAL
# ==========================================

# --- SIDEBAR DINÁMICO ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
    st.markdown("## ⚙️ Config")
    
    # Filtrar campos de Sidebar
    sidebar_fields = DB_UI_CONFIG[DB_UI_CONFIG['Sección'] == 'Sidebar']
    
    config_values = {}
    
    for _, row in sidebar_fields.iterrows():
        # Lógica especial para Moneda (Depende del País seleccionado antes)
        if row['Key'] == 'currency':
            country_sel = config_values.get('country')
            if country_sel:
                avail_cur = DB_COUNTRIES[DB_COUNTRIES["countries"] == country_sel]["Currency"].unique().tolist()
                cur_opts = list(dict.fromkeys(["USD"] + avail_cur))
                config_values['currency'] = st.pills(row['Etiqueta'], cur_opts, default=cur_opts[0], key=row['Key'])
        else:
            config_values[row['Key']] = render_dynamic_field(row, st)

    # Cálculos Globales
    country = config_values.get('country')
    currency = config_values.get('currency')
    risk_level = config_values.get('risk')
    
    fx_rate, tax_rate = 1.0, 0.0
    risk_val = 0.0
    
    if country and currency:
        fx_rate, tax_rate = get_country_data(country, currency)
    
    if risk_level:
        risk_row = DB_RISK[DB_RISK["Risk"] == risk_level]
        if not risk_row.empty:
            risk_val = float(risk_row["Contingency"].iloc[0])

    st.markdown("---")
    if currency != "USD": st.metric("FX Rate", f"{fx_rate:,.2f}")
    st.metric("Risk Applied", f"{risk_val:.1%}")
    st.caption("LAcostWeb V15 | Dynamic Engine")

# --- HEADER DINÁMICO ---
st.title("LAcostWeb V15 🚀")

with st.container():
    st.subheader("📝 Header Info")
    header_fields = DB_UI_CONFIG[DB_UI_CONFIG['Sección'] == 'Header']
    
    # Organizar en columnas (ej. 4 por fila)
    cols = st.columns(4)
    for i, (_, row) in enumerate(header_fields.iterrows()):
        render_dynamic_field(row, cols[i % 4])

st.divider()

# --- SERVICIOS DINÁMICOS ---
st.subheader("📋 Services Line Items")

grand_total_price = 0.0
summary_lines = []
service_fields = DB_UI_CONFIG[DB_UI_CONFIG['Sección'] == 'Services']

for i, line in enumerate(st.session_state.lines):
    # Nombre del servicio para el título del expander
    current_offering = line.get('offering', 'New Service')
    
    with st.expander(f"🔹 {i+1}. {current_offering}", expanded=True):
        
        # 1. Renderizar campos de Offering arriba (Row 1)
        # Filtramos el campo 'offering' para ponerlo primero y ancho
        offering_field = service_fields[service_fields['Key'] == 'offering'].iloc[0]
        
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns([4, 1, 1, 0.5])
        
        # Input Offering
        render_dynamic_field(offering_field, r1_c1, idx_suffix=i)
        
        # L40 y Conga (Son Read-Only derivados, no están en Config UI para editar, los mostramos manual)
        off_data = DB_OFFERINGS[DB_OFFERINGS["Offering"] == line.get('offering', '')]
        l40_val = off_data["L40"].iloc[0] if not off_data.empty else ""
        conga_val = off_data["Load in conga"].iloc[0] if not off_data.empty else ""
        
        with r1_c2: st.text_input("L40", value=l40_val, disabled=True, key=f"l40_{i}")
        with r1_c3: st.text_input("Conga", value=conga_val, disabled=True, key=f"cng_{i}")
        with r1_c4:
            if st.button("🗑️", key=f"del_{i}"):
                remove_line(i)
                st.rerun()
        
        # 2. Renderizar el resto de campos (Row 2)
        # Excluimos 'offering' que ya pusimos
        other_fields = service_fields[service_fields['Key'] != 'offering']
        
        # Grid dinámico para el resto
        cols_row2 = st.columns(len(other_fields) + 2) # +2 para Duración y Total
        
        # Diccionario temporal para cálculos
        calc_vals = {}
        
        col_idx = 0
        for _, field in other_fields.iterrows():
            val = render_dynamic_field(field, cols_row2[col_idx], idx_suffix=i)
            calc_vals[field['Key']] = val
            col_idx += 1
            
            # Si acabamos de renderizar las fechas, inyectamos el campo Duración
            if field['Key'] == 'svc_end':
                dur = calculate_months(calc_vals.get('svc_start'), calc_vals.get('svc_end'))
                with cols_row2[col_idx]:
                    st.text_input("Mth", value=str(dur), disabled=True, key=f"dur_{i}")
                col_idx += 1
        
        # --- CÁLCULO DE LÍNEA ---
        # Recuperamos variables usando las keys definidas en Excel
        qty = float(calc_vals.get('qty', 1))
        unit_cost = float(calc_vals.get('unit_cost', 0))
        gp_target = float(calc_vals.get('gp_target', 40)) / 100.0
        # Recalcular duración por seguridad
        dur = calculate_months(calc_vals.get('svc_start'), calc_vals.get('svc_end'))
        
        # Fórmula Maestra
        total_cost = unit_cost * qty * dur * fx_rate
        divisor = 1 - gp_target
        base_price = (total_cost * (1 + risk_val)) / divisor if divisor > 0 else 0
        final_line_price = base_price * (1 + tax_rate)
        grand_total_price += final_line_price
        
        summary_lines.append({"Offering": current_offering, "Price": final_line_price})

        # Mostrar Total
        with cols_row2[col_idx]:
            st.markdown(f"""
            <div style="background-color: #e0eaff; padding: 6px; border-radius: 5px; text-align: center; border: 1px solid #0F62FE; margin-top: 1px;">
                <small style="color: #555; font-size: 0.7em;">TOTAL</small><br>
                <strong style="color: #0F62FE; font-size: 1.1em;">${final_line_price:,.0f}</strong>
            </div>
            """, unsafe_allow_html=True)

if st.button("➕ Add Line", type="secondary"):
    add_line()

st.divider()

# --- FOOTER ---
c_summ1, c_summ2 = st.columns([3, 1])
with c_summ1:
    if summary_lines: st.dataframe(pd.DataFrame(summary_lines), use_container_width=True)

with c_summ2:
    st.markdown(f"""
        <div style="text-align: right;">
            <h5 style="color: gray; margin:0;">TOTAL ESTIMATED</h5>
            <h1 style="color: #0F62FE; margin:0;">${grand_total_price:,.2f}</h1>
            <p style="font-weight: bold; margin:0;">{currency}</p>
        </div>
    """, unsafe_allow_html=True)
    
    cust_name_val = st.session_state.get('cust_name_None', '') # Hack: Header keys don't have suffix
    # En V15 los headers no tienen sufijo, buscamos la key directa
    # Como son dinámicos, Streamlit los guarda en top-level state
    # Buscamos keys que empiecen con 'cust_name'
    keys = [k for k in st.session_state.keys() if k.startswith('cust_name')]
    cust_name = st.session_state[keys[0]] if keys else "Client"

    if st.button("📧 Outlook Draft", type="primary", use_container_width=True):
        subject = f"LAcostWeb V15: {cust_name} - {currency} ${grand_total_price:,.2f}"
        body = f"Customer: {cust_name}\nTotal: {grand_total_price:,.2f}"
        link = f"mailto:andresma@co.ibm.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;url={link}">', unsafe_allow_html=True)