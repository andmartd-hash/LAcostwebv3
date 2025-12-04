import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import traceback # Para mostrar el error real si ocurre

# ==========================================
# 0. MODO SEGURO (Error Catching)
# ==========================================
try:
    # ==========================================
    # 1. CONFIGURACIÓN Y ESTILOS
    # ==========================================
    st.set_page_config(page_title="LAcostWeb V21", layout="wide", page_icon="🛡️")

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
    # 2. BASE DE DATOS (V3 COMPLETA HARDCODED)
    # ==========================================

    # PAÍSES (Datos V3: E/R, Currency, Taxes)
    # Usamos nombres de columnas internos simples para evitar errores
    DB_COUNTRIES = pd.DataFrame([
        {"Country": "Argentina", "Code": "ARS", "Rate": 1428.9486, "Tax": 0.0529},
        {"Country": "Brazil",    "Code": "BRL", "Rate": 5.3410,    "Tax": 0.1425},
        {"Country": "Chile",     "Code": "CLP", "Rate": 934.704,   "Tax": 0.0},
        {"Country": "Chile",     "Code": "CLF", "Rate": 0.02358,   "Tax": 0.0},
        {"Country": "Colombia",  "Code": "COP", "Rate": 3775.22,   "Tax": 0.01},
        {"Country": "Ecuador",   "Code": "USD", "Rate": 1.0,       "Tax": 0.0},
        {"Country": "Peru",      "Code": "PEN", "Rate": 3.3729,    "Tax": 0.0},
        {"Country": "Mexico",    "Code": "MXN", "Rate": 18.4203,   "Tax": 0.0},
        {"Country": "Uruguay",   "Code": "UYU", "Rate": 39.7318,   "Tax": 0.0},
        {"Country": "Venezuela", "Code": "VES", "Rate": 235.28,    "Tax": 0.0155}
    ])

    # RIESGOS (Datos V3)
    DB_RISK = pd.DataFrame([
        {"Level": "Low", "Factor": 0.02},
        {"Level": "Medium", "Factor": 0.05},
        {"Level": "High", "Factor": 0.08}
    ])

    # OFERTAS (Datos V3 - 23 Servicios)
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
    # 3. LÓGICA SEGURA
    # ==========================================
    def safe_float(val):
        try: return float(val)
        except: return 0.0

    def calc_months(start, end):
        if not start or not end or start > end: return 0.0
        return round((end - start).days / 30.44, 1)

    def get_country_data(country_name, currency_code):
        try:
            # Caso USD
            if currency_code == "USD":
                # Buscamos el país solo para sacar el Tax
                row = DB_COUNTRIES[DB_COUNTRIES["Country"] == country_name].iloc[0]
                return 1.0, float(row["Tax"])
            
            # Caso Local
            row = DB_COUNTRIES[(DB_COUNTRIES["Country"] == country_name) & (DB_COUNTRIES["Code"] == currency_code)]
            if not row.empty:
                return float(row["Rate"].iloc[0]), float(row["Tax"].iloc[0])
        except:
            pass
        return 1.0, 0.0

    if 'lines' not in st.session_state:
        st.session_state.lines = []

    def add_line():
        st.session_state.lines.append({
            "offering_idx": 0, "qty": 1, "unit_cost": 0.0, "gp_percent": 40.0,
            "svc_start": date.today(),
            "svc_end": date.today().replace(year=date.today().year + 1)
        })

    def remove_line(idx):
        st.session_state.lines.pop(idx)

    # ==========================================
    # 4. INTERFAZ V3 (ESTRUCTURA V14)
    # ==========================================

    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
        st.header("Config V3")
        
        # País
        country_sel = st.selectbox("Countries", sorted(DB_COUNTRIES["Country"].unique()))
        
        # Moneda (Lógica dependiente)
        avail_cur = DB_COUNTRIES[DB_COUNTRIES["Country"] == country_sel]["Code"].unique().tolist()
        cur_opts = ["USD"] + avail_cur
        # Usamos radio horizontal (Más seguro que pills)
        currency_sel = st.radio("Currency", list(set(cur_opts)), index=0, horizontal=True)
        
        # Riesgo
        risk_sel = st.selectbox("QA Risk", DB_RISK["Level"].tolist())
        
        # Cálculos Globales
        fx_rate, tax_rate = get_country_data(country_sel, currency_sel)
        risk_row = DB_RISK[DB_RISK["Level"] == risk_sel]
        risk_val = float(risk_row["Factor"].iloc[0]) if not risk_row.empty else 0.0
        
        st.markdown("---")
        st.metric("Exchange Rate", f"{fx_rate:,.4f}")
        st.metric("Risk", f"{risk_val:.1%}")
        st.caption("LAcostWeb V21 | Safe Mode")

    # --- HEADER ---
    st.title("LAcostWeb V21 🛡️")
    
    with st.container():
        st.subheader("Header Info")
        c1, c2, c3 = st.columns(3)
        with c1:
            id_cot = st.text_input("ID Cotización", placeholder="COT-001")
            c_name = st.text_input("Customer Name", placeholder="Client Name")
        with c2:
            c_num = st.text_input("Customer Number", placeholder="ID #")
            q_date = st.date_input("Quote Date", value=date.today(), disabled=True)
        with c3:
            c_start = st.date_input("Contract Start", value=date.today())
            c_end = st.date_input("Contract End", value=date.today().replace(year=date.today().year + 1))

    st.divider()

    # --- SERVICES ---
    st.subheader("Services Lines")

    grand_total_price = 0.0
    summary_lines = []
    offering_list = DB_OFFERINGS["Offering"].tolist()

    for i, line in enumerate(st.session_state.lines):
        # Nombre para el título del expander
        curr_offering = line.get("offering_name", "New Item")
        
        with st.expander(f"🔹 {i+1}. {curr_offering}", expanded=True):
            
            # FILA 1: Catálogo y Datos ReadOnly
            r1_c1, r1_c2, r1_c3, r1_c4 = st.columns([3, 1, 1, 0.5])
            
            with r1_c1:
                # Recuperar índice de forma segura
                try: default_idx = offering_list.index(curr_offering)
                except: default_idx = 0
                
                sel_off = st.selectbox("Offering", offering_list, index=default_idx, key=f"off_{i}", label_visibility="collapsed")
                st.session_state.lines[i]["offering_name"] = sel_off
                
                # Buscar datos asociados
                off_data = DB_OFFERINGS[DB_OFFERINGS["Offering"] == sel_off].iloc[0]
                
            with r1_c2: st.text_input("L40", value=off_data["L40"], disabled=True, key=f"l40_{i}")
            with r1_c3: st.text_input("Conga", value=off_data["Conga"], disabled=True, key=f"cng_{i}")
            with r1_c4: 
                if st.button("🗑️", key=f"del_{i}"):
                    remove_line(i)
                    st.rerun()

            # FILA 2: Inputs y Duración
            r2_c1, r2_c2, r2_c3, r2_c_dur, r2_c4 = st.columns([2, 1, 1, 0.5, 0.5])
            
            with r2_c1: desc = st.text_input("Description", key=f"desc_{i}")
            
            with r2_c2: 
                s_s = st.date_input("Start", value=line.get("svc_start", date.today()), key=f"ss_{i}")
                st.session_state.lines[i]["svc_start"] = s_s
            with r2_c3: 
                s_e = st.date_input("End", value=line.get("svc_end", date.today().replace(year=date.today().year + 1)), key=f"se_{i}")
                st.session_state.lines[i]["svc_end"] = s_e
            
            dur = calc_months(s_s, s_e)
            with r2_c_dur:
                # Forzamos actualización visual
                st.session_state[f"dur_disp_{i}"] = str(dur)
                st.text_input("Mth", disabled=True, key=f"dur_disp_{i}")
                
            with r2_c4: 
                qty = st.number_input("Qty", min_value=1, value=line.get("qty", 1), key=f"qty_{i}")
                st.session_state.lines[i]["qty"] = qty

            # FILA 3: Costos y Totales
            r3_c1, r3_c2, r3_c3, r3_c4 = st.columns([1, 1, 0.8, 1.2])
            
            with r3_c1:
                cost_txt = st.text_input("Unit Cost USD", value=str(line.get("unit_cost", 0.0)), key=f"uc_{i}")
                unit_cost = safe_float(cost_txt)
                st.session_state.lines[i]["unit_cost"] = unit_cost
                
            with r3_c2:
                # Campo calculado Unit Local (Solo visual)
                local_val = unit_cost * fx_rate if currency_sel != "USD" else unit_cost
                st.text_input("Unit Local (Est)", value=f"{local_val:,.0f}", disabled=True, key=f"ucl_{i}")
                
            with r3_c3:
                gp_txt = st.text_input("GP %", value=str(line.get("gp_percent", 40.0)), key=f"gp_{i}")
                gp_val = safe_float(gp_txt)
                st.session_state.lines[i]["gp_percent"] = gp_val
                gp_factor = gp_val / 100.0

            # CÁLCULO FINAL V3 (Con Taxes)
            total_cost_base = unit_cost * qty * dur
            
            if currency_sel != "USD":
                total_cost_final = total_cost_base * fx_rate
            else:
                total_cost_final = total_cost_base
                
            divisor = 1 - gp_factor
            if divisor <= 0: divisor = 0.01 # Evitar div/0
                
            base_price = (total_cost_final * (1 + risk_val)) / divisor
            final_line_price = base_price * (1 + tax_rate)
            
            grand_total_price += final_line_price
            
            summary_lines.append({"Service": sel_off, "Price": final_line_price})

            with r3_c4:
                st.markdown(f"""
                <div style="background-color: #e0eaff; padding: 6px; border-radius: 5px; text-align: center; border: 1px solid #0F62FE; margin-top: 1px;">
                    <small>TOTAL (Inc Tax)</small><br>
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
            subject = f"Quote {id_cot}: {c_name} - {currency_sel} ${grand_total_price:,.2f}"
            body = f"Customer: {c_name}\nID: {id_cot}\nTotal: {grand_total_price:,.2f}"
            link = f"mailto:andresma@co.ibm.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            st.markdown(f'<meta http-equiv="refresh" content="0;url={link}">', unsafe_allow_html=True)

except Exception as e:
    st.error("⚠️ Ocurrió un error en la aplicación.")
    st.error(f"Detalle técnico: {str(e)}")
    st.code(traceback.format_exc())