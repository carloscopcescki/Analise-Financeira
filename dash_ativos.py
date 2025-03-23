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
get_market = str(
    st.sidebar.selectbox("Escolha um tipo de renda variável", [''] + markets))
if get_market:
    try:
        market = Market(get_market)
        stock_list = market.stock_list()
        stock = str(st.sidebar.selectbox("Escolha um ativo",
                                         [''] + stock_list))
        if stock:
            #stock_data = market.stock_data(stock)
            fundamental_data = Fundamental(stock)
            name = fundamental_data.name()
            ticker = fundamental_data.ticker()
            dy = fundamental_data.dividend_yield()
            price = fundamental_data.price()
            pl = fundamental_data.pl()
            pvp = fundamental_data.pvp()

            #name = market.get_ticker_name(stock)

            col_img, col_name = st.columns(2)

            with col_img:
                if ticker == "ISAE4" or ticker == "ISAE3":
                    img = st.image(f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/TRPL4.png",
                                  width=85)
                else:
                    img = st.image(
                        f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/{stock}.png",
                        width=85)
            with col_name:
                st.header(name)

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(label="Valor da cotação", value=f"R$ {price}")
            col2.metric(label="Dividend Yield", value=dy)
            col3.metric(label="PL", value=pl)
            col4.metric(label="PVP", value=pvp)

            style_metric_cards(border_left_color='#292D34',
                               border_color='#292D34')

            #st.subheader(f"Cotação {stock}")
            #market.price_chart(stock)

            st.header(f"Dividendos {stock}", divider="grey")
            market.dividends(stock)

            colDividendChart, colDividendTable = st.columns(2)
            with colDividendChart:
                market.dividends_chart(stock)
            with colDividendTable:
                market.dividends_table()

            st.header(f"Indicadores Fundamentalistas {stock}", divider="grey")

            col1a, col1b, col1c, col1d, col1e, col1f = st.columns(6)
            with col1a:
                st.metric(label="P/L", value=pl)
                st.metric(label="Margem Bruta", value=fundamental_data.marg_bruta())
                st.metric(label="ROIC", value=fundamental_data.roic())
            with col1b:
                st.metric(label="P/VP", value=pvp)
                st.metric(label="Margem Ebit", value=fundamental_data.marg_ebit())
                st.metric(label="ROE", value=fundamental_data.roe())
            with col1c:
                st.metric(label="P/Receita (PSR)", value=fundamental_data.psr())
                st.metric(label="Margem Líquida", value=fundamental_data.marg_liquida())
            with col1d:
                st.metric(label="Dividend Yield", value=dy)
                st.metric(label="Dívida Bruta Patrimônial", value=fundamental_data.div_bruta_patrim())
            with col1e:
                st.metric(label="EV/EBIT", value=fundamental_data.ev_ebit())
                st.metric(label="VPA", value=fundamental_data.vpa())
            with col1f:
                st.metric(label="EV/EBITDA", value=fundamental_data.ev_ebitda())
                st.metric(label="LPA", value=fundamental_data.lpa())
        
            #st.dataframe(stock_data, width=850, height=350)
            #st.dataframe(fundamental_data.table(stock), width=850, height=350)
        else:
            st.warning("Selecione um ativo")
    except Exception as e:
        st.error(f"Erro ao buscar os dados: {e}")
else:
    st.warning("Selecione um tipo de renda variável")

# Definir indices
#get_indice = st.sidebar.selectbox("Escolha o indice", list(indices.keys()))
