import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
# Incolla qui l'URL del tuo foglio Google (quello che finisce con /edit)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1eef9gbTdX9RczfzuLSv7PBIwL5Ie-wd2UjvEYMkjyLg/edit"

def get_csv_url(url, sheet_name):
    base_url = url.replace('/edit', '/gviz/tq?tqx=out:csv&sheet=')
    return f"{base_url}{sheet_name}"

st.set_page_config(page_title="Al Ain FC Performance", layout="wide")

# Caricamento dati (Sincronizzato con il Cloud)
try:
    df = pd.read_csv(get_csv_url(SHEET_URL, "Inventario"))
    log_df = pd.read_csv(get_csv_url(SHEET_URL, "Storico"))
except:
    st.error("Errore di connessione al foglio Google. Verifica che sia 'Pubblico - Editor'.")
    st.stop()

st.title("⚽ Al Ain FC - Cloud Inventory")

# --- SIDEBAR: AGGIUNTA PRODOTTI ---
with st.sidebar:
    st.header("📦 Magazzino")
    with st.form("new_prod"):
        n = st.text_input("Nome Prodotto")
        q = st.number_input("Quantità", min_value=0)
        u = st.selectbox("Unità", ["g", "capsule", "gel", "barrette", "unità"])
        if st.form_submit_button("Aggiungi a Cloud"):
            if n:
                if n in df['Prodotto'].values:
                    df.loc[df['Prodotto'] == n, 'Giacenza'] += q
                else:
                    new_row = pd.DataFrame([[n, q, u]], columns=['Prodotto', 'Giacenza', 'Unita'])
                    df = pd.concat([df, new_row], ignore_index=True)
                st.info("⚠️ Per salvare permanentemente su Google Sheets, usa il tasto 'Sincronizza Cloud' in fondo allo storico.")
                st.rerun()

# --- MAIN ---
t1, t2 = st.tabs(["🚀 Distribuzione", "📊 Storico & Sincronizzazione"])

with t1:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("Consegna Integratori")
        with st.form("delivery"):
            p = st.selectbox("Prodotto", df['Prodotto'].unique())
            qd = st.number_input("Quantità", min_value=1)
            sq = st.selectbox("Squadra", ["U14", "U15", "U16", "U17", "U19b", "U19a", "U21", "U23", "Staff"])
            if st.form_submit_button("REGISTRA"):
                idx = df[df['Prodotto'] == p].index[0]
                if df.at[idx, 'Giacenza'] >= qd:
                    df.at[idx, 'Giacenza'] -= qd
                    new_log = pd.DataFrame([[datetime.now().strftime("%d/%m %H:%M"), p, qd, sq]], 
                                           columns=['Data_Ora', 'Prodotto', 'Quantità', 'Squadra'])
                    log_df = pd.concat([log_df, new_log], ignore_index=True)
                    st.success("Registrato! Ricordati di sincronizzare nel Tab Storico.")
                else:
                    st.error("Giacenza insufficiente!")

    with col2:
        st.dataframe(df, use_container_width=True, hide_index=True)

with t2:
    st.subheader("Storico Online")
    st.dataframe(log_df.iloc[::-1], use_container_width=True, hide_index=True)
    
    st.divider()
    st.write("### ☁️ Persistenza Dati")
    st.write("I dati vengono salvati online su Google Sheets.")
    # Link diretto per l'analisi PhD
    st.link_button("Vai al database Excel (Google Sheets)", SHEET_URL)
