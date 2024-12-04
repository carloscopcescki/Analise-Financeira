from functions import *
from fundamentals import Fundamental
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

stock_dashboard = Page()
stock_dashboard.webpage()

# Definindo tipos e índices
markets = ['Ações', 'Fundos Imobiliários']

indices = {
        'BOVESPA': '^BVSP',
        'IBRX 50': '^IBV50',
        'DÓLAR': 'BRL=X',
        'EURO': 'EURBRL=X',
        'S&P 500': '^GSPC',
        'DOW JONES': '^DJI',
        'NASDAQ': '^IXIC',
}

# Tipos e ativos
get_market = str(st.sidebar.selectbox("Escolha um tipo de renda variável", [''] + markets))
if get_market:
    try:     
        market = Market(get_market)
        stock_list = market.stock_list()
        stock = str(st.sidebar.selectbox("Escolha um ativo", [''] + stock_list))
        if stock:
            stock_data = market.stock_data(stock)
            fundamental_data = Fundamental(stock)
            
            img = st.image(f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/{stock}.png", width=85)
            name = fundamental_data.name()
            dy = fundamental_data.dividend_yield()
            
            st.header(name)
            
            col1, col2, col3, col4 = st.columns(4)
            
            #col1.metric(label="Cotação", value=)
             
            
            st.subheader(dy)
            
            #st.dataframe(stock_data, width=850, height=350)
            st.dataframe(fundamental_data.table(stock), width=850, height=350)
        else:
            st.warning("Selecione um ativo")
    except Exception as e:
        st.error(f"Erro ao buscar os dados: {e}")
else:
    st.warning("Selecione um tipo de renda variável")

# Definir indices
get_indice = st.sidebar.selectbox("Escolha o indice", list(indices.keys()))