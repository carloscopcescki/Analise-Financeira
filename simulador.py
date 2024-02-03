import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import date, datetime, timedelta

# Coletar a lista de ativos/fii's
lista = list(pd.read_excel('listativos.xls')['Código'].values)
lista.sort()
lista_ativos = [ativo + '.SA' for ativo in lista]

# Definir intervalo de datas (1 ano padrão)
data_inicio = datetime.today() - timedelta(365)
data_final = datetime.today()

# Criar sidebar vazio
st.sidebar.empty()
st.sidebar.header("Defina a data de aporte e a data limite para analisar o rendimento")

# Definir titulos

st.title("Simulador de carteira de investimentos")

# Date input de datas
inicio = st.sidebar.date_input("De:", data_inicio)
fim = st.sidebar.date_input("Para:", data_final)

# Função para simular carteira
def simulador_carteira(inicio, fim, carteira):
    if not carteira:
        st.warning("Adicione ativos à carteira antes de simular.")
        return None
    
    carteira_sa = {ativo + '.SA': valor for ativo, valor in carteira.items()}
    
    try:
        precos_cotacao = yf.download(list(carteira_sa.keys()), start=inicio, end=fim, progress=False)['Adj Close']
    except Exception as e:
        st.error(f"Erro ao baixar dados: {e}")
        return None
    
    if precos_cotacao.empty:
        st.warning("Não há dados disponíveis para o intervalo de datas selecionado.")
        return None
    
    primeiro_preco = precos_cotacao.iloc[0]
    carteira_df = pd.Series(data=carteira, index=(carteira.keys()))
    qtd_ativos = round(carteira_df / primeiro_preco, 0)
    pl = pd.DataFrame(data=(precos_cotacao.values * qtd_ativos.values), index=precos_cotacao.index, columns=list(carteira.keys()))
    pl['PL Total'] = pl.sum(axis='columns')
    
    try:
        ibov = yf.download('^BVSP', start=inicio, end=fim, progress=False)['Adj Close'].rename('IBOV')
    except Exception as e:
        st.error(f"Erro ao baixar dados do Ibovespa: {e}")
        return None
    
    dado_consolidado = pd.concat([ibov, pl], axis=1, join='inner')
    dado_consolidado_adj = dado_consolidado / dado_consolidado.iloc[0]
    st.line_chart(dado_consolidado_adj[['IBOV', 'PL Total']])
    
# Carteira de ativos
carteira = {}

ativo = st.selectbox("Selecione um ativo", lista)
preco = st.text_input("Insira o valor em R$ a ser investido")

if st.button("Adicionar Ativo") and ativo and preco:
    carteira_sa = {ativo + '.SA': valor for ativo, valor in carteira.items()}
    simulador_carteira(inicio, fim, carteira_sa)
else:
    st.warning("Preencha ambos os campos 'Ativo' e 'Preço' antes de adicionar à carteira.")