from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from bs4 import BeautifulSoup
from bcb import sgs

# Lista de ativos utilizados
lista = list(pd.read_excel('listativos.xls')['Código'].values)
lista.sort()
lista_ativos = [ativo + '.SA' for ativo in lista]
lista_indices_select = ['CDI', 'IPCA', 'SELIC', 'POUPANÇA', 'BOVESPA', 'DÓLAR','EURO','S&P 500', 'DOW JONES', 'NASDAQ']

# Definir intervalo de datas (1 ano)
data_inicio = datetime.today() - timedelta(365)
data_final = datetime.today()

# Criar sidebar vazio
st.sidebar.empty()
st.sidebar.header("Insira os dados")

# Selecionar os ativos e período
selected_ativos = st.sidebar.multiselect("Selecione os ativos", lista)
de_data = st.sidebar.date_input("De:", data_inicio)
para_data = st.sidebar.date_input("Para:", data_final)
para_data_correta = para_data + timedelta(1)

data_intervalo = (para_data - de_data).total_seconds() / 86400

selected_indice = st.sidebar.selectbox("Selecione um indice para comparar", [''] + lista_indices_select)

# Simulador de carteira
st.sidebar.write("\n---\n")
st.sidebar.header("Simulador de carteira")
st.sidebar.link_button(f"Simular", f"https://simulador-carteira.streamlit.app/")

#Importar dados de indices
ipca_dados = sgs.get(('ipca', 7478), start=de_data, end=para_data_correta)
selic_dados = sgs.get(('selic', 11), start=de_data, end=para_data_correta)
cdi_dados = sgs.get(('cdi', 4390), start=de_data, end=para_data_correta)
poupanca_dados = sgs.get(('poupanca', 25), start=de_data, end=para_data_correta)

try:
    # Tentar ler os dados 
    df_ipca = pd.DataFrame(ipca_dados)
    df_cdi = pd.DataFrame(cdi_dados)
    df_selic = pd.DataFrame(selic_dados)
    df_poupanca = pd.DataFrame(poupanca_dados)
except ValueError as e:     
    df_ipca = pd.DataFrame()
    df_cdi = pd.DataFrame()
    df_selic = pd.DataFrame()
    df_poupanca = pd.DataFrame()

    st.warning("Houve um erro no carregamento de dados, recarregue a página ou insira um novo ativo/fii")

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
    'DÓLAR': 'BRL=X',
    'EURO': 'EURBRL=X',
    'S&P 500': '^GSPC',
    'DOW JONES': '^DJI',
    'NASDAQ': '^IXIC',
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
    
    # Obter o dividend yield
    if len(call_api) > 1:
        valor_ativo = call_api['Close'].iloc[-1]

    somatoria_por_ano = somatoria_dy.tail(2)
    somatoria_por_ano = somatoria_por_ano.iloc[-1]
    total_provento = somatoria_por_ano['Valor'].sum()
    dividend_yield = (total_provento / valor_ativo) * 100

# Formatar coluna de datas
for ativo, df in dados_ativos.items():
    # Verificar se o índice é do tipo datetime antes de formatar
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.strftime('%Y-%m-%d')

# Elaborando o dash
st.title("Monitoramento de Análise Financeira")
st.subheader("Cotação de ativos")

with st.expander("Gráfico de cotação:"):
    # Plotando o gráfico de cotações
    st.subheader("Cotação")
    fig_cotacoes, ax_cotacoes = plt.subplots(figsize=(12, 6))

    for ativo, df in dados_ativos.items():
        # Ignorar ativos que são iguais aos índices do mapa_indices
        if ativo not in selected_indice:
            ax_cotacoes.plot(pd.to_datetime(df.index), df['Close'], label=f"{ativo}")
    # Adicionando legenda e título
    plt.legend()
    plt.title("Comparação de Cotações de Ativos")
    plt.xlabel('Data')
    plt.ylabel('Preço de Fechamento')

    # Exibindo o gráfico de cotações
    st.pyplot(fig_cotacoes)

# Plotando o gráfico de retornos
st.subheader("Rendimento de ativos")

with st.expander("Gráfico de rendimento:"):
    if selected_indice == "":
        st.warning("Selecione o índice para analisar o rendimento")
    else:
        st.subheader("Rendimento")
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
        elif selected_indice == "SELIC":
            ax_retornos.plot(pd.to_datetime(df_selic.index), df_retornos_selic, label="SELIC")
        elif selected_indice == "POUPANÇA":
            ax_retornos.plot(pd.to_datetime(df_poupanca.index), df_retornos_poupanca, label="POUPANÇA")
            # Adicionando legenda e título
        plt.legend()
        plt.title("Comparação de Rendimento de Ativos")
        plt.xlabel('Data')
        plt.ylabel('Rendimento')
       # Exibindo o gráfico de retornos
        ax_retornos.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        st.pyplot(fig_retornos)

st.write("\n---\n")

# Definir cores de rendimento positivo ou negativo
color_positive = 'green'
color_negative = 'red'


# Remover o índice selecionado se estiver presente
if selected_indice in dados_ativos:
    del dados_ativos[selected_indice]

selected_ativos.append(selected_indice)

# Coletar proventos do ativo
# Request para coletar proventos

preco_teto_dict = {}
last_data = {}

for ativo in selected_ativos:
    
    # Construir a URL dinâmica para cada ativo
    stock_url = f'https://www.dadosdemercado.com.br/bolsa/acoes/{ativo}/dividendos'

    # Restante do código permanece o mesmo
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    response = requests.get(stock_url, headers=headers)

    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Parseando o conteúdo HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrando a tabela diretamente usando pandas
        tabela = pd.read_html(str(soup), decimal=',', thousands='.')[0]
        tabela = tabela.drop(["Pagamento", "Ex"], axis=1)

        # Convertendo a coluna "Pagamento" para o formato desejado
        tabela['Registro'] = pd.to_datetime(tabela['Registro'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

        # Criando uma nova coluna "Ano" para extrair o ano da coluna "Pagamento"
        tabela['Ano'] = pd.to_datetime(tabela['Registro']).dt.year

        # Atualizando a variável com os dados da tabela
        somatoria_por_ano = tabela.groupby('Ano')['Valor'].sum().reset_index()

        # Mantendo apenas as últimas linhas
        somatoria_por_ano = somatoria_por_ano.tail(6)
        somatoria_por_ano = somatoria_por_ano.iloc[:-1]

        # Calcular o preco_teto para cada ativo e armazenar no dicionário
        
        media_prov = (somatoria_por_ano['Valor'].sum()) / 5
        preco_teto = (media_prov * 100) / 5
        preco_teto_dict[ativo] = preco_teto
        
    else:
        print(f"Não foi possível obter o preço teto para {ativo}. Status code: {response.status_code}")
        
for ativo, df in dados_ativos.items():
    last_data = df.iloc[-1]
    
    # Calcular os retornos apenas se houver dados disponíveis
    if len(df) > 1:
        df_retornos = (df['Close'].pct_change() + 1).cumprod() - 1
        rendimento_total = df_retornos.iloc[-1]
        
        rendimento_diario = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        st.subheader(f'{ativo}')
        
        st.write(f"**Valor do ativo:** R$ {last_data['Close']:.2f}")
        st.write(f"**Dividend Yield:** {dividend_yield:.2f}%")
        if ativo in preco_teto_dict:
            st.write(f"**Preço teto:** R$ {preco_teto_dict[ativo]:.2f}")
        else:
            st.warning(f"Não foi possível encontrar o preço teto para {ativo}.")
        if rendimento_diario < 0:
            st.write(f"**Variação do dia:** <span style='color:{color_negative}'>{rendimento_diario:.2f}%</span>", unsafe_allow_html=True)
        else:
            st.write(f"**Variação do dia:** <span style='color:{color_positive}'>+{rendimento_diario:.2f}%</span>", unsafe_allow_html=True)
        if rendimento_total < 0:
            st.write(f"**Rendimento no período:** <span style='color:{color_negative}'>{rendimento_total:.2%}</span>", unsafe_allow_html=True)
        else:
            st.write(f"**Rendimento no período:** <span style='color:{color_positive}'>{rendimento_total:.2%}</span>", unsafe_allow_html=True)
    else:
        st.write("Não há dados suficientes para calcular retornos.")
    
    with st.expander("Histórico do ativo no período:"):
        st.dataframe(df, width=850, height=350)
        df = dados_ativos[ativo]

    st.link_button(f"Veja mais sobre {ativo}", f"https://www.fundamentus.com.br/detalhes.php?papel={ativo}")
    st.write("\n---\n")
