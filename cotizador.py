import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# ==========================================
# 0. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="LAcostWeb V3 Final", layout="wide", page_icon="🏢")

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
# 1. BASE DE DATOS (V3 COMPLETA)
# ==========================================

# 1.1 PAÍSES (V3 - countries.csv)
DB_COUNTRIES = pd.DataFrame([
    {"Country": "Argentina", "Currency": "ARS", "E/R": 1428.9486, "Tax": 0.0529},
    {"Country": "Brazil",    "Currency": "BRL", "E/R": 5.3410,    "Tax": 0.1425},
    {"Country": "Chile",     "Currency": "CLP", "E/R": 934.704,   "Tax": 0.0},
    {"Country": "Chile",     "Currency": "CLF", "E/R": 0.02358,   "Tax": 0.0},
    {"Country": "Colombia",  "Currency": "COP", "E/R": 3775.22,   "Tax": 0.01},
    {"Country": "Ecuador",   "Currency": "USD", "E/R": 1.0,       "Tax": 0.0},
    {"Country": "Peru",      "Currency": "PEN", "E/R": 3.3729,    "Tax": 0.0},
    {"Country": "Mexico",    "Currency": "MXN", "E/R": 18.4203,   "Tax": 0.0},
    {"Country": "Uruguay",   "Currency": "UYU", "E/R": 39.7318,   "Tax": 0.0},
    {"Country": "Venezuela", "Currency": "VES", "E/R": 235.28,    "Tax": 0.0155}
])

# 1.2 RIESGO (V3 - QA Risk.csv)
DB_RISK = pd.DataFrame([
    {"Risk": "Low", "Contingency": 0.02},
    {"Risk": "Medium", "Contingency": 0.05},
    {"Risk": "High", "Contingency": 0.08}
])

# 1.3 CATÁLOGO (V3 - Offering.csv - 23 Ítems)
DB_OFFERINGS = pd.DataFrame([
    {'Offering': 'IBM Hardware Resell for Server and Storage-Lenovo', 'L40': '6942-1BT', 'Conga': 'Location Based Services'},
    {'Offering': '1-HWMA MVS SPT other Prod', 'L40': '6942-0IC', 'Conga': 'Conga by CSV'},
    {'Offering': '2-HWMA MVS SPT other Prod', 'L40': '6942-0IC', 'Conga': 'Conga by CSV'},
    {'Offering': 'SWMA MVS SPT other Prod', 'L40': '6942-76O', 'Conga': 'Conga by CSV'},
    {'Offering': 'IBM Support for Red Hat', 'L40': '6948-B73', 'Conga': 'Conga by CSV'},
    {'Offering': 'IBM Support for Red Hat - Enterprise Linux Subscription', 'L40': '6942-42T', 'Conga': 'Location Based Services'},
    {'Offering': 'Subscription for Red Hat', 'L40': '6948-66J', 'Conga': 'Location Based Services'},
    {'Offering': 'Support for Red Hat', 'L40': '6949-66K', 'Conga': 'Location Based Services'},
    {'Offering': 'IBM Support for Oracle', 'L40': '6942-42E', 'Conga': 'Location Based Services'},
    {'Offering': 'IBM Customized Support for Multivendor Hardware Services', 'L40': '6942-76T', 'Conga': 'Location Based Services'},
    {'Offering': 'IBM Customized Support for Multivendor Software Services', 'L40': '6942-76U', 'Conga': 'Location Based Services'},
    {'Offering': 'IBM Customized Support for Hardware Services-Logo', 'L40': '6942-76V', 'Conga': 'Location Based Services'},
    {'Offering': 'IBM Customized Support for Software Services-Logo', 'L40': '6942-76W', 'Conga': 'Location Based Services'},
    {'Offering': 'HWMA MVS SPT other Loc', 'L40': '6942-0ID', 'Conga': 'Location Based Services'},
    {'Offering': 'SWMA MVS SPT other Loc', 'L40': '6942-0IG', 'Conga': 'Location Based Services'},
    {'Offering': 'Relocation Services - Packaging', 'L40': '6942-54E', 'Conga': 'Location Based Services'},
    {'Offering': 'Relocation Services - Movers Charge', 'L40': '6942-54F', 'Conga': 'Location Based Services'},
    {'Offering': 'Relocation Services - Travel and Living', 'L40': '6942-54R', 'Conga': 'Location Based Services'},
    {'Offering': "Relocation Services - External Vendor's Charge", 'L40': '6942-78O', 'Conga': 'Location Based Services'},
    {'Offering': 'IBM Hardware Resell for Networking and Security Alliances', 'L40': '6942-1GE', 'Conga': 'Location Based Services'},
    {'Offering': 'IBM Software Resell for Networking and Security Alliances', 'L40': '6942-1GF', 'Conga': 'Location Based Services'},
    {'Offering': 'System Technical Support Service-MVS-STSS', 'L40': '6942-1FN', 'Conga': 'Location Based Services'},
    {'Offering': 'System Technical Support Service-Logo-STSS', 'L40': '6942-1KJ', 'Conga': 'Location Based Services'}
])

# ==========================================
# 2. FUNCIONES
# ==========================================
def safe_float(val):
    try: return float(val)
    except: return 0.0

def calc_months(start, end):
    if not start or not end or start > end: return 0.0
    return round((end - start).days / 30.44, 1)

def get_country_info(c_name, currency):
    # Lógica: Traer E/R y Tax según País + Moneda
    try:
        if currency == "USD":
            row = DB_COUNTRIES[DB_COUNTRIES["Country"] == c_name].iloc[0]
            return 1.0, float(row["Tax"]) # Tasa 1.0 pero Tax del país
        
        row = DB_COUNTRIES[(DB_COUNTRIES["Country"] == c_name) & (DB_COUNTRIES["Currency"] == currency)]
        if not row.empty:
            return float(row["E/R"].iloc[0]), float(row["Tax"].iloc[0])
    except:
        pass
    return 1.0, 0.0

if 'lines' not in st.session_state:
    st.session_state.lines = []

def add_line():
    st.session_state.lines.append({
        "qty": 1, "unit_cost": 0.0, "gp_target": 40.0,
        "svc_start": date.today(),
        "svc_end": date.today().replace(year=date.today().year + 1)
    })

def remove_line(idx):
    st.session_state.lines.pop(idx)

# ==========================================
# 3. INTERFAZ (UI)
# ==========================================

# --- SIDEBAR ---
with st.sidebar: