from functions import *
from fundamentals import FII_Data, Fundamental
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
if get_market == "Ações":
    try:
        market = Market(get_market)
        stock_list = market.stock_list()
        stock = str(st.sidebar.selectbox("Escolha um ativo",
                                         [''] + stock_list))
        if stock:
            fundamental_data = Fundamental(stock)
            ticker = fundamental_data.ticker()
            col_img, col_name = st.columns(2)

            with col_img:
                if fundamental_data.ticker() == "ISAE4" or fundamental_data.ticker() == "ISAE3":
                    img = st.image(f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/TRPL4.png",
                                  width=120)
                else:
                    img = st.image(
                        f"https://raw.githubusercontent.com/thecartera/B3-Assets-Images/refs/heads/main/imgs/{stock}.png",
                        width=120)
            with col_name:
                st.header(fundamental_data.name())

            st.markdown(f"**Código de negociação:** {fundamental_data.ticker()}")
            st.markdown(f"**Setor:** {fundamental_data.sector()}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                col1.metric(label="Valor da cotação", value=f"R$ {fundamental_data.price()}", delta=f"{fundamental_data.variation()}")
                st.link_button(f"Dados de {stock}", url=f"https://investidor10.com.br/acoes/{stock}/")
                st.link_button(f"Notícias sobre {stock}", url=f"https://investidor10.com.br/noticias/ativo/{stock}/")
            with col2:
                col2.metric(label="Dividend Yield", value=fundamental_data.dividend_yield())
            with col3:
                col3.metric(label="PL", value=fundamental_data.pl())
            with col4:
                col4.metric(label="PVP", value=fundamental_data.pvp())

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
                st.metric(label="P/L", value=fundamental_data.pl())
                st.metric(label="Margem Bruta", value=fundamental_data.marg_bruta())
                st.metric(label="ROIC", value=fundamental_data.roic())
            with col1b:
                st.metric(label="P/VP", value=fundamental_data.pvp())
                st.metric(label="Margem Ebit", value=fundamental_data.marg_ebit())
                st.metric(label="ROE", value=fundamental_data.roe())
            with col1c:
                st.metric(label="P/Receita (PSR)", value=fundamental_data.psr())
                st.metric(label="Margem Líquida", value=fundamental_data.marg_liquida())
            with col1d:
                st.metric(label="Dividend Yield", value=fundamental_data.dividend_yield())
                st.metric(label="Dívida Bruta Patrimônial", value=fundamental_data.div_bruta_patrim())
            with col1e:
                st.metric(label="EV/EBIT", value=fundamental_data.ev_ebit())
                st.metric(label="VPA", value=fundamental_data.vpa())
            with col1f:
                st.metric(label="EV/EBITDA", value=fundamental_data.ev_ebitda())
                st.metric(label="LPA", value=fundamental_data.lpa())

            st.header(f"Informações sobre {fundamental_data.ticker()}", divider="grey")

            colInfo1, colInfo2, colInfo3 = st.columns(3)
            with colInfo1:
                st.metric(label="Valor de mercado", value=f"R$ {fundamental_data.market_value()}")
                st.metric(label="N° de cotas", value=fundamental_data.ticker_quantity())
                st.metric(label="Dívida Bruta", value=f"R$ {fundamental_data.debt_brut()}")
            with colInfo2:
                st.metric(label="Valor de firma", value=f"R$ {fundamental_data.enterprise_value()}")
                st.metric(label="Ativos", value=f"R$ {fundamental_data.ativos()}")
                st.metric(label="Dívida Líquida", value=f"R$ {fundamental_data.debt_liq()}")
            with colInfo3:
                st.metric(label="Patrimônio Líquido", value=f"R$ {fundamental_data.ticker_patrim()}")
                st.metric(label="Ativo Circulante", value=f"R$ {fundamental_data.ativos_circulantes()}")
                st.metric(label="Disponibilidades", value=f"R$ {fundamental_data.ticker_disp()}")

            #st.dataframe(stock_data, width=850, height=350)
            #st.dataframe(fundamental_data.table(stock), width=850, height=350)    
        else:
            st.warning("Selecione um ativo")
    except Exception as e:
        st.error(f"Erro ao buscar os dados: {e}")

if get_market == "Fundos Imobiliários":
    try:
        market = Market(get_market)
        stock_list = market.stock_list()
        stock = str(st.sidebar.selectbox("Escolha um ativo",
                                         [''] + stock_list))
        if stock:
            fundamental_data = FII_Data(stock)
            ticker = fundamental_data.fii_ticker()
            col_img, col_name = st.columns(2)
            with col_img:
                img = st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRz2D2twD0bV62AwgI4vG6NXPrgt-rmw86XA&s", width=120)
            with col_name:
                st.header(fundamental_data.fii_name())
            st.markdown(f"**Código de negociação:** {fundamental_data.fii_ticker()}")
            st.markdown(f"**Setor:** {fundamental_data.fii_type()}")
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Valor da cotação", value=f"R$ {fundamental_data.fii_value()}", delta=f"{fundamental_data.fii_variation()}")
            st.link_button(f"Dados de {stock}", url=f"https://investidor10.com.br/fiis/{stock}/")
            st.link_button(f"Notícias sobre {stock}", url=f"https://investidor10.com.br/noticias/ativo/{stock}/")
            col2.metric(label="Dividend Yield", value=fundamental_data.fii_dy())
            col3.metric(label="P/VP", value=fundamental_data.fii_pvp())

            style_metric_cards(border_left_color='#292D34',
                   border_color='#292D34')

            st.header(f"Dividendos {stock}", divider="grey")
            market.fii_dividends(stock)

            colDividendChart, colDividendTable = st.columns(2)
            with colDividendChart:
                market.fii_dividends_chart(stock)
            with colDividendTable:
                market.fii_dividends_table()
        else:
            st.warning("Selecione um tipo de renda variável")
    except Exception as e:
        st.error(f"Erro ao buscar os dados: {e}")
    
# Definir indices
#get_indice = st.sidebar.selectbox("Escolha o indice", list(indices.keys()))
