import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# ==========================================
# 0. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="LAcostWeb V8", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    /* Estilo para métricas en el sidebar */
    .css-1r6slb0 { border: 1px solid #e0e0e0; padding: 10px; border-radius: 5px; }
    h1 { color: #0F62FE; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS (Mismos datos V2)
# ==========================================
DB_COUNTRIES = pd.DataFrame([
    {"Country": "Argentina", "Currency_Code": "ARS", "Exchange_Rate": 1428.95, "Tax_Rate": 0.0529},
    {"Country": "Brazil",    "Currency_Code": "BRL", "Exchange_Rate": 5.34,    "Tax_Rate": 0.1425},
    {"Country": "Chile",     "Currency_Code": "CLP", "Exchange_Rate": 934.70,  "Tax_Rate": 0.0},
    {"Country": "Chile",     "Currency_Code": "CLF", "Exchange_Rate": 0.02358, "Tax_Rate": 0.0},
    {"Country": "Colombia",  "Currency_Code": "COP", "Exchange_Rate": 3775.22, "Tax_Rate": 0.01},
    {"Country": "Ecuador",   "Currency_Code": "USD", "Exchange_Rate": 1.0,     "Tax_Rate": 0.0},
    {"Country": "Peru",      "Currency_Code": "PEN", "Exchange_Rate": 3.37,    "Tax_Rate": 0.0},
    {"Country": "Mexico",    "Currency_Code": "MXN", "Exchange_Rate": 18.42,   "Tax_Rate": 0.0},
    {"Country": "Uruguay",   "Currency_Code": "UYU", "Exchange_Rate": 39.73,   "Tax_Rate": 0.0},
    {"Country": "Venezuela", "Currency_Code": "VES", "Exchange_Rate": 235.28,  "Tax_Rate": 0.0155}
])

DB_RISK = pd.DataFrame({
    "Risk_Level": ["Low", "Medium", "High"],
    "Contingency": [0.02, 0.05, 0.08]
})

DB_OFFERINGS = pd.DataFrame([
    {"Offering": "IBM Hardware Resell for Server and Storage-Lenovo", "L40": "6942-1BT", "Conga": "Location Based Services"},
    {"Offering": "1-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Conga": "Conga by CSV"},
    {"Offering": "2-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Conga": "Conga by CSV"},
    {"Offering": "SWMA MVS SPT other Prod", "L40": "6942-76O", "Conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat", "L40": "6948-B73", "Conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat - Enterprise Linux Subscription", "L40": "6942-42T", "Location Based Services": "Location Based Services"},
    {"Offering": "Subscription for Red Hat", "L40": "6948-66J", "Conga": "Location Based Services"},
    {"Offering": "Support for Red Hat", "L40": "6949-66K", "Conga": "Location Based Services"},
    {"Offering": "IBM Support for Oracle", "L40": "6942-42E", "Conga": "Location Based Services"},
    {"Offering": "IBM Customized Support for Multivendor Hardware Services", "L40": "6942-76T", "Conga": "Location Based Services"},
    {"Offering": "IBM Customized Support for Multivendor Software Services", "L40": "6942-76U", "Conga": "Location Based Services"},
    {"Offering": "IBM Customized Support for Hardware Services-Logo", "L40": "6942-76V", "Conga": "Location Based Services"},
    {"Offering": "IBM Customized Support for Software Services-Logo", "L40": "6942-76W", "Conga": "Location Based Services"},
    {"Offering": "HWMA MVS SPT other Loc", "L40": "6942-0ID", "Conga": "Location Based Services"},
    {"Offering": "SWMA MVS SPT other Loc", "L40": "6942-0IG", "Conga": "Location Based Services"},
    {"Offering": "Relocation Services - Packaging", "L40": "6942-54E", "Conga": "Location Based Services"},
    {"Offering": "Relocation Services - Movers Charge", "L40": "6942-54F", "Conga": "Location Based Services"},
    {"Offering": "Relocation Services - Travel and Living", "L40": "6942-54R", "Conga": "Location Based Services"},
    {"Offering": "Relocation Services - External Vendor's Charge", "L40": "6942-78O", "Conga": "Location Based Services"}
])

# ==========================================
# 2. LÓGICA
# ==========================================
def calculate_months(start, end):
    if start > end: return 0.0
    return round((end - start).days / 30.44, 1)

def get_country_data(country, currency_code):
    if currency_code == "USD":
        row = DB_COUNTRIES[DB_COUNTRIES["Country"] == country].iloc[0]
        return 1.0, float(row["Tax_Rate"])
    row = DB_COUNTRIES[(DB_COUNTRIES["Country"] == country) & (DB_COUNTRIES["Currency_Code"] == currency_code)]
    if not row.empty:
        return float(row["Exchange_Rate"].iloc[0]), float(row["Tax_Rate"].iloc[0])
    return 1.0, 0.0

if 'lines' not in st.session_state:
    st.session_state.lines = []

def add_line():
    st.session_state.lines.append({
        "offering_idx": 0, "qty": 1, "start_date": date.today(),
        "end_date": date.today().replace(year=date.today().year + 1),
        "unit_cost": 0.0, "gp_target": 0.20
    })

def remove_line(index):
    st.session_state.lines.pop(index)

# ==========================================
# 3. LAYOUT (Modificado V8)
# ==========================================

# --- SIDEBAR: CONTROLES FINANCIEROS Y MÉTRICAS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
    st.markdown("## ⚙️ Financial Config")
    
    # 1. Región y Moneda
    st.caption("Region & Currency")
    country_list = sorted(DB_COUNTRIES["Country"].unique())
    country_sel = st.selectbox("Country", country_list)
    
    available_currencies = DB_COUNTRIES[DB_COUNTRIES["Country"] == country_sel]["Currency_Code"].unique().tolist()
    currency_options = list(dict.fromkeys(["USD"] + available_currencies)) 
    currency_sel = st.pills("Currency", currency_options, selection_mode="single", default=currency_options[0])
    
    # 2. Riesgo
    st.caption("Risk Management")
    risk_sel = st.selectbox("QA Risk Level", DB_RISK["Risk_Level"])
    risk_val = float(DB_RISK[DB_RISK["Risk_Level"] == risk_sel]["Contingency"].iloc[0])

    # Cálculos en segundo plano
    fx_rate, tax_rate = get_country_data(country_sel, currency_sel)

    st.markdown("---")
    st.markdown("### 📊 Live Metrics")
    
    # 3. Las métricas que pediste mover a la izquierda
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Exchange Rate", f"{fx_rate:,.2f}")
    with col_s2:
        st.metric("Risk Applied", f"{risk_val:.1%}")
    
    st.metric("Local Logic / Tax", "Active" if tax_rate > 0 else "N/A", 
              help="Tax calculation is applied internally but hidden from main view.")

    st.markdown("---")
    st.caption("LAcostWeb V8 | Internal Use Only")

# --- MAIN AREA: CLIENTE Y LÍNEAS ---
st.title("LAcostWeb V8 🚀")

# 1. SECCIÓN CLIENTE (Movida a la derecha)
with st.container():
    st.subheader("👤 Customer Information")
    c_cust1, c_cust2, c_cust3 = st.columns([2, 1, 1])
    with c_cust1:
        cust_name = st.text_input("Customer Name", placeholder="Enter Client Name...")
    with c_cust2:
        cust_num = st.text_input("Customer Number", placeholder="ID#")
    with c_cust3:
        quote_date = st.date_input("Quote Date", value=date.today(), disabled=True)

st.divider()

# 2. SECCIÓN DE LÍNEAS
st.subheader("📋 Service Lines")

grand_total_price = 0.0
summary_lines = []

for i, line in enumerate(st.session_state.lines):
    with st.expander(f"🔹 Line #{i+1}: {line.get('selected_offering', 'New Service')}", expanded=True):
        
        # Catálogo
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            offer_list = DB_OFFERINGS["Offering"].tolist()
            try: curr_idx = offer_list.index(line.get("selected_offering", offer_list[0]))
            except: curr_idx = 0
            sel_offering = st.selectbox("Offering", offer_list, index=curr_idx, key=f"off_{i}", label_visibility="collapsed")
            st.session_state.lines[i]["selected_offering"] = sel_offering
            off_data = DB_OFFERINGS[DB_OFFERINGS["Offering"] == sel_offering].iloc[0]
        with c2: st.text_input("L40", value=off_data["L40"], key=f"l40_{i}", disabled=True)
        with c3: st.text_input("Conga", value=off_data["Conga"], key=f"cng_{i}", disabled=True)

        # Inputs
        c4, c5, c6, c7, c8 = st.columns([2, 1, 1, 1, 1])
        with c4: desc = st.text_input("Desc", key=f"desc_{i}", placeholder="Details...")
        with c5: qty = st.number_input("Qty", min_value=1, value=1, key=f"qty_{i}")
        with c6: unit_cost = st.number_input("Unit Cost (USD)", min_value=0.0, key=f"uc_{i}")
        with c7:
            s_s = st.date_input("Start", value=date.today(), key=f"ss_{i}")
            s_e = st.date_input("End", value=date.today().replace(year=date.today().year + 1), key=f"se_{i}")
            dur = calculate_months(s_s, s_e)
        with c8: gp = st.number_input("GP Target", 0.0, 0.99, 0.20, step=0.01, key=f"gp_{i}")

        # Cálculo y Resultado Línea
        c_res, c_del = st.columns([5, 1])
        with c_res:
            total_cost = unit_cost * qty * dur * fx_rate
            divisor = 1 - gp
            base_price = (total_cost * (1 + risk_val)) / divisor if divisor > 0 else 0
            final_line_price = base_price * (1 + tax_rate)
            grand_total_price += final_line_price
            
            st.info(f"💵 Line Price: **${final_line_price:,.2f}** ({currency_sel}) | Duration: {dur} months")
            summary_lines.append({"Offering": sel_offering, "Qty": qty, "Price": final_line_price})

        with c_del:
            st.write("")
            if st.button("🗑️", key=f"del_{i}"):
                remove_line(i)
                st.rerun()

if st.button("➕ Add New Service Line"):
    add_line()

st.divider()

# 3. RESUMEN
st.subheader("💰 Quote Summary")
col_sum1, col_sum2 = st.columns([2, 1])

with col_sum1:
    if summary_lines:
        st.dataframe(pd.DataFrame(summary_lines), use_container_width=True, hide_index=True)
    else:
        st.caption("No lines added yet.")

with col_sum2:
    st.markdown(f"""
        <div style="background-color: #e0eaff; padding: 20px; border-radius: 10px; border: 2px solid #0F62FE; text-align: center;">
            <h4 style="margin:0; color: #0F62FE;">GRAND TOTAL</h4>
            <h1 style="margin:0; font-size: 3em;">${grand_total_price:,.2f}</h1>
            <p style="margin:0;">{currency_sel}</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("📧 Open in Outlook (Draft)", type="primary"):
        if not cust_name:
            st.error("Please enter Customer Name.")
        else:
            subject = f"LAcostWeb V8: {cust_name} - Total {currency_sel} ${grand_total_price:,.2f}"
            body = f"""
LAcostWeb V8 Proposal
---------------------
Customer: {cust_name} ({cust_num})
Region: {country_sel} | Currency: {currency_sel}
Risk: {risk_sel}

Services:
"""
            for l in summary_lines:
                body += f"- {l['Offering']} (Qty: {l['Qty']}) = ${l['Price']:,.2f}\n"
            body += f"\nTOTAL: ${grand_total_price:,.2f}"
            
            link = f"mailto:andresma@co.ibm.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            st.markdown(f'<meta http-equiv="refresh" content="0;url={link}">', unsafe_allow_html=True)
            st.success("Opening Outlook...")