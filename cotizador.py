import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# ==========================================
# 1. DATABASE (Simulada desde tus CSVs)
# ==========================================

# Data: Countries
DB_COUNTRIES = pd.DataFrame({
    "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Ecuador", "Peru", "Mexico", "Uruguay", "Venezuela"],
    "Currency_Code": ["ARS", "BRL", "CLP", "COP", "USD", "PEN", "MXN", "UYU", "VES"],
    "Exchange_Rate": [1428.95, 5.34, 934.70, 3775.22, 1.0, 3.37, 18.42, 39.73, 235.28]
})

# Data: QA Risk
DB_RISK = pd.DataFrame({
    "Risk_Level": ["Low", "Medium", "High"],
    "Contingency": [0.02, 0.05, 0.08]
})

# Data: Offering (Catálogo ampliado según tu archivo)
DB_OFFERINGS = pd.DataFrame([
    {"Offering": "IBM Hardware Resell for Server and Storage-Lenovo", "L40": "6942-1BT", "Conga": "Location Based Services"},
    {"Offering": "1-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Conga": "Conga by CSV"},
    {"Offering": "2-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Conga": "Conga by CSV"},
    {"Offering": "SWMA MVS SPT other Prod", "L40": "6942-76O", "Conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat", "L40": "6948-B73", "Conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat - Enterprise Linux Subscription", "L40": "6942-42T", "Conga": "Location Based Services"},
    {"Offering": "Support for Red Hat", "L40": "6949-66K", "Conga": "Location Based Services"},
    {"Offering": "IBM Support for Oracle", "L40": "6942-42E", "Conga": "Location Based Services"},
    {"Offering": "Relocation Services - Packaging", "L40": "6942-54E", "Conga": "Location Based Services"},
])

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def calculate_months(start, end):
    if start > end: return 0.0
    return round((end - start).days / 30.44, 1)

def get_exchange_rate(country, currency_mode):
    if currency_mode == "USD" or country == "Ecuador":
        return 1.0
    row = DB_COUNTRIES[DB_COUNTRIES["Country"] == country]
    if not row.empty:
        return float(row["Exchange_Rate"].iloc[0])
    return 1.0

# Inicializar estado para líneas múltiples
if 'lines' not in st.session_state:
    st.session_state.lines = []

def add_line():
    st.session_state.lines.append({
        "offering_idx": 0,
        "desc": "",
        "qty": 1,
        "start_date": date.today(),
        "end_date": date.today().replace(year=date.today().year + 1),
        "unit_cost": 0.0,
        "gp_target": 0.20
    })

def remove_line(index):
    st.session_state.lines.pop(index)

# ==========================================
# 3. USER INTERFACE
# ==========================================

st.set_page_config(page_title="IBM Pricing Tool V3", layout="wide", page_icon="🌐")

st.title("🌐 IBM Services Pricing Tool V3")
st.caption("Multi-line Support | Global Risk Config | English Fields")

# --- SECTION 1: GENERAL CONFIGURATION ---
st.header("1. General Configuration")

with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.subheader("Customer Info")
        cust_name = st.text_input("Customer Name")
        cust_num = st.text_input("Customer Number")
        quote_date = st.date_input("Quote Date", value=date.today(), disabled=True)
    
    with c2:
        st.subheader("Contract Info")
        contract_start = st.date_input("Contract Start Date", value=date.today())
        contract_end = st.date_input("Contract End Date", value=date.today().replace(year=date.today().year + 1))
        
    with c3:
        st.subheader("Financial Config")
        country_sel = st.selectbox("Countries", DB_COUNTRIES["Country"])
        currency_sel = st.radio("Currency", ["USD", "Local"], horizontal=True)
        
        # QA RISK (Ahora Global)
        risk_sel = st.selectbox("QA Risk", DB_RISK["Risk_Level"])
        risk_val = float(DB_RISK[DB_RISK["Risk_Level"] == risk_sel]["Contingency"].iloc[0])
        st.info(f"Global Contingency: {risk_val:.1%}")

    with c4:
        st.subheader("Exchange Rate")
        fx_rate = get_exchange_rate(country_sel, currency_sel)
        st.metric("Exchange Rate used", f"{fx_rate:,.2f}")

st.markdown("---")

# --- SECTION 2: SERVICE LINES (COSTOS) ---
st.header("2. Cost Lines & Offerings")

# Botón para agregar línea
col_add, col_info = st.columns([1, 6])
with col_add:
    if st.button("➕ Add Line Item"):
        add_line()

# Loop para mostrar cada línea
grand_total_price = 0.0
summary_lines = []

for i, line in enumerate(st.session_state.lines):
    with st.expander(f"Line #{i+1}", expanded=True):
        # Fila 1: Offering Info
        lc1, lc2, lc3, lc4 = st.columns([3, 1.5, 1.5, 0.5])
        with lc1:
            # Offering Selector
            # Buscamos el índice actual para mantener la selección
            offer_list = DB_OFFERINGS["Offering"].tolist()
            selected_offering = st.selectbox(f"Offering #{i+1}", offer_list, key=f"off_name_{i}")
            
            # Auto-fill logic
            off_data = DB_OFFERINGS[DB_OFFERINGS["Offering"] == selected_offering].iloc[0]
            
        with lc2:
            st.text_input(f"L40", value=off_data["L40"], key=f"l40_{i}", disabled=True)
        with lc3:
            st.text_input(f"Load in Conga", value=off_data["Conga"], key=f"conga_{i}", disabled=True)
        with lc4:
            if st.button("🗑️", key=f"del_{i}"):
                remove_line(i)
                st.rerun()

        # Fila 2: Inputs
        li1, li2, li3, li4, li5, li6 = st.columns(6)
        with li1:
            desc = st.text_input(f"Description Service", key=f"desc_{i}")
        with li2:
            qty = st.number_input(f"QTY", min_value=1, value=1, key=f"qty_{i}")
        with li3:
            s_start = st.date_input(f"Service Start", value=date.today(), key=f"sd_{i}")
        with li4:
            s_end = st.date_input(f"Service End", value=date.today().replace(year=date.today().year + 1), key=f"se_{i}")
        with li5:
            duration = calculate_months(s_start, s_end)
            st.text_input(f"Duration (Months)", value=str(duration), disabled=True, key=f"dur_{i}")
        with li6:
            unit_cost = st.number_input(f"Unit Cost (USD)", min_value=0.0, key=f"cost_{i}")

        # Fila 3: GP & Calc
        lc_calc1, lc_calc2 = st.columns([1, 3])
        with lc_calc1:
            gp = st.slider(f"GP Target #{i+1}", 0.0, 0.99, 0.20, key=f"gp_{i}")
        
        with lc_calc2:
            # --- FORMULAS ---
            # 1. Total Cost = Unit * Qty * Duration * FX
            total_cost = unit_cost * qty * duration * fx_rate
            
            # 2. Price = Total Cost * (1 + GlobalRisk) / (1 - GP)
            divisor = 1 - gp
            line_price = 0.0
            if divisor > 0:
                line_price = (total_cost * (1 + risk_val)) / divisor
            
            grand_total_price += line_price
            
            st.success(f"Line Price: **${line_price:,.2f}** ({currency_sel})")
            
            # Guardar datos para resumen
            summary_lines.append({
                "Offering": selected_offering,
                "L40": off_data["L40"],
                "Qty": qty,
                "Duration": duration,
                "Total Cost": total_cost,
                "Price": line_price
            })

# --- SECTION 3: GRAND TOTAL & OUTPUT ---
st.markdown("---")
st.header("3. Quote Summary")

tot_col1, tot_col2 = st.columns([3, 1])

with tot_col1:
    if len(summary_lines) > 0:
        st.dataframe(pd.DataFrame(summary_lines))
    else:
        st.info("No lines added yet.")

with tot_col2:
    st.metric(label="TOTAL QUOTE VALUE", value=f"${grand_total_price:,.2f}", delta=currency_sel)

# EMAIL GENERATION
if st.button("📧 Create Email Draft", type="primary"):
    if not cust_name:
        st.error("Please enter Customer Name first.")
    else:
        # Build Body
        lines_text = ""
        for item in summary_lines:
            lines_text += f"- {item['Offering']} (L40: {item['L40']}) | Qty: {item['Qty']} | Dur: {item['Duration']}mo | Price: ${item['Price']:,.2f}\n"
        
        subject = f"Pricing Proposal: {cust_name} - Total ${grand_total_price:,.2f}"
        body = f"""
Dear Team/Client,

Please find below the proposal details:

CUSTOMER: {cust_name} ({cust_num})
COUNTRY: {country_sel}
CURRENCY: {currency_sel}
RISK APPLIED: {risk_sel} ({risk_val:.1%})

SERVICES:
{lines_text}

---------------------------------------
GRAND TOTAL: ${grand_total_price:,.2f}
---------------------------------------

Regards,
Andresma
        """
        
        # Link Mailto
        safe_subject = urllib.parse.quote(subject)
        safe_body = urllib.parse.quote(body)
        mailto_link = f"mailto:andresma@co.ibm.com?subject={safe_subject}&body={safe_body}"
        
        st.markdown(f'''
            <a href="{mailto_link}" target="_blank">
                <button style="background-color:#0F62FE;color:white;padding:12px 20px;border-radius:4px;border:none;font-weight:bold;cursor:pointer;">
                    🚀 Open in Outlook
                </button>
            </a>
        ''', unsafe_allow_html=True)