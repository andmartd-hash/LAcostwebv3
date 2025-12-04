import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import io

# ==========================================
# 0. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="LAcostWeb V16 - Robust", layout="wide", page_icon="🏢")

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
# 1. BASE DE DATOS (V14)
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
    {"Offering": "Subscription for Red Hat", "L40": "6948-66J", "Location Based Services": "Location Based Services"},
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
# 2. LÓGICA MANUAL (V14)
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
        "unit_cost": 0.0, 
        "gp_percent": 40 
    })

def remove_line(index):
    st.session_state.lines.pop(index)

# ==========================================
# 3. LÓGICA PROCESAMIENTO V3 (CORREGIDO)
# ==========================================
def calcular_costo_v3(fila):
    """
    Aplica la regla:
    - Normaliza moneda (US/USD).
    - Excepción Unit Loc 10/Ecuador.
    """
    # 1. Obtener datos con seguridad (Manejo de vacíos y espacios)
    try:
        costo = pd.to_numeric(fila.get('Unit Cost', 0), errors='coerce') 
        if pd.isna(costo): costo = 0.0
        
        er = pd.to_numeric(fila.get('ER', 1), errors='coerce')
        if pd.isna(er): er = 1.0
        
        moneda = str(fila.get('Currency', '')).strip().upper()
        
        raw_loc = str(fila.get('Unit Loc', '')).strip()
        unit_loc = raw_loc.split('.')[0].upper() # Limpia "10.0" -> "10"
        
        # 2. Regla de Excepción
        es_excepcion = unit_loc in ['10', 'ECUADOR']
        
        # 3. Regla de Moneda (Acepta US y USD)
        es_dolar = moneda in ['US', 'USD']

        # 4. Cálculo
        # Si es Dólar Y NO es excepción -> Dividir por ER
        if es_dolar and not es_excepcion:
            if er == 0: return 0.0
            return costo / er
        else:
            return costo
            
    except Exception:
        return 0.0

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================

# --- SIDEBAR COMÚN ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
    st.markdown("## ⚙️ Config")
    
    country_sel = st.selectbox("Country", sorted(DB_COUNTRIES["Country"].unique()))
    
    avail_cur = DB_COUNTRIES[DB_COUNTRIES["Country"] == country_sel]["Currency_Code"].unique().tolist()
    cur_opts = list(dict.fromkeys(["USD"] + avail_cur))
    currency_sel = st.pills("Currency", cur_opts, default=cur_opts[0])
    
    risk_sel = st.selectbox("Risk Level", DB_RISK["Risk_Level"])
    risk_val = float(DB_RISK[DB_RISK["Risk_Level"] == risk_sel]["Contingency"].iloc[0])

    fx_rate, tax_rate = get_country_data(country_sel, currency_sel)

    st.markdown("---")
    if currency_sel != "USD": st.metric("FX Rate", f"{fx_rate:,.2f}")
    st.metric("Risk", f"{risk_val:.1%}")
    st.caption("LAcostWeb V16 | Robust Fix")

# --- HEADER GLOBAL ---
st.title("LAcostWeb V16 🚀")

# PESTAÑAS PARA SEPARAR MODOS
tab_manual, tab_file = st.tabs(["📝 Calculadora Manual", "📂 Procesar Archivo V3"])

# ==========================================
# PESTAÑA 1: CALCULADORA MANUAL
# ==========================================
with tab_manual:
    with st.container():
        c_cust1, c_cust2, c_date1, c_date2 = st.columns([2, 1, 1, 1])
        with c_cust1: cust_name = st.text_input("Customer Name", placeholder="Client Name")
        with c_cust2: cust_num = st.text_input("Cust. #", placeholder="ID")
        with c_date1: c_start = st.date_input("Start Date", value=date.today())
        with c_date2: c_end = st.date_input("End Date", value=date.today().replace(year=date.today().year + 1))

    st.divider()

    st.subheader("📋 Services")

    grand_total_price = 0.0
    summary_lines = []
    offer_list = DB_OFFERINGS["Offering"].tolist()

    for i, line in enumerate(st.session_state.lines):
        current_offering_name = line.get("selected_offering", "New Item")
        
        with st.expander(f"🔹 {i+1}. {current_offering_name}", expanded=True):
            r1_c1, r1_c2, r1_c3, r1_c4 = st.columns([4, 0.8, 0.8, 0.3])
            
            with r1_c1:
                try: curr_idx = offer_list.index(line.get("selected_offering", offer_list[0]))
                except: curr_idx = 0
                sel_offering = st.selectbox("Offering Name", offer_list, index=curr_idx, key=f"off_{i}", label_visibility="collapsed")
                st.session_state.lines[i]["selected_offering"] = sel_offering
                off_data = DB_OFFERINGS[DB_OFFERINGS["Offering"] == sel_offering].iloc[0]
                
            with r1_c2: st.text_input("L40", value=off_data["L40"], key=f"l40_{i}", disabled=True, label_visibility="collapsed")
            with r1_c3: st.text_input("Conga", value=off_data["Conga"], key=f"cng_{i}", disabled=True, label_visibility="collapsed")
            with r1_c4: 
                if st.button("🗑️", key=f"del_{i}"):
                    remove_line(i)
                    st.rerun()

            r2_c1, r2_c2, r2_c3, r2_c_dur, r2_c4, r2_c5, r2_c6, r2_c7 = st.columns([1.5, 0.9, 0.9, 0.5, 0.6, 0.8, 0.6, 1.2])
            
            with r2_c1: desc = st.text_input("Desc", key=f"desc_{i}", placeholder="Details...")
            with r2_c2: 
                s_s = st.date_input("Start", value=line.get("start_date", date.today()), key=f"ss_{i}")
                st.session_state.lines[i]["start_date"] = s_s 
            with r2_c3: 
                s_e = st.date_input("End", value=line.get("end_date", date.today().replace(year=date.today().year + 1)), key=f"se_{i}")
                st.session_state.lines[i]["end_date"] = s_e 
            
            dur = calculate_months(s_s, s_e)
            with r2_c_dur: st.text_input("Mth", value=str(dur), disabled=True, key=f"dur_disp_{i}")

            with r2_c4: 
                qty = st.number_input("Qty", min_value=1, value=1, key=f"qty_{i}")
                st.session_state.lines[i]["qty"] = qty
            
            with r2_c5: 
                cost_txt = st.text_input("Cost ($)", value=str(line.get("unit_cost", 0.0)), key=f"uc_{i}")
                try: unit_cost = float(cost_txt)
                except: unit_cost = 0.0
                st.session_state.lines[i]["unit_cost"] = unit_cost
            
            with r2_c6: 
                gp_txt = st.text_input("GP %", value=str(line.get("gp_percent", 40)), key=f"gp_{i}")
                try: gp_percent_val = float(gp_txt)
                except: gp_percent_val = 0.0
                st.session_state.lines[i]["gp_percent"] = gp_percent_val
                gp = gp_percent_val / 100.0

            total_cost = unit_cost * qty * dur * fx_rate
            divisor = 1 - gp
            base_price = (total_cost * (1 + risk_val)) / divisor if divisor > 0 else 0
            final_line_price = base_price * (1 + tax_rate)
            grand_total_price += final_line_price
            
            summary_lines.append({"Offering": sel_offering, "Qty": qty, "Price": final_line_price})

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

    col_sum1, col_sum2 = st.columns([3, 1])
    with col_sum1:
        if summary_lines:
            st.dataframe(pd.DataFrame(summary_lines), use_container_width=True, hide_index=True)

    with col_sum2:
        st.markdown(f"""
            <div style="text-align: right; padding-right: 10px;">
                <h5 style="margin:0; color: gray;">TOTAL ESTIMATED</h5>
                <h1 style="margin:0; color: #0F62FE; font-size: 1.8em;">${grand_total_price:,.2f}</h1>
                <p style="margin:0; font-weight: bold;">{currency_sel}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📧 Outlook Draft", type="primary", use_container_width=True):
            if not cust_name:
                st.error("Customer Name required!")
            else:
                subject = f"LAcostWeb V14: {cust_name} - Total {currency_sel} ${grand_total_price:,.2f}"
                body = f"""Customer: {cust_name} ({cust_num})\nRegion: {country_sel} | Cur: {currency_sel} | Risk: {risk_sel}\nLines:\n"""
                for l in summary_lines:
                    body += f"- {l['Offering']} (Qty: {l['Qty']}) = ${l['Price']:,.2f}\n"
                body += f"\nTOTAL: ${grand_total_price:,.2f}"
                
                link = f"mailto:andresma@co.ibm.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                st.markdown(f'<meta http-equiv="refresh" content="0;url={link}">', unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: CARGA DE ARCHIVOS V3 (ROBUST)
# ==========================================
with tab_file:
    st.header("📂 Procesamiento Masivo (Lógica V3)")
    st.info("Acepta archivos con columnas: 'Unit Cost', 'Currency' (US/USD), 'ER', 'Unit Loc'")
    
    uploaded_file = st.file_uploader("Sube tu archivo (Excel o CSV)", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            # Detección inteligente de formato y separador
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file)
                    # Si falla al leer columnas clave, intenta con punto y coma
                    if 'Unit Cost' not in df.columns and len(df.columns) < 2:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, sep=';')
                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=';')
            else:
                df = pd.read_excel(uploaded_file)
            
            # Limpieza de nombres de columnas (Quita espacios extra en encabezados)
            df.columns = [c.strip() for c in df.columns]

            # Verificación de columnas requeridas
            cols_req = ['Unit Cost', 'Currency', 'ER', 'Unit Loc']
            missing = [c for c in cols_req if c not in df.columns]

            if not missing:
                st.success(f"Archivo válido: {len(df)} filas detectadas.")
                
                if st.button("🚀 Ejecutar Cálculo V3"):
                    # Aplicar lógica
                    df['Costo Final Calculado'] = df.apply(calcular_costo_v3, axis=1)
                    
                    st.subheader("Resultado:")
                    # Muestra columnas relevantes primero
                    cols_show = ['Unit Loc', 'Currency', 'ER', 'Unit Cost', 'Costo Final Calculado']
                    # Agregar otras columnas si existen
                    cols_show += [c for c in df.columns if c not in cols_show]
                    
                    st.dataframe(df[cols_show].head(10))
                    
                    # Descargar
                    csv_buffer = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Descargar CSV Resultado",
                        data=csv_buffer,
                        file_name="V3_Procesado_Final.csv",
                        mime="text/csv"
                    )
            else:
                st.error(f"Error: Faltan estas columnas en el archivo: {missing}")
                st.write("Columnas detectadas en tu archivo:", list(df.columns))
                st.warning("Verifica que los nombres de las columnas sean exactos (Mayúsculas importan).")
                
        except Exception as e:
            st.error(f"Error crítico leyendo el archivo: {e}")
