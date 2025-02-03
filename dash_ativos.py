from functions import *
from fundamentals import Fundamental
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid

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
            name = fundamental_data.name()
            dy = fundamental_data.dividend_yield()
            price = fundamental_data.price()
            pl = fundamental_data.pl()
            pvp = fundamental_data.pvp()
            
            my_grid = grid(2)
            c = my_grid.container(border=True)
            colImage, colStock = c.columns(2)
            
            with colImage:
                if stock != "ISAE4" and stock != "ISAE3":
                    img = st.image(f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/{stock}.png", width=100)
                else:
                    img = st.image(f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/TRPL4.png", width=100)
            with colStock:    
                st.header(name)
            
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric(label="Valor da cotação", value=f"R$ {price}")
            col2.metric(label="Dividend Yield", value=dy)
            col3.metric(label="P/L", value=pl)
            col4.metric(label="PVP", value=pvp)
            
            style_metric_cards(background_color="#0E1117",
                    border_left_color='#afb381',
                    border_color='#afb381')
            
            st.dataframe(stock_data, width=850, height=350)
            st.dataframe(fundamental_data.table(stock), width=850, height=350)
        else:
            st.warning("Selecione um ativo")
    except Exception as e:
        st.error(f"Erro ao buscar os dados: {e}")
else:
    st.warning("Selecione um tipo de renda variável")

# Definir indices
get_indice = st.sidebar.selectbox("Escolha o indice", list(indices.keys()))