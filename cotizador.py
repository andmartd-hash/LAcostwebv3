import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# ==========================================
# 0. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="LAcostWeb V22", layout="wide", page_icon="🏢")

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

# 1.1 PAÍSES (V3)
DB_COUNTRIES = pd.DataFrame([
    {"Country": "Argentina", "Currency_Code": "ARS", "Exchange_Rate": 1428.9486, "Tax_Rate": 0.0529},
    {"Country": "Brazil",    "Currency_Code": "BRL", "Exchange_Rate": 5.3410,    "Tax_Rate": 0.1425},
    {"Country": "Chile",     "Currency_Code": "CLP", "Exchange_Rate": 934.704,   "Tax_Rate": 0.0},
    {"Country": "Chile",     "Currency_Code": "CLF", "Exchange_Rate": 0.02358,   "Tax_Rate": 0.0},
    {"Country": "Colombia",  "Currency_Code": "COP", "Exchange_Rate": 3775.22,   "Tax_Rate": 0.01},
    {"Country": "Ecuador",   "Currency_Code": "USD", "Exchange_Rate": 1.0,       "Tax_Rate": 0.0},
    {"Country": "Peru",      "Currency_Code": "PEN", "Exchange_Rate": 3.3729,    "Tax_Rate": 0.0},
    {"Country": "Mexico",    "Currency_Code": "MXN", "Exchange_Rate": 18.4203,   "Tax_Rate": 0.0},
    {"Country": "Uruguay",   "Currency_Code": "UYU", "Exchange_Rate": 39.7318,   "Tax_Rate": 0.0},
    {"Country": "Venezuela", "Currency_Code": "VES", "Exchange_Rate": 235.28,    "Tax_Rate": 0.0155}
])

# 1.2 RIESGO (V3)
DB_RISK = pd.DataFrame({
    "Risk_Level": ["Low", "Medium", "High"],
    "Contingency": [0.02, 0.05, 0.08]
})

# 1.3 CATÁLOGO DE SERVICIOS (23 Ítems - V3 Completo)
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
# 2. FUNCIONES LÓGICAS (Seguras)
# ==========================================
def calculate_months(start, end):
    if start > end: return 0.0
    return round((end - start).days / 30.44, 1)

def get_country_data(country, currency_code):
    try:
        if currency_code == "USD":
            row = DB_COUNTRIES[DB_COUNTRIES["Country"] == country].iloc[0]
            return 1.0, float(row["Tax_Rate"])
        
        row = DB_COUNTRIES[(DB_COUNTRIES["Country"] == country) & (DB_COUNTRIES["Currency_Code"] == currency_code)]
        if not row.empty:
            return float(row["Exchange_Rate"].iloc[0]), float(row["Tax_Rate"].iloc[0])
    except:
        pass
    return 1.0, 0.0

# Función segura para convertir texto a número
def safe_float(val_str):
    try:
        return float(val_str)
    except:
        return 0.0

if 'lines' not in st.session_state:
    st.session_state.lines = []

def add_line():
    st.session_state.lines.append({
        "offering_idx": 0, "qty": 1, "start_date": date.today(),
        "end_date": date.today().replace(year=date.today().year + 1),
        "unit_cost": 0.0, "gp_percent": 40 
    })

def remove_line(index):
    st.session_state.lines.pop(index)

# ==========================================
# 3. INTERFAZ (V14 con Ajustes V3)
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
    st.markdown("## ⚙️ Config V3")
    
    country_sel = st.selectbox("Country", sorted(DB_COUNTRIES["Country"].unique()))
    
    avail_cur = DB_COUNTRIES[DB_COUNTRIES["Country"] == country_sel]["Currency_Code"].unique().tolist()
    cur_opts = list(dict.fromkeys(["USD"] + avail_cur))
    currency_sel = st.radio("Currency", cur_opts, index=0, horizontal=True)
    
    risk_sel = st.selectbox("Risk Level", DB_RISK["Risk_Level"])
    risk_val = float(DB_RISK[DB_RISK["Risk_Level"] == risk_sel]["Contingency"].iloc[0])

    fx_rate, tax_rate = get_country_data(country_sel, currency_sel)

    st.markdown("---")
    
    # AJUSTE: E/R solo visible si es Local Currency
    if currency_sel != "USD":
        st.metric("Exchange Rate", f"{fx_rate:,.4f}")
    
    st.metric("Risk", f"{risk_val:.1%}")
    st.caption("LAcostWeb V22 | Tuned")

# --- HEADER ---
st.title("LAcostWeb V22 🚀")

with st.container():
    c_cust1, c_cust2, c_date1, c_date2 = st.columns([2, 1, 1, 1])
    with c_cust1: cust_name = st.text_input("Customer Name", placeholder="Client Name")
    with c_cust2: cust_num = st.text_input("Cust. #", placeholder="ID")
    with c_date1: c_start = st.date_input("Start Date", value=date.today())
    with c_date2: c_end = st.date_input("End Date", value=date.today().replace(year=date.today().year + 1))

st.divider()

# --- SERVICIOS ---
st.subheader("📋 Services")

grand_total_price = 0.0
summary_lines = []

offer_list = DB_OFFERINGS["Offering"].tolist()

for i, line in enumerate(st.session_state.lines):
    current_offering_name = line.get("selected_offering", "New Item")
    
    with st.expander(f"🔹 {i+1}. {current_offering_name}", expanded=True):
        
        # FILA 1: Offering (Safe Lookup)
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns([4, 0.8, 0.8, 0.3])
        
        with r1_c1:
            try: 
                curr_idx = offer_list.index(line.get("selected_offering", offer_list[0]))
            except: 
                curr_idx = 0
            
            sel_offering = st.selectbox("Offering Name", offer_list, index=curr_idx, key=f"off_{i}", label_visibility="collapsed")
            st.session_state.lines[i]["selected_offering"] = sel_offering
            
            off_data = DB_OFFERINGS[DB_OFFERINGS["Offering"] == sel_offering].iloc[0]
            
        with r1_c2: st.text_input("L40", value=off_data["L40"], key=f"l40_{i}", disabled=True, label_visibility="collapsed")
        with r1_c3: st.text_input("Conga", value=off_data["Conga"], key=f"cng_{i}", disabled=True, label_visibility="collapsed")
        with r1_c4: 
            if st.button("🗑️", key=f"del_{i}"):
                remove_line(i)
                st.rerun()

        # FILA 2: Inputs Operativos + Costo Local
        # Desc | Start | End | Mth | Qty | Cost USD | Cost Local | GP% | TOTAL
        r2_c1, r2_c2, r2_c3, r2_c_dur, r2_c4, r2_c5, r2_c_loc, r2_c6, r2_c7 = st.columns([1.5, 0.9, 0.9, 0.5, 0.5, 0.8, 0.8, 0.6, 1.2])
        
        with r2_c1: desc = st.text_input("Desc", key=f"desc_{i}")
        
        with r2_c2: 
            s_s = st.date_input("Start", value=line.get("start_date", date.today()), key=f"ss_{i}")
            st.session_state.lines[i]["start_date"] = s_s
        with r2_c3: 
            s_e = st.date_input("End", value=line.get("end_date", date.today().replace(year=date.today().year + 1)), key=f"se_{i}")
            st.session_state.lines[i]["end_date"] = s_e
        
        dur = calculate_months(s_s, s_e)
        with r2_c_dur: 
            dur_key = f"dur_disp_{i}"
            st.session_state[dur_key] = str(dur)
            st.text_input("Mth", disabled=True, key=dur_key)

        with r2_c4: 
            # AJUSTE: QTY sin botones (Text Input -> Int)
            qty_txt = st.text_input("Qty", value=str(line.get("qty", 1)), key=f"qty_{i}")
            qty = int(safe_float(qty_txt))
            st.session_state.lines[i]["qty"] = qty
        
        with r2_c5: 
            # Costo en USD
            cost_txt = st.text_input("Unit USD", value=str(line.get("unit_cost", 0.0)), key=f"uc_{i}")
            unit_cost = safe_float(cost_txt)
            st.session_state.lines[i]["unit_cost"] = unit_cost
            
        with r2_c_loc:
            # AJUSTE: Costo Local HABILITADO (Editable)
            # Calculamos el valor sugerido
            suggested_local = unit_cost * fx_rate if currency_sel != "USD" else unit_cost
            # Lo mostramos en un input editable. Nota: Si el usuario edita, no actualiza el USD (flujo unidireccional simple)
            st.text_input("Unit Loc", value=f"{suggested_local:,.0f}", key=f"ucl_{i}", help="Editable field. Default is calculated.")
        
        with r2_c6: 
            gp_txt = st.text_input("GP %", value=str(line.get("gp_percent", 40)), key=f"gp_{i}")
            gp_val = safe_float(gp_txt)
            st.session_state.lines[i]["gp_percent"] = gp_val
            gp_factor = gp_val / 100.0

        # CÁLCULO FINAL (V3 con Taxes)
        total_cost_base = unit_cost * qty * dur
        
        if currency_sel != "USD":
            total_cost_final = total_cost_base * fx_rate
        else:
            total_cost_final = total_cost_base
            
        divisor = 1 - gp_factor
        if divisor <= 0: divisor = 0.01 
            
        base_price = (total_cost_final * (1 + risk_val)) / divisor
        final_line_price = base_price * (1 + tax_rate)
        
        grand_total_price += final_line_price
        
        summary_lines.append({"Service": sel_offering, "Qty": qty, "Price": final_line_price})

        with r2_c7:
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
c1, c2 = st.columns([3, 1])
if summary_lines: c1.dataframe(pd.DataFrame(summary_lines), use_container_width=True)

with c2:
    st.markdown(f"""
        <div style="text-align: right;">
            <h5 style="margin:0; color: gray;">TOTAL</h5>
            <h1 style="margin:0; color: #0F62FE;">${grand_total_price:,.2f}</h1>
            <p style="font-weight: bold;">{currency_sel}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📧 Outlook Draft", type="primary"):
        subject = f"Quote: {cust_name} - {currency_sel} ${grand_total_price:,.2f}"
        body = f"Customer: {cust_name}\nTotal: {grand_total_price:,.2f}"
        link = f"mailto:andresma@co.ibm.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;url={link}">', unsafe_allow_html=True)