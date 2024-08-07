from datetime import date, datetime, timedelta
from functions import Market
import streamlit as st
from PIL import Image

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

# Definindo dashboard
icon = Image.open("img/icon-monitor.png")
st.set_page_config(
    page_title="Monitor Financeiro",
    page_icon=icon,
    layout="wide",
)

st.sidebar.title("Monitoramento de Análise Financeira")
st.sidebar.empty()
st.sidebar.header("Insira os dados")

# Tipos e ativos
get_market = st.sidebar.selectbox("Escolha um tipo de renda variável", [''] + markets)
market = Market(get_market)
stock_list = market.get_stock_list()
stock = st.sidebar.selectbox("Escolha um ativo", [''] + stock_list)

if stock == "" and get_market != "":
    st.warning("Selecione um ativo")

# Datas
of_date = st.sidebar.date_input("De:", datetime.today() - timedelta(365))
to_date = st.sidebar.date_input("Para:", datetime.today())
if of_date > to_date:
    st.sidebar.warning("A data de inicio não pode ser superior a data atual")
    
market.date_interval(of_date, to_date)

# Definir indices
get_indice = st.sidebar.selectbox("Escolha o indice", list(indices.keys()))

# Sobre
st.sidebar.write("\n---\n")
st.sidebar.info('Aplicativo simples utilizando Streamlit para realizar o'
            '\nmonitoramento de ativos financeiros, simulação de carteira'
            '\ne cálculo de juros compostos.\n'
            '\nVeja o código em: https://github.com/carloscopcescki/Analise-Financeira/tree/main')

st.sidebar.info('Veja também: https://investmentofthefuture.netlify.app')


# Coletando dados
stock = stock + '.SA'
st.dataframe(market.get_stock_data(stock), width=850, height=350)
