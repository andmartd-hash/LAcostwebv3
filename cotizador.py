import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# ==========================================
# 0. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="LAcostWeb V18", layout="wide", page_icon="🛡️")

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
# 1. BASE DE DATOS (Hardcoded para estabilidad)
# ==========================================

# 1.1 CONFIGURACIÓN UI (Estructura de la Pantalla)
DB_UI_CONFIG = pd.DataFrame([
    # HEADER
    {"Sección": "Header", "Etiqueta": "ID_Cotizacion", "Tipo": "Texto", "Origen": None, "Key": "id_cot"},
    {"Sección": "Header", "Etiqueta": "Customer Name", "Tipo": "Texto", "Origen": None, "Key": "cust_name"},
    {"Sección": "Header", "Etiqueta": "Customer Number", "Tipo": "Texto", "Origen": None, "Key": "cust_num"},
    {"Sección": "Header", "Etiqueta": "Quote Date", "Tipo": "Fecha", "Origen": None, "Key": "quote_date"},
    {"Sección": "Header", "Etiqueta": "Contract Start", "Tipo": "Fecha", "Origen": None, "Key": "contract_start"},
    {"Sección": "Header", "Etiqueta": "Contract End", "Tipo": "Fecha", "Origen": None, "Key": "contract_end"},
    
    # SIDEBAR
    {"Sección": "Sidebar", "Etiqueta": "Countries", "Tipo": "Lista", "Origen": "Sheet: countries", "Key": "country"},
    {"Sección": "Sidebar", "Etiqueta": "QA Risk", "Tipo": "Lista", "Origen": "Sheet: QA Risk", "Key": "risk"},
    {"Sección": "Sidebar", "Etiqueta": "Currency", "Tipo": "Lógica", "Origen": "Auto", "Key": "currency"},
    
    # SERVICES
    {"Sección": "Services", "Etiqueta": "Offering", "Tipo": "Lista", "Origen": "Sheet: Offering", "Key": "offering"},
    {"Sección": "Services", "Etiqueta": "Description", "Tipo": "Texto", "Origen": None, "Key": "desc"},
    {"Sección": "Services", "Etiqueta": "Service Start", "Tipo": "Fecha", "Origen": None, "Key": "svc_start"},
    {"Sección": "Services", "Etiqueta": "Service End", "Tipo": "Fecha", "Origen": None, "Key": "svc_end"},
    {"Sección": "Services", "Etiqueta": "QTY", "Tipo": "Número", "Origen": None, "Key": "qty"},
    {"Sección": "Services", "Etiqueta": "Unit Cost USD", "Tipo": "Moneda", "Origen": None, "Key": "unit_cost"},
    {"Sección": "Services", "Etiqueta": "GP Target", "Tipo": "Porcentaje", "Origen": None, "Key": "gp_target"}
])

# 1.2 PAÍSES
DB_COUNTRIES = pd.DataFrame([
    {"countries": "Argentina", "E/R": 1428.9486, "Currency": "ARS", "Taxes/deduc": 0.0529},
    {"countries": "Brazil",    "E/R": 5.3410,    "Currency": "BRL", "Taxes/deduc": 0.1425},
    {"countries": "Chile",     "E/R": 934.704,   "Currency": "CLP", "Taxes/deduc": 0.0},
    {"countries": "Chile",     "E/R": 0.02358,   "Currency": "CLF", "Taxes/deduc": 0.0},
    {"countries": "Colombia",  "E/R": 3775.22,   "Currency": "COP", "Taxes/deduc": 0.01},
    {"countries": "Ecuador",   "E/R": 1.0,       "Currency": "USD", "Taxes/deduc": 0.0},
    {"countries": "Peru",      "E/R": 3.3729,    "Currency": "PEN", "Taxes/deduc": 0.0},
    {"countries": "Mexico",    "E/R": 18.4203,   "Currency": "MXN", "Taxes/deduc": 0.0},
    {"countries": "Uruguay",   "E/R": 39.7318,   "Currency": "UYU", "Taxes/deduc": 0.0},
    {"countries": "Venezuela", "E/R": 235.28,    "Currency": "VES", "Taxes/deduc": 0.0155}
])

# 1.3 RIESGO
DB_RISK = pd.DataFrame([
    {"Risk": "Low", "Contingency": 0.02},
    {"Risk": "Medium", "Contingency": 0.05},
    {"Risk": "High", "Contingency": 0.08}
])

# 1.4 OFFERINGS (Catálogo Completo V3)
DB_OFFERINGS = pd.DataFrame([
    {'Offering': 'IBM Hardware Resell for Server and Storage-Lenovo', 'L40': '6942-1BT', 'Load in conga': 'Location Based Services'},
    {'Offering': '1-HWMA MVS SPT other Prod', 'L40': '6942-0IC', 'Load in conga': 'Conga by CSV'},
    {'Offering': '2-HWMA MVS SPT other Prod', 'L40': '6942-0IC', 'Load in conga': 'Conga by CSV'},
    {'Offering': 'SWMA MVS SPT other Prod', 'L40': '6942-76O', 'Load in conga': 'Conga by CSV'},
    {'Offering': 'IBM Support for Red Hat', 'L40': '6948-B73', 'Load in conga': 'Conga by CSV'},
    {'Offering': 'IBM Support for Red Hat - Enterprise Linux Subscription', 'L40': '6942-42T', 'Load in conga': 'Location Based Services'},
    {'Offering': 'Subscription for Red Hat', 'L40': '6948-66J', 'Load in conga': 'Location Based Services'},
    {'Offering': 'Support for Red Hat', 'L40': '6949-66K', 'Load in conga': 'Location Based Services'},
    {'Offering': 'IBM Support for Oracle', 'L40': '6942-42E', 'Load in conga': 'Location Based Services'},
    {'Offering': 'IBM Customized Support for Multivendor Hardware Services', 'L40': '6942-76T', 'Load in conga': 'Location Based Services'},
    {'Offering': 'IBM Customized Support for Multivendor Software Services', 'L40': '6942-76U', 'Load in conga': 'Location Based Services'},
    {'Offering': 'IBM Customized Support for Hardware Services-Logo', 'L40': '6942-76V', 'Load in conga': 'Location Based Services'},
    {'Offering': 'IBM Customized Support for Software Services-Logo', 'L40': '6942-76W', 'Load in conga': 'Location Based Services'},
    {'Offering': 'HWMA MVS SPT other Loc', 'L40': '6942-0ID', 'Load in conga': 'Location Based Services'},
    {'Offering': 'SWMA MVS SPT other Loc', 'L40': '6942-0IG', 'Load in conga': 'Location Based Services'},
    {'Offering': 'Relocation Services - Packaging', 'L40': '6942-54E', 'Load in conga': 'Location Based Services'},
    {'Offering': 'Relocation Services - Movers Charge', 'L40': '6942-54F', 'Load in conga': 'Location Based Services'},
    {'Offering': 'Relocation Services - Travel and Living', 'L40': '6942-54R', 'Load in conga': 'Location Based Services'},
    {'Offering': "Relocation Services - External Vendor's Charge", 'L40': '6942-78O', 'Load in conga': 'Location Based Services'},
    {'Offering': 'IBM Hardware Resell for Networking and Security Alliances', 'L40': '6942-1GE', 'Load in conga': 'Location Based Services'},
    {'Offering': 'IBM Software Resell for Networking and Security Alliances', 'L40': '6942-1GF', 'Load in conga': 'Location Based Services'},
    {'Offering': 'System Technical Support Service-MVS-STSS', 'L40': '6942-1FN', 'Load in conga': 'Location Based Services'},
    {'Offering': 'System Technical Support Service-Logo-STSS', 'L40': '6942-1KJ', 'Load in conga': 'Location Based Services'}
])

# ==========================================
# 2. FUNCIONES SEGURAS
# ==========================================
def safe_float(value, default=0.0):
    try: return float(value)
    except: return default

def calculate_months(start, end):
    if not start or not end or start > end: return 0.0
    return round((end - start).days / 30.44, 1)

def get_country_data(country, currency_code):
    try:
        # USD Base
        if currency_code == "USD":
            row = DB_COUNTRIES[DB_COUNTRIES["countries"] == country].iloc[0]
            return 1.0, safe_float(row["Taxes/deduc"])
        # Local
        row = DB_COUNTRIES[(DB_COUNTRIES["countries"] == country) & (DB_COUNTRIES["Currency"] == currency_code)]
        if not row.empty:
            return safe_float(row["E/R"].iloc[0]), safe_float(row["Taxes/deduc"].iloc[0])
    except:
        pass
    return 1.0, 0.0

def get_list_options(source_str):
    if pd.isna(source_str): return []
    if "Sheet: countries" in source_str: return sorted(DB_COUNTRIES["countries"].unique())
    if "Sheet: QA Risk" in source_str: return DB_RISK["Risk"].tolist()
    if "Sheet: Offering" in source_str: return DB_OFFERINGS["Offering"].tolist()
    return []

if 'lines' not in st.session_state:
    st.session_state.lines = []

def add_line():
    st.session_state.lines.append({
        "qty": 1, "unit_cost": 0.0, "gp_target": 40.0,
        "svc_start": date.today(),
        "svc_end": date.today().replace(year=date.today().year + 1)
    })

def remove_line(index):
    st.session_state.lines.pop(index)

# ==========================================
# 3. RENDERIZADOR UI
# ==========================================
def render_dynamic_field(row, col_container, idx_suffix=None):
    label = row['Etiqueta']
    key = f"{row['Key']}_{idx_suffix}" if idx_suffix is not None else row['Key']
    
    # Recuperar valor previo
    default_val = None
    if idx_suffix is not None:
        default_val = st.session_state.lines[int(idx_suffix)].get(row['Key'])

    val = None
    with col_container:
        if row['Tipo'] == "Texto":
            val = st.text_input(label, value=str(default_val) if default_val else "", key=key)
        elif row['Tipo'] == "Fecha":
            val = st.date_input(label, value=default_val if default_val else date.today(), key=key)
        elif row['Tipo'] == "Número":
            val = st.number_input(label, min_value=1, value=int(default_val) if default_val else 1, key=key)
        elif row['Tipo'] == "Moneda":
            val_str = st.text_input(label + " ($)", value=str(default_val) if default_val else "0.0", key=key)
            val = safe_float(val_str)
        elif row['Tipo'] == "Porcentaje":
            val_str = st.text_input(label + " %", value=str(default_val) if default_val else "40", key=key)
            val = safe_float(val_str)
        elif row['Tipo'] == "Lista":
            options = get_list_options(row['Origen'])
            idx = 0
            if default_val and default_val in options: idx = options.index(default_val)
            val = st.selectbox(label, options, index=idx, key=key)

        # Actualizar estado si es una línea
        if idx_suffix is not None and val is not None:
            st.session_state.lines[int(idx_suffix)][row['Key']] = val
            
    return val

# ==========================================
# 4. APP PRINCIPAL
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
    st.markdown("## ⚙️ Config")
    
    sidebar_fields = DB_UI_CONFIG[DB_UI_CONFIG['Sección'] == 'Sidebar']
    config = {}
    
    for _, row in sidebar_fields.iterrows():
        if row['Key'] == 'currency':
            c_sel = config.get('country')
            if c_sel:
                cur_opts = ["USD"] + DB_COUNTRIES[DB_COUNTRIES["countries"] == c_sel]["Currency"].unique().tolist()
                # Usamos st.radio horizontal en lugar de st.pills para compatibilidad
                config['currency'] = st.radio(row['Etiqueta'], list(set(cur_opts)), index=0, horizontal=True, key=row['Key'])
        else:
            config[row['Key']] = render_dynamic_field(row, st)

    # Cálculos
    fx_rate, tax_rate = get_country_data(config.get('country'), config.get('currency'))
    
    risk_val = 0.0
    risk_row = DB_RISK[DB_RISK["Risk"] == config.get('risk')]
    if not risk_row.empty: risk_val = float(risk_row["Contingency"].iloc[0])

    st.markdown("---")
    if config.get('currency') != "USD": st.metric("FX Rate", f"{fx_rate:,.2f}")
    st.metric("Risk", f"{risk_val:.1%}")
    st.caption("LAcostWeb V18 | Stable")

# --- HEADER ---
st.title("LAcostWeb V18 🚀")
with st.container():
    st.subheader("📝 Header Info")
    header_fields = DB_UI_CONFIG[DB_UI_CONFIG['Sección'] == 'Header']
    cols = st.columns(3)
    for i, (_, row) in enumerate(header_fields.iterrows()):
        render_dynamic_field(row, cols[i % 3])

st.divider()

# --- SERVICES ---
st.subheader("📋 Services")

grand_total = 0.0
summary = []
svc_fields = DB_UI_CONFIG[DB_UI_CONFIG['Sección'] == 'Services']

for i, line in enumerate(st.session_state.lines):
    offering = line.get('offering', 'New Service')
    
    with st.expander(f"🔹 {i+1}. {offering}", expanded=True):
        
        # ROW 1: Offering + Auto Fields + Delete
        r1 = st.columns([3, 1, 1, 0.5])
        
        # Offering Field
        off_field = svc_fields[svc_fields['Key'] == 'offering'].iloc[0]
        render_dynamic_field(off_field, r1[0], idx_suffix=i)
        
        # Auto Fields
        off_data = DB_OFFERINGS[DB_OFFERINGS["Offering"] == offering]
        l40 = off_data["L40"].iloc[0] if not off_data.empty else ""
        conga = off_data["Load in conga"].iloc[0] if not off_data.empty else ""
        
        with r1[1]: st.text_input("L40", value=l40, disabled=True, key=f"l40_{i}")
        with r1[2]: st.text_input("Conga", value=conga, disabled=True, key=f"cng_{i}")
        with r1[3]:
            if st.button("🗑️", key=f"del_{i}"):
                remove_line(i)
                st.rerun()
        
        # ROW 2: Rest of Fields
        others = svc_fields[svc_fields['Key'] != 'offering']
        r2 = st.columns(len(others) + 2) # +2 for Duration and Total
        
        vals = {}
        for idx, (_, f) in enumerate(others.iterrows()):
            vals[f['Key']] = render_dynamic_field(f, r2[idx], idx_suffix=i)
        
        # Logic: Duration
        dur = calculate_months(vals.get('svc_start'), vals.get('svc_end'))
        with r2[len(others)]:
            st.text_input("Mth", value=str(dur), disabled=True, key=f"dur_{i}")
        
        # Logic: Visual Local Cost Calculation
        unit_cost_usd = safe_float(vals.get('unit_cost', 0))
        if config.get('currency') != "USD":
            local_cost_est = unit_cost_usd * fx_rate
            # Mostramos el cálculo sugerido, no se guarda como input
            st.caption(f"Local ~ {local_cost_est:,.2f}")

        # Logic: Total Price
        qty = safe_float(vals.get('qty', 1))
        gp = safe_float(vals.get('gp_target', 40)) / 100.0
        
        total_cost = unit_cost_usd * qty * dur * fx_rate
        divisor = 1 - gp
        base = (total_cost * (1 + risk_val)) / divisor if divisor > 0 else 0
        final = base * (1 + tax_rate)
        grand_total += final
        
        summary.append({"Service": offering, "Price": final})

        with r2[len(others)+1]:
             st.markdown(f"""<div style="background-color:#e0eaff;padding:5px;border-radius:5px;text-align:center;border:1px solid #0F62FE;">
                <small>TOTAL</small><br><strong>${final:,.0f}</strong></div>""", unsafe_allow_html=True)

if st.button("➕ Add Line"):
    add_line()

st.divider()

# --- FOOTER ---
c1, c2 = st.columns([3, 1])
if summary: c1.dataframe(pd.DataFrame(summary), use_container_width=True)

with c2:
    cur_label = config.get('currency', 'USD')
    st.markdown(f"""<div style="text-align:right"><h5 style="margin:0;color:gray">TOTAL</h5><h1 style="margin:0;color:#0F62FE">${grand_total:,.2f}</h1><p>{cur_label}</p></div>""", unsafe_allow_html=True)
    
    # Email Button (Robust Key Access)
    id_cot = st.session_state.get('id_cot', 'N/A')
    cust_name = st.session_state.get('cust_name', 'Client')
    
    if st.button("📧 Outlook Draft", type="primary"):
        subject = f"Quote {id_cot}: {cust_name} - {cur_label} ${grand_total:,.2f}"
        body = f"ID: {id_cot}\nCustomer: {cust_name}\nTotal: {grand_total:,.2f}"
        link = f"mailto:andresma@co.ibm.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;url={link}">', unsafe_allow_html=True)