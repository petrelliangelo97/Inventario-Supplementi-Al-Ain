import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Al Ain FC - Performance Inventory", layout="wide")

# Squadre predefinite
SQUADRE = ["U14", "U15", "U16", "U17", "U19b", "U19a", "U21", "U23", "Staff"]

# Funzione per caricare dati (D'ora in poi useremo i file del sito)
@st.cache_data
def load_initial_data():
    return pd.DataFrame(columns=['Prodotto', 'Giacenza', 'Unita'])

if 'df' not in st.session_state:
    st.session_state.df = load_initial_data()
if 'log' not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=['Data_Ora', 'Prodotto', 'Quantità', 'Squadra', 'Nota'])

st.title("⚽ Al Ain FC - Inventory & Performance Log")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Gestione")
    with st.expander("📥 Carico Prodotti"):
        with st.form("carico"):
            n = st.text_input("Nome Prodotto")
            q = st.number_input("Quantità", min_value=0)
            u = st.selectbox("Unità", ["g", "capsule", "gel", "barrette", "unità"])
            if st.form_submit_button("Aggiungi"):
                if n in st.session_state.df['Prodotto'].values:
                    st.session_state.df.loc[st.session_state.df['Prodotto'] == n, 'Giacenza'] += q
                else:
                    new_row = pd.DataFrame([[n, q, u]], columns=['Prodotto', 'Giacenza', 'Unita'])
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.rerun()

# --- MAIN ---
t1, t2 = st.tabs(["🚀 Distribuzione", "📜 Storico"])

with t1:
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        if not st.session_state.df.empty:
            with st.form("dist"):
                p = st.selectbox("Prodotto", st.session_state.df['Prodotto'].unique())
                qd = st.number_input("Quantità", min_value=1)
                sq = st.selectbox("Squadra", SQUADRE)
                nt = st.text_input("Note")
                if st.form_submit_button("Registra"):
                    idx = st.session_state.df[st.session_state.df['Prodotto'] == p].index[0]
                    if st.session_state.df.at[idx, 'Giacenza'] >= qd:
                        st.session_state.df.at[idx, 'Giacenza'] -= qd
                        new_log = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), p, qd, sq, nt]], 
                                               columns=['Data_Ora', 'Prodotto', 'Quantità', 'Squadra', 'Nota'])
                        st.session_state.log = pd.concat([st.session_state.log, new_log], ignore_index=True)
                        st.success("Registrato!")
                        st.rerun()
    with col_b:
        st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)

with t2:
    st.dataframe(st.session_state.log.iloc[::-1], use_container_width=True, hide_index=True)
