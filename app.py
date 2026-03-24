import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Al Ain FC - Performance Inventory", layout="wide")

# Squadre predefinite
SQUADRE = ["U14", "U15", "U16", "U17", "U19b", "U19a", "U21", "U23", "Staff"]

# Gestione Stato dei Dati (In attesa di collegamento Google Sheets)
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Prodotto', 'Giacenza', 'Unita'])
if 'log' not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=['Data_Ora', 'Prodotto', 'Quantità', 'Squadra', 'Nota'])

st.title("⚽ Al Ain FC - Inventory & Performance Log")

# --- SIDEBAR: GESTIONE PRODOTTI ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    # 1. AGGIUNGI O CARICA
    with st.expander("📥 Carico / Nuovo Prodotto"):
        with st.form("carico"):
            n = st.text_input("Nome Prodotto")
            q = st.number_input("Quantità", min_value=0)
            u = st.selectbox("Unità", ["g", "capsule", "gel", "barrette", "unità"])
            if st.form_submit_button("Registra"):
                if n:
                    if n in st.session_state.df['Prodotto'].values:
                        st.session_state.df.loc[st.session_state.df['Prodotto'] == n, 'Giacenza'] += q
                    else:
                        new_row = pd.DataFrame([[n, q, u]], columns=['Prodotto', 'Giacenza', 'Unita'])
                        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    st.rerun()

    # 2. RINOMINA O ELIMINA (Ripristinati!)
    if not st.session_state.df.empty:
        with st.expander("📝 Modifica / Elimina"):
            p_edit = st.selectbox("Seleziona Prodotto", st.session_state.df['Prodotto'].unique())
            nuovo_nome = st.text_input("Nuovo Nome (opzionale)")
            
            col1, col2 = st.columns(2)
            if col1.button("Rinomina"):
                if nuovo_nome:
                    # Aggiorna in inventario
                    st.session_state.df.loc[st.session_state.df['Prodotto'] == p_edit, 'Prodotto'] = nuovo_nome
                    # Aggiorna anche nello storico per coerenza
                    st.session_state.log.loc[st.session_state.log['Prodotto'] == p_edit, 'Prodotto'] = nuovo_nome
                    st.rerun()
            
            if col2.button("Elimina"):
                st.session_state.df = st.session_state.df[st.session_state.df['Prodotto'] != p_edit]
                st.rerun()

# --- MAIN INTERFACE ---
tab1, tab2 = st.tabs(["🚀 Distribuzione", "📜 Storico Distribuzioni"])

with tab1:
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        st.subheader("📤 Registra Consegna")
        if not st.session_state.df.empty:
            with st.form("dist"):
                p = st.selectbox("Cosa stai consegnando?", st.session_state.df['Prodotto'].unique())
                qd = st.number_input("Quantità", min_value=1)
                sq = st.selectbox("A quale squadra?", SQUADRE)
                nt = st.text_input("Note (es. Pre-partita, Recupero)")
                if st.form_submit_button("Conferma Distribuzione"):
                    idx = st.session_state.df[st.session_state.df['Prodotto'] == p].index[0]
                    if st.session_state.df.at[idx, 'Giacenza'] >= qd:
                        st.session_state.df.at[idx, 'Giacenza'] -= qd
                        new_log = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), p, qd, sq, nt]], 
                                               columns=['Data_Ora', 'Prodotto', 'Quantità', 'Squadra', 'Nota'])
                        st.session_state.log = pd.concat([st.session_state.log, new_log], ignore_index=True)
                        st.success(f"Consegnato {qd} {p} alla {sq}!")
                        st.rerun()
                    else:
                        st.error("Giacenza insufficiente!")
        else:
            st.info("Carica dei prodotti dalla barra laterale per iniziare.")

    with col_b:
        st.subheader("📊 Stato Magazzino")
        st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("📜 Registro Cronologico")
    if not st.session_state.log.empty:
        st.dataframe(st.session_state.log.iloc[::-1], use_container_width=True, hide_index=True)
        # Tasto per scaricare i dati per la tua ricerca PhD
        csv = st.session_state.log.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Report per Analisi PhD", csv, "report_performance_alain.csv", "text/csv")
    else:
        st.write("Nessuna distribuzione registrata finora.")
