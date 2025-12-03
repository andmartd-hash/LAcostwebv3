import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse

# ==========================================
# 1. BASE DE DATOS (Actualizada con tus archivos V2)
# ==========================================

# TABLA PAÍSES + IMPUESTOS (Taxes/deduc)
# Fuente: V2-BASE.xlsx - countries.csv
DB_COUNTRIES = pd.DataFrame([
    {"Country": "Argentina", "Currency_Code": "ARS", "Exchange_Rate": 1428.95, "Tax_Rate": 0.0501},
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

# TABLA RIESGOS
# Fuente: V2-BASE.xlsx - QA Risk.csv
DB_RISK = pd.DataFrame({
    "Risk_Level": ["Low", "Medium", "High"],
    "Contingency": [0.02, 0.05, 0.08]
})

# TABLA OFERTAS (Catálogo Completo)
# Fuente: V2-BASE.xlsx - Offering.csv
DB_OFFERINGS = pd.DataFrame([
    {"Offering": "IBM Hardware Resell for Server and Storage-Lenovo", "L40": "6942-1BT", "Conga": "Location Based Services"},
    {"Offering": "1-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Conga": "Conga by CSV"},
    {"Offering": "2-HWMA MVS SPT other Prod", "L40": "6942-0IC", "Conga": "Conga by CSV"},
    {"Offering": "SWMA MVS SPT other Prod", "L40": "6942-76O", "Conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat", "L40": "6948-B73", "Conga": "Conga by CSV"},
    {"Offering": "IBM Support for Red Hat - Enterprise Linux Subscription", "L40": "6942-42T", "Conga": "Location Based Services"},
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
# 2. FUNCIONES DE LÓGICA
# ==========================================

def calculate_months(start, end):
    if start > end: return 0.0
    return round((end - start).days / 30.44, 1)

def get_country_data(country, currency_code):
    """Devuelve Tasa de Cambio y Tasa de Impuesto"""
    # Filtro por país y moneda (para manejar Chile CLP/CLF)
    if currency_code == "USD":
        # Si es USD, la tasa de cambio es 1, pero necesitamos buscar el Impuesto del país
        # Buscamos la primera entrada del país para sacar el Tax
        row = DB_COUNTRIES[DB_COUNTRIES["Country"] == country].iloc[0]
        return 1.0, float(row["Tax_Rate"])
    
    # Si es moneda local, buscamos la fila exacta
    row = DB_COUNTRIES[(DB_COUNTRIES["Country"] == country) & (DB_COUNTRIES["Currency_Code"] == currency_code)]
    
    if not row.empty:
        return float(row["Exchange_Rate"].iloc[0]), float(row["Tax_Rate"].iloc[0])
    return 1.0, 0.0

if 'lines' not in st.session_state:
    st.session_state.lines = []

def add_line():
    st.session_state.lines.append({
        "offering_idx": 0,
        "qty": 1,
        "start_date": date.today(),
        "end_date": date.today().replace(year=date.today().year + 1),
        "unit_cost": 0.0,
        "gp_target": 0.20
    })

def remove_line(index):
    st.session_state.lines.pop(index)

# ==========================================
# 3. INTERFAZ DE USUARIO (LAcostWeb V5)
# ==========================================

st.set_page_config(page_title="LAcostWeb V5", layout="wide", page_icon="🌎")

st.title("🌎 LAcostWeb V5")
st.caption("New Tax Logic | Updated Catalog | Global Risk")

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
        # Selector de País
        country_list = sorted(DB_COUNTRIES["Country"].unique())
        country_sel = st.selectbox("Countries", country_list)
        
        # Lógica de Moneda
        available_currencies = DB_COUNTRIES[DB_COUNTRIES["Country"] == country_sel]["Currency_Code"].unique().tolist()
        currency_options = ["USD"] + available_currencies
        # Eliminamos duplicados si USD ya estaba (caso Ecuador)
        currency_options = list(dict.fromkeys(currency_options)) 
        
        currency_sel = st.radio("Currency Selection", currency_options, horizontal=True)
        
        # QA RISK (Global)
        risk_sel = st.selectbox("QA Risk", DB_RISK["Risk_Level"])
        risk_val = float(DB_RISK[DB_RISK["Risk_Level"] == risk_sel]["Contingency"].iloc[0])

    with c4:
        st.subheader("Rates & Taxes")
        # Obtenemos Tasa de Cambio e Impuestos
        fx_rate, tax_rate = get_country_data(country_sel, currency_sel)
        
        st.metric(f"Exchange Rate ({currency_sel})", f"{fx_rate:,.4f}")
        st.metric(f"Local Tax/Deduc", f"{tax_rate:.2%}")
        st.info(f"Risk Applied: {risk_val:.1%}")

st.markdown("---")

# --- SECTION 2: COST LINES ---
st.header("2. Cost Lines & Offerings")

col_add, col_info = st.columns([1, 6])
with col_add:
    if st.button("➕ Add Line Item"):
        add_line()

grand_total_price = 0.0
summary_lines = []

for i, line in enumerate(st.session_state.lines):
    with st.expander(f"Line #{i+1}", expanded=True):
        # Row 1: Offering
        lc1, lc2, lc3, lc4 = st.columns([3, 1.5, 1.5, 0.5])
        with lc1:
            offer_list = DB_OFFERINGS["Offering"].tolist()
            selected_offering = st.selectbox(f"Offering #{i+1}", offer_list, key=f"off_name_{i}")
            off_data = DB_OFFERINGS[DB_OFFERINGS["Offering"] == selected_offering].iloc[0]
        with lc2:
            st.text_input(f"L40", value=off_data["L40"], key=f"l40_{i}", disabled=True)
        with lc3:
            st.text_input(f"Load in Conga", value=off_data["Conga"], key=f"conga_{i}", disabled=True)
        with lc4:
            if st.button("🗑️", key=f"del_{i}"):
                remove_line(i)
                st.rerun()

        # Row 2: Inputs
        li1, li2, li3, li4, li5, li6 = st.columns(6)
        with li1:
            desc = st.text_input(f"Description", key=f"desc_{i}")
        with li2:
            qty = st.number_input(f"QTY", min_value=1, value=1, key=f"qty_{i}")
        with li3:
            s_start = st.date_input(f"Start", value=date.today(), key=f"sd_{i}")
        with li4:
            s_end = st.date_input(f"End", value=date.today().replace(year=date.today().year + 1), key=f"se_{i}")
        with li5:
            duration = calculate_months(s_start, s_end)
            st.text_input(f"Months", value=str(duration), disabled=True, key=f"dur_{i}")
        with li6:
            unit_cost = st.number_input(f"Unit Cost (USD)", min_value=0.0, key=f"cost_{i}")

        # Row 3: GP & Calc
        lc_calc1, lc_calc2 = st.columns([1, 3])
        with lc_calc1:
            gp = st.slider(f"GP Target #{i+1}", 0.0, 0.99, 0.20, key=f"gp_{i}")
        
        with lc_calc2:
            # --- FORMULA V5 ---
            # 1. Total Cost = Unit * Qty * Dur * FX
            total_cost = unit_cost * qty * duration * fx_rate
            
            # 2. Base Price = Total Cost * (1 + Risk) / (1 - GP)
            divisor = 1 - gp
            base_price = 0.0
            if divisor > 0:
                base_price = (total_cost * (1 + risk_val)) / divisor
            
            # 3. Final Price (With Taxes) = Base Price * (1 + Tax_Rate)
            # Interpretación: "sumarle el porcentaje de taxes"
            final_line_price = base_price * (1 + tax_rate)
            
            grand_total_price += final_line_price
            
            st.success(f"Line Price (Inc. Tax): **${final_line_price:,.2f}** ({currency_sel})")
            if tax_rate > 0:
                st.caption(f"Base: ${base_price:,.2f} + Tax: {tax_rate:.2%}")
            
            summary_lines.append({
                "Offering": selected_offering,
                "Qty": qty,
                "Duration": duration,
                "Price": final_line_price
            })

# --- SECTION 3: SUMMARY ---
st.markdown("---")
st.header("3. Quote Summary")

c_tot1, c_tot2 = st.columns([3, 1])
with c_tot1:
    if summary_lines: st.dataframe(pd.DataFrame(summary_lines))
with c_tot2:
    st.metric("TOTAL QUOTE", f"${grand_total_price:,.2f}", delta=currency_sel)

# EMAIL BUTTON
if st.button("📧 Generate Email Draft"):
    if not cust_name:
        st.error("Missing Customer Name")
    else:
        subject = f"LAcostWeb V5: {cust_name} - Total {currency_sel} ${grand_total_price:,.2f}"
        body = f"""
LAcostWeb V5 Proposal
---------------------
Customer: {cust_name} ({cust_num})
Country: {country_sel}
Currency: {currency_sel} (Rate: {fx_rate})
Global Risk: {risk_sel} ({risk_val:.1%})
Applicable Tax/Deduc: {tax_rate:.2%}

Details:
"""
        for l in summary_lines:
            body += f"- {l['Offering']} | Qty: {l['Qty']} | ${l['Price']:,.2f}\n"
            
        body += f"\nGRAND TOTAL (Inc. Taxes): ${grand_total_price:,.2f}"
        
        link = f"mailto:andresma@co.ibm.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        st.markdown(f'<a href="{link}" target="_blank"><button style="background:#0F62FE;color:white;padding:10px;border-radius:5px;border:none;">Open in Outlook ↗</button></a>', unsafe_allow_html=True)