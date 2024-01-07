from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Lista de ativos utilizados
lista = list(pd.read_excel('listativos.xls')['Código'].values)
lista.sort()
lista_ativos = [ativo + '.SA' for ativo in lista]
lista_indices_select = ['BOVESPA', 'OURO', 'DOW JONES', 'S&P 500', 'NASDAQ']

# Definir intervalo de datas
data_inicio = datetime.today() - timedelta(30)
data_final = datetime.today()

# Criar sidebar vazio
st.sidebar.empty()
st.sidebar.header("Insira os dados")

# Selecionar os ativos e período
selected_ativos = st.sidebar.multiselect("Selecione os ativos", lista)
de_data = st.sidebar.date_input("De:", data_inicio)
para_data = st.sidebar.date_input("Para:", data_final)
para_data_correta = para_data + timedelta(1)

# Condição para evitar conflito de datas

if de_data > para_data:
    st.sidebar.warning("A data de inicio não pode ser superior a data atual")

# Coletar dados para os ativos selecionados
dados_ativos = {}
for ativo in selected_ativos:
    call_api = yf.Ticker(f"{ativo}.SA").history(start=f"{de_data}", end=f"{para_data_correta}")
    dados_ativos[ativo] = pd.DataFrame(call_api)
    
# Formatar coluna de datas
for ativo, df in dados_ativos.items():
    df.index = df.index.strftime('%Y-%m-%d')

# Elaborando o dash
st.title("Monitoramento de Análise Financeira")
st.subheader("Comparação de cotação - Visualização gráfica")

# Plotando o gráfico de cotações
fig_cotacoes, ax_cotacoes = plt.subplots(figsize=(12, 6))

for ativo, df in dados_ativos.items():
    ax_cotacoes.plot(df.index, df['Close'], label=ativo)

# Adicionando legenda e título
plt.legend()
plt.title("Comparação de Cotações de Ativos")
plt.xlabel('Data')
plt.ylabel('Preço de Fechamento')

# Exibindo o gráfico de cotações
st.pyplot(fig_cotacoes)

# Plotando o gráfico de retornos
st.subheader("Comparação de rendimento - Visualização gráfica")
fig_retornos, ax_retornos = plt.subplots(figsize=(12, 6))
dados_retornos_completo = {}

for ativo, df in dados_ativos.items():
    # Calcular os retornos para cada ativo
    df_retornos = (df['Close'].pct_change() + 1).cumprod() - 1
    dados_retornos_completo[ativo] = df_retornos  
    ax_retornos.plot(df_retornos.index, df_retornos, label=f"{ativo}")

# Adicionando legenda e título
plt.legend()
plt.title("Comparação de Rendimento de Ativos")
plt.xlabel('Data')
plt.ylabel('Rendimento')

# Exibindo o gráfico de retornos
st.pyplot(fig_retornos)

# Definir cores de rendimento positivo ou negativo
color_positive = 'green'
color_negative = 'red'

# Exibindo a tabela com os dados
st.subheader("Dados dos Ativos")
for ativo, df in dados_ativos.items():
    st.write(f"Dados para {ativo}")
    st.dataframe(df, width=850, height=350)
    last_data = df.iloc[-1]
    rendimento_total = df_retornos.iloc[-1] if len(df) > 1 else 0

    st.write(f"**Alta do último dia disponível:** R$ {last_data['High']:.2f}")
    st.write(f"**Baixa do último dia disponível:** R$ {last_data['Low']:.2f}")
    st.write(f"**Fechamento do último dia disponível:** R$ {last_data['Close']:.2f}")
    
    st.write("\n---\n")

if rendimento_total < 0:
    st.sidebar.write(f"**Rendimento:** <span style='color:{color_negative}'>{rendimento_total:.2%}</span>", unsafe_allow_html=True)
else:
    st.sidebar.write(f"**Rendimento:** <span style='color:{color_positive}'>{rendimento_total:.2%}</span>", unsafe_allow_html=True)
