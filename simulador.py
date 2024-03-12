import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.ticker as mtick
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt


# Coletar a lista de ativos/fii's
lista = list(pd.read_excel('lists/listativos.xls')['Código'].values)
lista.sort()
lista_ativos = [ativo + '.SA' for ativo in lista]

# Definir intervalo de datas (1 ano padrão)
data_inicio = datetime.today() - timedelta(365)
data_final = datetime.today()

# Criar sidebar vazio
st.sidebar.empty()
st.sidebar.header("Defina a data de aporte e a data limite para analisar o rendimento")

# Definir titulos
st.title("Simulador de rentabilidade de ativo")

# Date input de datas
inicio = st.sidebar.date_input("De:", data_inicio)
fim = st.sidebar.date_input("Para:", data_final)

# Definir quantidade de ativos em carteira
st.sidebar.header("Quantidade de ativos em carteira")
qtd_ativo = st.sidebar.number_input("Insira a quantidade:", min_value=0, step=1)

# Sobre
st.sidebar.write("\n---\n")
st.sidebar.title("Sobre")
st.sidebar.info('Simulador simples para analisar o rendimento de uma carteira'
                '\nde ativos em um período selecionado.\n'
                '\n\n'
                'Veja o código em https://github.com/carloscopcescki/Analise-Financeira/blob/main/simulador.py')

# Função para simular carteira
def simulador_carteira(inicio, fim, carteira):
    if not carteira:
        st.warning("Adicione ativos à carteira antes de simular.")
        return None
    
    carteira_sa = {}
    for valor, ativo in carteira.items():
        ativo_sa = ativo + '.SA'
        carteira_sa[ativo_sa] = float(valor)  # Convertendo o valor para float
    
    try:
        precos_cotacao = yf.download(list(carteira_sa.keys()), start=inicio, end=fim, progress=False)['Adj Close']
    except Exception as e:
        st.error(f"Erro ao baixar dados: {e}")
        return None
    
    if precos_cotacao.empty:
        st.warning("Não há dados disponíveis para o intervalo de datas selecionado.")
        return None
    
    primeiro_preco = precos_cotacao.iloc[0]
    
    # Certifique-se de que todos os valores são numéricos antes de realizar a operação de divisão
    carteira_df = pd.Series(data=carteira_sa, name='Carteira')
    
    qtd_ativos = round(carteira_df / primeiro_preco, 0)
    pl = pd.DataFrame(data=(precos_cotacao.values * qtd_ativos.values), index=precos_cotacao.index, columns=list(carteira_sa.keys()))
    pl['PL Total'] = pl.sum(axis='columns')
    
    try:
        ibov = yf.download('^BVSP', start=inicio, end=fim, progress=False)['Adj Close'].rename('IBOV')
    except Exception as e:
        st.error(f"Erro ao baixar dados do Ibovespa: {e}")
        return None
    
    dado_consolidado = pd.concat([ibov, pl], axis=1, join='inner')
    dado_consolidado_adj = dado_consolidado / dado_consolidado.iloc[0]
    
    # Plotar o gráfico com Matplotlib
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.title("Carteira x Bovespa")
    ax.plot(dado_consolidado_adj[['IBOV', 'PL Total']])
    ax.set_xlabel('Data')
    ax.set_ylabel('Rendimento')
    ax.legend(['BOVESPA', 'CARTEIRA'])
    
    # Exibir o gráfico comparativo
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    st.pyplot(fig)

# Carteira de ativos
carteira = {}
contador = 0

try:
    while contador < qtd_ativo:
        ativo = st.selectbox(f"Selecione o ativo {contador + 1}", [''] + lista, key=f"select_ativo_{contador}")
        preco = st.text_input(f"Insira o valor em R$ a ser investido em {ativo}", key=f"input_preco_{contador}")

        if ativo != '' and preco != '':
            preco_float = float(preco)
            carteira[preco_float] = ativo
            contador += 1

except Exception as e:
    st.warning("Selecione o ativo e insira o valor aportado")

if qtd_ativo != 0:
    if st.button("Comparar rendimento") and carteira:
        simulador_carteira(inicio, fim, carteira)
else:
    st.warning("Informe a quantidade de ativos em sua carteira")
