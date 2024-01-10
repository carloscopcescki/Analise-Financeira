from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from bcb import sgs

# Lista de ativos utilizados
lista = list(pd.read_excel('listativos.xls')['Código'].values)
lista.sort()
lista_ativos = [ativo + '.SA' for ativo in lista]
lista_indices_select = ['CDI', 'IPCA', 'TAXA SELIC', 'POUPANÇA', 'BOVESPA']

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

selected_indice = st.sidebar.selectbox("Selecione um indice para comparar", [''] + lista_indices_select)
#Importar dados de indices

ipca_dados = sgs.get(('ipca', 433), start=de_data, end=para_data_correta)
selic_dados = sgs.get(('selic', 11), start=de_data, end=para_data_correta)
cdi_dados = sgs.get(('cdi', 12), start=de_data, end=para_data_correta)
poupanca_dados = sgs.get(('poupanca', 25), start=de_data, end=para_data_correta)

try:
    # Tentar ler os dados 
    df_ipca = pd.DataFrame(ipca_dados)
    df_cdi = pd.DataFrame(cdi_dados)
    df_selic = pd.DataFrame(selic_dados)
    df_poupanca = pd.DataFrame(poupanca_dados)
except ValueError as e:     
    st.error(f"Erro ao ler os dados do IPCA: {e}")
    df_ipca = pd.DataFrame()
    df_cdi = pd.DataFrame()
    df_selic = pd.DataFrame()
    df_poupanca = pd.DataFrame()

df_retornos_ipca = (df_ipca['ipca'].pct_change() + 1).cumprod() - 1
df_retornos_cdi = (df_cdi['cdi'].pct_change() + 1).cumprod() - 1
df_retornos_selic = (df_selic['selic'].pct_change() + 1).cumprod() - 1
df_retornos_poupanca = (df_poupanca['poupanca'].pct_change() + 1).cumprod() - 1

# Condição para evitar conflito de datas

if de_data > para_data:
    st.sidebar.warning("A data de inicio não pode ser superior a data atual")

# Coletar dados para os ativos selecionados
mapa_indices = {
    'BOVESPA': '^BVSP',
}

dados_ativos = {}

selected_ativos.append(selected_indice)

for ativo in selected_ativos:
    if ativo in mapa_indices:
        # Se o ativo estiver no mapa_indices, use o valor mapeado diretamente
        symbol = mapa_indices[ativo]
    else:
        # Caso contrário, acrescente o sufixo ".SA"
        symbol = f"{ativo}.SA"
    
    # Chamar a API com o símbolo obtido
    call_api = yf.Ticker(symbol).history(start=f"{de_data}", end=f"{para_data_correta}")
    
    # Adicionar os dados ao dicionário
    dados_ativos[ativo] = pd.DataFrame(call_api)
    
# Formatar coluna de datas
for ativo, df in dados_ativos.items():
    # Verificar se o índice é do tipo datetime antes de formatar
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.strftime('%Y-%m-%d')

# Elaborando o dash
st.title("Monitoramento de Análise Financeira")
st.subheader("Cotação de ativos")

# Plotando o gráfico de cotações
fig_cotacoes, ax_cotacoes = plt.subplots(figsize=(12, 6))

for ativo, df in dados_ativos.items():
    # Ignorar ativos que são iguais aos índices do mapa_indices
    if ativo not in lista_indices_select:
        ax_cotacoes.plot(df.index, df['Close'], label=ativo)
# Adicionando legenda e título
plt.legend()
plt.title("Comparação de Cotações de Ativos")
plt.xlabel('Data')
plt.ylabel('Preço de Fechamento')

# Exibindo o gráfico de cotações
st.pyplot(fig_cotacoes)

# Plotando o gráfico de retornos
if selected_indice == "":
    st.warning("Selecione o índice para analisar o rendimento")
else:
    st.subheader("Rendimento de ativos")
    fig_retornos, ax_retornos = plt.subplots(figsize=(12, 6))
    dados_retornos_completo = {}
    for ativo, df in dados_ativos.items():
        # Calcular os retornos apenas se houver dados disponíveis
        if len(df) > 1:
            df_retornos = (df['Close'].pct_change() + 1).cumprod() - 1
            dados_retornos_completo[ativo] = df_retornos  
            ax_retornos.plot(pd.to_datetime(df_retornos.index), df_retornos, label=f"{ativo}")

    # Adicionando legenda e título
    if selected_indice == "IPCA":
        ax_retornos.plot(pd.to_datetime(df_ipca.index), df_retornos_ipca, label="IPCA")
    elif selected_indice == "CDI":
        ax_retornos.plot(pd.to_datetime(df_cdi.index), df_retornos_cdi, label="CDI")
    elif selected_indice == "TAXA SELIC":
        ax_retornos.plot(pd.to_datetime(df_selic.index), df_retornos_selic, label="SELIC")
    elif selected_indice == "POUPANÇA":
        ax_retornos.plot(pd.to_datetime(df_poupanca.index), df_retornos_poupanca, label="POUPANÇA")
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


# Remover o índice selecionado se estiver presente
if selected_indice in dados_ativos:
    del dados_ativos[selected_indice]

selected_ativos.append(selected_indice)

# Exibindo a tabela com os dados
st.subheader("Dados dos Ativos")
for ativo, df in dados_ativos.items():
    st.write(f"Dados para {ativo}")
    st.dataframe(df, width=850, height=350)
    last_data = df.iloc[-1]
    
    # Calcular os retornos apenas se houver dados disponíveis
    if len(df) > 1:
        df_retornos = (df['Close'].pct_change() + 1).cumprod() - 1
        rendimento_total = df_retornos.iloc[-1]
        
        st.write(f"**Alta do último dia disponível:** R$ {last_data['High']:.2f}")
        st.write(f"**Baixa do último dia disponível:** R$ {last_data['Low']:.2f}")
        st.write(f"**Fechamento do último dia disponível:** R$ {last_data['Close']:.2f}")
        if rendimento_total < 0:
            st.write(f"**Rendimento no período:** <span style='color:{color_negative}'>{rendimento_total:.2%}</span>", unsafe_allow_html=True)
        else:
            st.write(f"**Rendimento no período:** <span style='color:{color_positive}'>{rendimento_total:.2%}</span>", unsafe_allow_html=True)
    else:
        st.write("Não há dados suficientes para calcular retornos.")
    
    st.write("\n---\n")
