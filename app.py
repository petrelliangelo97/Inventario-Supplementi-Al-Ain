import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Al Ain FC - Permanent Inventory", layout="wide")

# Connessione al database permanente (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    inv = conn.read(worksheet="Inventario")
    log = conn.read(worksheet="Storico")
    return inv.dropna(how="all"), log.dropna(how="all")

df, log_df = get_data()
SQUADRE = ["U14", "U15", "U16", "U17", "U19b", "U19a", "U21", "U23", "Staff"]

st.title("⚽ Al Ain FC - Database Permanente")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Gestione")
    with st.expander("📥 Carico Prodotti"):
        with st.form("carico"):
            n = st.text_input("Nome Prodotto")
            q = st.number_input("Quantità", min_value=0)
            u = st.selectbox("Unità", ["g", "capsule", "gel", "barrette", "unità"])
            if st.form_submit_button("Registra"):
                if n in df['Prodotto'].values:
                    df.loc[df['Prodotto'] == n, 'Giacenza'] += q
                else:
                    new_row = pd.DataFrame([[n, q, u]], columns=['Prodotto', 'Giacenza', 'Unita'])
                    df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="Inventario", data=df)
                st.success("Inventario Aggiornato!")
                st.rerun()

    if not df.empty:
        if st.sidebar.button("Elimina Prodotto Selezionato"):
            # Aggiungeremo logica di selezione qui se serve
            pass

# --- INTERFACCIA ---
t1, t2 = st.tabs(["🚀 Distribuzione", "📜 Storico"])

with t1:
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        if not df.empty:
            with st.form("dist"):
                p = st.selectbox("Prodotto", df['Prodotto'].unique())
                qd = st.number_input("Quantità", min_value=1)
                sq = st.selectbox("Squadra", SQUADRE)
                if st.form_submit_button("Conferma"):
                    idx = df[df['Prodotto'] == p].index[0]
                    if df.at[idx, 'Giacenza'] >= qd:
                        df.at[idx, 'Giacenza'] -= qd
                        new_log = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), p, qd, sq, ""]], 
                                               columns=['Data_Ora', 'Prodotto', 'Quantità', 'Squadra', 'Nota'])
                        log_df = pd.concat([log_df, new_log], ignore_index=True)
                        conn.update(worksheet="Inventario", data=df)
                        conn.update(worksheet="Storico", data=log_df)
                        st.rerun()
    with col_b:
        st.subheader("Giacenze Reali")
        st.dataframe(df, use_container_width=True, hide_index=True)

with t2:
    st.subheader("Registro su Google Sheets")
    st.dataframe(log_df.iloc[::-1], use_container_width=True, hide_index=True)
