import pandas as pd
import numpy as np
import streamlit as st
from src.page.etapa1 import render_etapa01
from src.page.etapa2 import render_etapa02
from src.page.etapa3 import render_etapa03


st.set_page_config(
    page_title="Preparação PDI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

menu = [
"Etapa 01 - Carregar dados do Cliente",
"Etapa 02 - Verificar serviços lançados no DATASUL",
"Etapa 03 - Verificar Estoque"
]

st.sidebar.image(
"logo/Logo_PDI-on-Track-02.png",
use_column_width=True
)

page = st.sidebar.radio(
    "Navegação",
    menu,
    key="menu_principal"
)

# ALTERAÇÕES DAS PAGINAS
if page == menu[0]:
    render_etapa01()
elif page == menu[1]:
    render_etapa02()
elif page == menu[2]:
    render_etapa03()
    







    


