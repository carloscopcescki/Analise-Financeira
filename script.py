from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import fundamentus
from bs4 import BeautifulSoup
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid

# Habilitar o css
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Lista de ativos utilizados
lista = list(pd.read_excel('listativos.xls')['Código'].values)
lista.sort()
lista_ativos = [ativo + '.SA' for ativo in lista]

mapa_indices = {
    'BOVESPA': '^BVSP',
    'DÓLAR': 'BRL=X',
    'EURO': 'EURBRL=X',
    'S&P 500': '^GSPC',
    'DOW JONES': '^DJI',
    'NASDAQ': '^IXIC',
}

# Definir intervalo de datas (1 ano)
data_inicio = datetime.today() - timedelta(365)
data_final = datetime.today()

# Criar sidebar vazio
st.sidebar.empty()
st.sidebar.title("Insira os dados")

# Selecionar os ativos e período
ativo = st.sidebar.selectbox("Escolha um ativo", [''] + lista)
de_data = st.sidebar.date_input("De:", data_inicio)
para_data = st.sidebar.date_input("Para:", data_final)
para_data_correta = para_data + timedelta(1)

data_intervalo = (para_data - de_data).total_seconds() / 86400

selected_indice = st.sidebar.selectbox("Selecione um indice para comparar", [''] + list(mapa_indices.keys()))

# Sobre
st.sidebar.write("\n---\n")
st.sidebar.title("Sobre")
st.sidebar.info('Aplicativo simples utilizando Streamlit para realizar o'
                '\nmonitoramento de ativos financeiros, simulação de carteira'
                '\ne cálculo de juros compostos.\n'
                '\nVeja o código em: https://github.com/carloscopcescki/analise-financeira/blob/main/script.py')

# Simulador de carteira
st.sidebar.write("\n---\n")
st.sidebar.link_button(f"Simulador de Carteira", f"https://simulador-carteira.streamlit.app/")

# Calculadora de Juros Compostos
st.sidebar.link_button(f"Calculadora de Juros Compostos", f"https://calculadora-juros-compostos.streamlit.app/")

# Condição para evitar conflito de datas

if de_data > para_data:
    st.sidebar.warning("A data de inicio não pode ser superior a data atual")

# Coletar dados para os ativos selecionados

dados_ativos = {}

if ativo in mapa_indices:
    # Se o ativo estiver no mapa_indices, use o valor mapeado diretamente
    symbol = mapa_indices[ativo]
else:
    # Caso contrário, acrescente o sufixo ".SA"
    symbol = f"{ativo}.SA"
    
    # Chamar a API com o símbolo obtido
    call_api = yf.Ticker(f'{symbol}').history(start=f"{de_data}", end=f"{para_data_correta}")
    
    # Adicionar os dados ao dicionário
    dados_ativos[ativo] = pd.DataFrame(call_api)

# Formatar coluna de datas
for ativo, df in dados_ativos.items():
    # Verificar se o índice é do tipo datetime antes de formatar
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.strftime('%Y-%m-%d')

# Elaborando o dash
st.title("Monitoramento de Análise Financeira")

# Definir cores de rendimento positivo ou negativo
color_positive = 'green'
color_negative = 'red'

# Remover o índice selecionado se estiver presente
if selected_indice in dados_ativos:
    del dados_ativos[selected_indice]


# Coletar proventos do ativo
# Request para coletar proventos

preco_teto_dict = {}
last_data = {}
yield_dict = {}
pl_dict = {}
pvp_dict = {}
dados_div = {}
#name_dict = {}

# Construir a URL dinâmica para cada ativo
stock_url = (f'https://www.dadosdemercado.com.br/bolsa/acoes/{ativo}/dividendos')
url_fundamentus = (f'https://investidor10.com.br/acoes/{ativo}/')
    
# Restante do código permanece o mesmo
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

response = requests.get(stock_url, headers=headers)
dados_fundamentus = requests.get(url_fundamentus, headers=headers, timeout=5).text
    
# Verificando se a requisição foi bem-sucedida
if response.status_code == 200:
    # Parseando o conteúdo HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_valuation = BeautifulSoup(dados_fundamentus, 'html.parser')
        
    # Obter dados de valuation        
    valuation = soup_valuation.find_all('div', class_='_card-body')
    
    #name = soup_valuation.find('h2').get_text()
    
    preco_lucro = valuation[2].find('span').text
    preco_vp = valuation[3].find('span').text
    dividend_yield = valuation[4].find('span').text
        
    table_valuation = pd.DataFrame(columns=['P/L', 'P/VP', 'DY','EMPRESA'])
    
    #table_valuation['EMPRESA'] = [name]
    table_valuation['P/L'] = [preco_lucro]
    table_valuation['P/VP'] = [preco_vp]
    table_valuation['DY'] = [dividend_yield]
    
    #name_dict[ativo] = name    
    yield_dict[ativo] = dividend_yield
    pvp_dict[ativo] = preco_vp 
    pl_dict[ativo] = preco_lucro
        
    # Encontrando a tabela diretamente usando pandas
    tabela = pd.read_html(str(soup), decimal=',', thousands='.')[0]
    tabela = tabela.drop(["Pagamento", "Ex"], axis=1)
    tabela.set_index('Tipo', inplace=True)

    # Convertendo a coluna "Pagamento" para o formato desejado
    tabela['Registro'] = pd.to_datetime(tabela['Registro'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

    # Criando uma nova coluna "Ano" para extrair o ano da coluna "Pagamento"
    tabela['Ano'] = pd.to_datetime(tabela['Registro']).dt.year.astype(str) 
    tabela['Ano'] = tabela['Ano'].str.replace(',', '')
        
    dados_div[ativo] = pd.DataFrame(tabela) 
        
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
    print(f"Não foi possível obter indicadores de valuation para {ativo}. Status code: {response.status_code}")

for ativo, df in dados_ativos.items():
    last_data = df.iloc[-1]
    
    # Calcular os retornos apenas se houver dados disponíveis
    if len(df) > 1:
        
        df_retornos = (df['Close'].pct_change() + 1).cumprod() - 1
        rendimento_total = df_retornos.iloc[-1]
        
        rendimento_diario = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        colimg, colname = st.columns(2)
        
        with colimg:
            st.image(f'https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{ativo}.png', width=85)
        
        #with colname:
            #st.subheader(f'{name_dict[ativo]}')
        
        st.subheader(f'{ativo}')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.write("**Cotação:**")
            st.write(f"R$ {last_data['Close']:.2f}")
        with col2:
            if rendimento_total < 0:
                st.write("**Rendimento**")
                st.write(f"<span style='color:{color_negative}'>{rendimento_total:.2%}</span>", unsafe_allow_html=True)
            else:
                st.write("**Rendimento**")
                st.write(f"<span style='color:{color_positive}'>{rendimento_total:.2%}</span>", unsafe_allow_html=True)
        with col3:
            if ativo in pl_dict:
                st.write("**P/L**")
                st.write(f"{pl_dict[ativo]}")
            else:
                st.write("**P/L**")
                st.write("N/A")
        with col4:
            if ativo in pvp_dict:
                st.write("**P/VP**")
                st.write(f"{pvp_dict[ativo]}")
            else:
                st.write("**P/VP**")
                st.write("N/A")
        with col5:
            if ativo in yield_dict:
                st.write("**DY**")
                st.write(f"{yield_dict[ativo]}")
            else:
                st.write("**DY**")
                st.write("N/A")
        with col6:
            if ativo in preco_teto_dict:
                st.write("**Preço Teto**")
                st.write(f"R$ {preco_teto_dict[ativo]:.2f}")
            else:
                st.write("**Preço Teto**")
                st.write("N/A")
        
    else:
        st.write("Não há dados suficientes para calcular retornos.")
        
    with st.expander("Histórico de dividendos:"):
        if ativo in dados_div:
            st.dataframe(tabela, width=850, height=350)
            tabela = dados_div[ativo]
        else:
            st.warning("Não foi possível obter a tabela de proventos")
        
    if ativo in pvp_dict:
        st.link_button(f"Veja mais sobre {ativo}", f"https://investidor10.com.br/acoes/{ativo}/")
    else:
        st.link_button(f"Veja mais sobre {ativo}", f"https://investidor10.com.br/fiis/{ativo}/")
        
    st.write("\n---\n")


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

        plt.legend()
        plt.title("Comparação de Rendimento de Ativos")
        plt.xlabel('Data')
        plt.ylabel('Rendimento')
    # Exibindo o gráfico de retornos
        ax_retornos.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        st.pyplot(fig_retornos)
    
    st.write("\n---\n")