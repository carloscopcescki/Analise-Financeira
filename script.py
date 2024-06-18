from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import fundamentus
import matplotlib.ticker as mtick
from bs4 import BeautifulSoup
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid
from PIL import Image

# Definindo o ícone e título da página
icon = Image.open("img/icon-monitor.png")
st.set_page_config(
    page_title="Monitor Financeiro",
    page_icon=icon,
    layout="wide",
)

# Definindo abas
aba1, aba2, aba3, aba4 = st.tabs(['Monitoramento Financeiro', 'Calculadora de Juros Simples', 'Calculadora de Juros Compostos', 'Simulador de Carteira'])

# Ajustando aba de monitoramento financeiro
with aba1:

    # Elaborando o monitor
    st.sidebar.title("Monitoramento de Análise Financeira")

    mapa_indices = {
        'BOVESPA': '^BVSP',
        'IBRX 50': '^IBV50',
        'DÓLAR': 'BRL=X',
        'EURO': 'EURBRL=X',
        'S&P 500': '^GSPC',
        'DOW JONES': '^DJI',
        'NASDAQ': '^IXIC',
    }

    tipo_invest = ['Ações', 'Fundos Imobiliários', 'BDR', 'ETFs', 'ETFs Americanos', 'Stocks', 'Cripto']

    # Definir intervalo de datas (1 ano)
    data_inicio = datetime.today() - timedelta(365)
    data_final = datetime.today()

    # Criar sidebar vazio
    st.sidebar.empty()
    st.sidebar.header("Insira os dados")

    tipo = st.sidebar.selectbox('Selecione um tipo de renda variável',[''] + tipo_invest)

    # Selecionar os ativos e período

    ativo = ''

    if tipo == 'Fundos Imobiliários':
        # Lista de Fundos Imobiliários utilizados
        listafii = list(pd.read_excel('lists/listafii.xls')['Código'].values)
        listafii.sort()
        lista_fiis = [ativo + '.SA' for ativo in listafii]
        ativo = st.sidebar.selectbox("Escolha um ativo",[''] + listafii)
        
    if tipo == 'Ações':
        # Lista de ações utilizadas
        lista = list(pd.read_excel('lists/listativos.xls')['Código'].values)
        lista.sort()
        lista_ativos = [ativo + '.SA' for ativo in lista]
        ativo = st.sidebar.selectbox("Escolha um ativo",[''] + lista)
        
    if tipo == 'BDR':
        listabdr = list(pd.read_excel('lists/listabdr.xls')['Código'].values)
        listabdr.sort()
        lista_bdrs = [ativo + '.SA' for ativo in listabdr]
        ativo = st.sidebar.selectbox("Escolha uma ativo",[''] + listabdr)
    
    if tipo == 'ETFs':
        # Lista de ETFs utilizados
        listaetf = list(pd.read_excel('lists/listaetfs.xls')['Código'].values)
        listaetf.sort()
        lista_etfs = [ativo + '.SA' for ativo in listaetf]
        ativo = st.sidebar.selectbox("Escolha um ativo",[''] + listaetf)

    if tipo == 'Stocks':
        # Lista de Stocks utilizados
        listastock = list(pd.read_excel('lists/listastocks.xls')['Código'].values)
        listastock.sort()
        lista_stocks = [ativo + '.SA' for ativo in listastock]
        ativo = st.sidebar.selectbox("Escolha um ativo",[''] + listastock)

    if tipo == 'ETFs Americanos':
        # Lista de ETFs americanos utilizados
        listaetfeua = list(pd.read_excel('lists/listaetfseua.xls')['Código'].values)
        listaetfeua.sort()
        lista_etfseua = [ativo + '.SA' for ativo in listaetfeua]
        ativo = st.sidebar.selectbox("Escolha um ativo",[''] + listaetfeua)
    
    if tipo == 'Cripto':
        # Lista de criptomoedas utilizadas
        listacripto = list(pd.read_excel('lists/listacripto.xls')['Código'].values)
        listacripto.sort()
        ativo = st.sidebar.selectbox("Escolha um ativo", [''] + listacripto)
        
    if tipo == '':
        st.warning("Selecione um tipo de renda variável")

    if ativo == '' and tipo == 'Fundos Imobiliários':
        st.warning("Selecione um fundo imobiliário")

    if ativo == '' and tipo == 'Ações':
        st.warning("Selecione uma ação")

    if ativo == '' and tipo == 'BDR':
        st.warning("Selecione uma BDR")
        
    if ativo == '' and tipo == 'ETFs':
        st.warning("Selecione uma ETF")
        
    if ativo == '' and tipo == 'ETFs Americanos':
        st.warning("Selecione um ETF")
        
    if ativo == '' and tipo == 'Stocks':
        st.warning("Selecione um stock")
        
    if ativo == '' and tipo == 'Cripto':
        st.warning("Selecione uma criptomoeda")
            
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

    # Condição para evitar conflito de datas

    if de_data > para_data:
        st.sidebar.warning("A data de inicio não pode ser superior a data atual")

    # Coletar dados para os ativos selecionados

    dados_ativos = {}

    if ativo in mapa_indices:
        # Se o ativo estiver no mapa_indices, use o valor mapeado diretamente
        symbol = mapa_indices[ativo]
        selected_indice = mapa_indices[ativo]
    elif tipo != 'Stocks' and tipo != 'ETFs Americanos' and tipo != 'Cripto':
        # Caso contrário, acrescente o sufixo ".SA"
        symbol = f"{ativo}.SA"
        
        # Chamar a API com o símbolo obtido
        call_api = yf.Ticker(f'{symbol}').history(start=f"{de_data}", end=f"{para_data_correta}")
        
        # Adicionar os dados ao dicionário
        dados_ativos[ativo] = pd.DataFrame(call_api)

    elif tipo == 'Cripto':
        
        symbol = f"{ativo}-USD"
        
        # Chamar a API com o símbolo obtido
        call_api = yf.Ticker(f'{symbol}').history(start=f"{de_data}", end=f"{para_data_correta}")
        
        # Adicionar os dados ao dicionário
        dados_ativos[ativo] = pd.DataFrame(call_api)
    
    else:
        symbol = f"{ativo}"

        # Chamar a API com o símbolo obtido
        call_api = yf.Ticker(f'{symbol}').history(start=f"{de_data}", end=f"{para_data_correta}")
        
        # Adicionar os dados ao dicionário
        dados_ativos[ativo] = pd.DataFrame(call_api)
        
    # Formatar coluna de datas
    for ativo, df in dados_ativos.items():
        # Verificar se o índice é do tipo datetime antes de formatar
        if isinstance(df.index, pd.DatetimeIndex):
            df.index = df.index.strftime('%Y-%m-%d')

    # Definir cores de rendimento positivo ou negativo
    color_positive = 'green'
    color_negative = 'red'

    # Remover o índice selecionado se estiver presente
    if selected_indice in dados_ativos:
        del dados_ativos[selected_indice]

    # Dicionário para valuation
    preco_teto_dict = {}
    last_data = {}
    yield_dict = {}
    pl_dict = {}
    pvp_dict = {}
    dados_div = {}
    name_dict = {}

    yield_dict_fii = {}
    pvp_dict_fii = {}
    name_dict_fii = {}
    liquidez_dict = {}
    preco_teto_dict_fii = {}

    yield_dict_bdr = {}
    pvp_dict_bdr = {}
    name_dict_bdr = {}
    pl_dict_bdr = {}

    capital_dict_etf = {}
    variacao_12_dict_etf = {}
    yield_dict_etf = {}
    name_dict_etf = {}
    variacao_60_dict_etf = {}

    setor_dict = {}
    lpa_dict = {}
    vpa_dict = {}
    roe_dict = {}
    roic_dict = {}
    evebit_dict = {}
    margbruta_dict = {}
    margebit_dict = {}
    margliq_dict = {}
    divbrut_dict = {}
    divliq_dict = {}
    patrliq_dict = {}
    
    relatorio_investidor = {}

    # Construir a URL dinâmica para cada ativo
    url_fundamentus = (f'https://investidor10.com.br/acoes/{ativo}/')
    url_fundamentus_fii = (f'https://investidor10.com.br/fiis/{ativo}/')
    url_fundamentus_bdr = (f'https://investidor10.com.br/bdrs/{ativo}/')
    url_fundamentus_etf = (f'https://investidor10.com.br/etfs/{ativo}/')
    url_fundamentus_stock = (f'https://investidor10.com.br/stocks/{ativo}/')
    url_fundamentus_etf_americano = (f'https://investidor10.com.br/etfs-global/{ativo}/')
        
    # Restante do código permanece o mesmo
    headers = { 
        'User-Agent'      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
        'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
        'Accept-Language' : 'en-US,en;q=0.5',
        'DNT'             : '1', # Do Not Track Request Header 
        'Connection'      : 'close'
    }

    dados_fundamentus = requests.get(url_fundamentus, headers=headers, timeout=30).text
    dados_fundamentus_fii = requests.get(url_fundamentus_fii, headers=headers, timeout=30).text
    dados_fundamentus_etf = requests.get(url_fundamentus_etf, headers=headers, timeout=30).text
    dados_fundamentus_bdr = requests.get(url_fundamentus_bdr, headers=headers, timeout=30).text
    dados_fundamentus_stock = requests.get(url_fundamentus_stock, headers=headers, timeout=30).text

    # Verificando se a requisição foi bem-sucedida
    if ativo != '' and tipo == 'Ações':
        # Parseando o conteúdo HTML
        ativos_url = (f'https://www.fundamentus.com.br/proventos.php?papel={ativo}&tipo=2')
        response = requests.get(ativos_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_valuation = BeautifulSoup(dados_fundamentus, 'html.parser')
        
        # Obtendo dados para RI (relatório de investidores)
        url_ri = (f'https://www.dadosdemercado.com.br/bolsa/acoes/{ativo}')
        dados_ri = requests.get(url_ri, headers=headers, timeout=30).text
        soup_ri = BeautifulSoup(dados_ri, 'html.parser')

        divs_about_params = soup_ri.find_all('div', class_='about-params')
        text_ativo = soup_ri.find_all('p', class_='serif')
        
        sobre_ativo = None
        
        for p in text_ativo:
            sobre_ativo = p.get_text()
        
        for div in divs_about_params:
            links_ri = div.find_all('a', href=True)
            text = div.find_all('span')
            text_razao = text[1].text.strip()
            text_cnpj = text[3].text.strip()
            text_isin = text[5].text.strip()
            text_setorial = text[9].text.strip()
            
            for link in links_ri:
                href = link['href']
        
        if ativo == "AURE3":
            href = "https://ri.aurenenergia.com.br/"
        
        # Obter dados de valuation        
        valuation = soup_valuation.find_all('div', class_='_card-body')
        valuation_inv10 = soup_valuation.find_all('div', class_='value d-flex justify-content-between align-items-center')
        
        # Obter valores de valuation para ações
        name = soup_valuation.find('h2').get_text()
        preco_lucro = valuation[2].find('span').text
        preco_vp = valuation[3].find('span').text
        dividend_yield = valuation[4].find('span').text
        
        # Tabela valuation para ações
        table_valuation = pd.DataFrame(columns=['P/L', 'P/VP', 'DY','EMPRESA'])
        table_valuation['EMPRESA'] = [name]
        table_valuation['P/L'] = [preco_lucro]
        table_valuation['P/VP'] = [preco_vp]
        table_valuation['DY'] = [dividend_yield]
        
        name_dict[ativo] = name    
        yield_dict[ativo] = dividend_yield
        pvp_dict[ativo] = preco_vp 
        pl_dict[ativo] = preco_lucro
           
        # Encontrando a tabela diretamente usando pandas
        
        tabela = soup.find('table')
        proventos = pd.DataFrame(columns=['Data', 'Valor', 'Tipo', 'Data de Pagamento', 'Por quantas ações'])

        for row in tabela.tbody.find_all('tr'):
            columns = row.find_all('td')
            if (columns != []):
                ult_data_table = columns[0].text.strip(' ')
                valor_table = columns[1].text.strip(' ')
                tipo_table = columns[2].text.strip(' ')
                data_pag_table = columns[3].text.strip(' ')
                qtd_açao = columns[4].text.strip(' ')
                proventos = pd.concat([proventos, pd.DataFrame.from_records([{'Data': ult_data_table, 'Valor': valor_table, 'Tipo': tipo_table, 'Data de Pagamento': data_pag_table, 'Por quantas ações': qtd_açao}])])
        
        proventos.head(20)
        proventos['Valor'] = [x.replace(',','.') for x in proventos['Valor']]
        proventos = proventos.astype({'Valor': float})
        proventos = proventos.drop(columns=['Por quantas ações'])
        proventos.set_index('Tipo', inplace=True)
        proventos = proventos.rename(columns={'Data': 'Registro', 'Data de Pagamento': 'Pagamento'})

        proventos['Ano'] = pd.to_datetime(proventos['Registro'], dayfirst=True).dt.year.astype(str) 
        proventos['Ano'] = proventos['Ano'].str.replace(',', '')
            
        # Calcular o preço teto
        
        somatoria_por_ano = proventos.groupby('Ano')['Valor'].sum().reset_index()

        # Mantendo apenas as últimas linhas
        somatoria_por_ano = somatoria_por_ano.tail(6)

        # Calcular o preco_teto para cada ativo e armazenar no dicionário
            
        media_prov = (somatoria_por_ano['Valor'].sum()) / 6
        preco_teto = (media_prov * 100) / 5
        preco_teto_dict[ativo] = preco_teto
        
        # Coletar dados fundamentalistas do ativo
        
        dados_fundamentalistas = fundamentus.get_detalhes_papel(f'{ativo}')
        df_fund = pd.DataFrame(dados_fundamentalistas)
        df_fund = df_fund.reset_index(drop=True)
        
        setor = df_fund.at[0, 'Subsetor']
        lpa = df_fund.at[0, 'LPA']
        vpa = df_fund.at[0, 'VPA']
        roe = df_fund.at[0, 'ROE']
        roic = df_fund.at[0, 'ROIC']
        evebit = df_fund.at[0, 'EV_EBIT']
        margbruta = df_fund.at[0, 'Marg_Bruta']
        margebit = df_fund.at[0, 'Marg_EBIT']
        margliq = df_fund.at[0, 'Marg_Liquida']
        
        if 'Div_Bruta' in df_fund.columns:
            divbruta = df_fund.at[0, 'Div_Bruta']
        else:
            divbruta = None
    
        patrliq = df_fund.at[0, 'Patrim_Liq']
        evebitda = df_fund.at[0, 'EV_EBITDA']
        pebit = df_fund.at[0, 'PEBIT']
        psr = df_fund.at[0, 'PSR']
        cre = df_fund.at[0, 'Cres_Rec_5a']
        
        if 'Div_Liquida' in df_fund.columns:
            divliq = df_fund.at[0, 'Div_Liquida'] 
        else:
            divliq = None
    
    elif ativo != '' and tipo == 'Stocks':
        soup_stock = BeautifulSoup(dados_fundamentus_stock, 'html.parser')
        valuation_stock = soup_stock.find_all('div', class_='_card-body')
        
        # Obter valores de valuation para ações
        name = soup_stock.find('h2').get_text()
        preco_lucro = valuation_stock[2].find('span').text
        preco_vp = valuation_stock[3].find('span').text
        dividend_yield = valuation_stock[4].find('span').text
        
        # Tabela valuation para ações
        table_valuation_stock = pd.DataFrame(columns=['P/L', 'P/VP', 'DY','EMPRESA'])
        table_valuation_stock['EMPRESA'] = [name]
        table_valuation_stock['P/L'] = [preco_lucro]
        table_valuation_stock['P/VP'] = [preco_vp]
        table_valuation_stock['DY'] = [dividend_yield]
        
        name_dict[ativo] = name    
        yield_dict[ativo] = dividend_yield
        pvp_dict[ativo] = preco_vp 
        pl_dict[ativo] = preco_lucro
        
    
    elif ativo != '' and tipo == 'Fundos Imobiliários': 
        stock_fii_url = (f'https://www.fundamentus.com.br/fii_proventos.php?papel={ativo}&tipo=2')
        response_fii = requests.get(stock_fii_url, headers=headers, timeout=30).text
        soup_proventos = BeautifulSoup(response_fii, 'html.parser')
        soup_fii = BeautifulSoup(dados_fundamentus_fii, 'html.parser')
        valuation_fii = soup_fii.find_all('div', class_='_card-body')
            
        # Obter valores de valuation para fii's
        name_fii = soup_fii.find('h2').get_text()
        preco_vp_fii = valuation_fii[2].find('span').text
        dividend_yield_fii = valuation_fii[1].find('span').text
        liquidez_fii = valuation_fii[3].find('span').text
            
        # Tabela valuation para fii
        table_valuation_fii = pd.DataFrame(columns=['P/VP', 'DY', 'EMPRESA', 'LIQUIDEZ'])
        table_valuation_fii['P/VP'] = [preco_vp_fii]
        table_valuation_fii['DY'] = [dividend_yield_fii]
        table_valuation_fii['EMPRESA'] = [name_fii]
        table_valuation_fii['LIQUIDEZ'] = [liquidez_fii]
            
        yield_dict_fii[ativo] = dividend_yield_fii
        pvp_dict_fii[ativo] = preco_vp_fii
        name_dict_fii[ativo] = name_fii
        liquidez_dict[ativo] = liquidez_fii

        tabela_fii = soup_proventos.find('table')
        proventos_fii = pd.DataFrame(columns=['Última Data Com', 'Tipo', 'Data de Pagamento', 'Valor'])
            
        for row in tabela_fii.tbody.find_all('tr'):
            columns = row.find_all('td')
            if (columns != []):
                ult_data_table = columns[0].text.strip(' ')
                tipo_table = columns[1].text.strip(' ')
                data_pag_table = columns[2].text.strip(' ')
                valor_table = columns[3].text.strip(' ')
                proventos_fii = pd.concat([proventos_fii, pd.DataFrame.from_records([{'Última Data Com': ult_data_table, 'Tipo': tipo_table, 'Data de Pagamento': data_pag_table, 'Valor': valor_table}])])
        
        proventos_fii.head(20)
        proventos_fii['Valor'] = [x.replace(',','.') for x in proventos_fii['Valor']]
        proventos_fii = proventos_fii.astype({'Valor': float})
        proventos_fii.set_index('Tipo', inplace=True)
        proventos_fii = proventos_fii.rename(columns={'Última Data Com': 'Registro', 'Data de Pagamento': 'Pagamento'})

        proventos_fii['Ano'] = pd.to_datetime(proventos_fii['Registro']).dt.year.astype(str) 
        proventos_fii['Ano'] = proventos_fii['Ano'].str.replace(',', '')
            
        # Calcular o preço teto do fundo imobiliário
        
        somatoria_por_ano_fii = proventos_fii.groupby('Ano')['Valor'].sum().reset_index()

        # Mantendo apenas as últimas linhas
        somatoria_por_ano_fii = somatoria_por_ano_fii.tail(6)

        # Calcular o preco_teto para cada ativo e armazenar no dicionário
            
        media_prov_fii = (somatoria_por_ano_fii['Valor'].sum()) / 6
        preco_teto_fii = (media_prov_fii * 100) / 5
        preco_teto_dict_fii[ativo] = preco_teto_fii
        
    elif ativo != '' and tipo == 'BDR':
        
        soup_bdr = BeautifulSoup(dados_fundamentus_bdr, 'html.parser')      
        valuation_bdr = soup_bdr.find_all('div', class_='_card-body')
            
        # Obter valores de valuation para ações
        name_bdr = soup_bdr.find('h2').get_text()
        preco_lucro_bdr = valuation_bdr[2].find('span').text
        preco_vp_bdr = valuation_bdr[3].find('span').text
        dividend_yield_bdr = valuation_bdr[4].find('span').text
            
        # Tabela valuation para ações
        table_valuation_bdr = pd.DataFrame(columns=['P/L', 'P/VP', 'DY','EMPRESA'])
        table_valuation_bdr['EMPRESA'] = [name_bdr]
        table_valuation_bdr['P/L'] = [preco_lucro_bdr]
        table_valuation_bdr['P/VP'] = [preco_vp_bdr]
        table_valuation_bdr['DY'] = [dividend_yield_bdr]
            
        name_dict_bdr[ativo] = name_bdr    
        yield_dict_bdr[ativo] = dividend_yield_bdr
        pvp_dict_bdr[ativo] = preco_vp_bdr 
        pl_dict_bdr[ativo] = preco_lucro_bdr    

    elif ativo != '' and tipo == 'ETFs':
        
        soup_bdr = BeautifulSoup(dados_fundamentus_etf, 'html.parser')      
        valuation_etf = soup_bdr.find_all('div', class_='_card-body')
            
        # Obter valores de valuation para ações
        name_etf = soup_bdr.find('h2').get_text()
        capitalizacao = valuation_etf[1].find('span').text
        variacao_12m = valuation_etf[2].find('span').text
        variacao_60m = valuation_etf[3].find('span').text
        dividend_yield_etf = valuation_etf[4].find('span').text
            
        # Tabela valuation para ações
        table_valuation_etf = pd.DataFrame(columns=['CAPITALIZAÇÃO', 'VARIAÇÃO (12M)', 'DY','ETF', 'VARIAÇÃO (60M)'])
        table_valuation_etf['ETF'] = [name_etf]
        table_valuation_etf['CAPITALIZAÇÃO'] = [capitalizacao]
        table_valuation_etf['VARIAÇÃO (12M)'] = [variacao_12m]
        table_valuation_etf['VARIAÇÃO (60M)'] = [variacao_60m]
        table_valuation_etf['DY'] = [dividend_yield_etf]
            
        name_dict_etf[ativo] = name_etf    
        yield_dict_etf[ativo] = dividend_yield_etf
        capital_dict_etf[ativo] = capitalizacao
        variacao_12_dict_etf[ativo] = variacao_12m    
        variacao_60_dict_etf[ativo] = variacao_60m
        
    elif ativo != '' and tipo == 'ETFs Americanos':
        
        dados_fundamentus_etf = requests.get(url_fundamentus_etf_americano, headers=headers, timeout=10).text
        
        soup_etf = BeautifulSoup(dados_fundamentus_etf, 'html.parser')      
        valuation_etf = soup_etf.find_all('div', class_='_card-body')
            
        # Obter valores de valuation para ações
        name_etf = soup_etf.find('h2').get_text()
        capitalizacao = valuation_etf[1].find('span').text
        variacao_12m = valuation_etf[2].find('span').text
        variacao_60m = valuation_etf[3].find('span').text
        dividend_yield_etf = valuation_etf[4].find('span').text
            
        # Tabela valuation para ações
        table_valuation_etf = pd.DataFrame(columns=['CAPITALIZAÇÃO', 'VARIAÇÃO (12M)', 'DY','ETF', 'VARIAÇÃO (60M)'])
        table_valuation_etf['ETF'] = [name_etf]
        table_valuation_etf['CAPITALIZAÇÃO'] = [capitalizacao]
        table_valuation_etf['VARIAÇÃO (12M)'] = [variacao_12m]
        table_valuation_etf['VARIAÇÃO (60M)'] = [variacao_60m]
        table_valuation_etf['DY'] = [dividend_yield_etf]
            
        name_dict_etf[ativo] = name_etf    
        yield_dict_etf[ativo] = dividend_yield_etf
        capital_dict_etf[ativo] = capitalizacao
        variacao_12_dict_etf[ativo] = variacao_12m    
        variacao_60_dict_etf[ativo] = variacao_60m

    if ativo != '' and tipo != '':
        for ativo, df in dados_ativos.items():
            
            last_data = df.iloc[-1]
            
            # Calcular os retornos apenas se houver dados disponíveis
            if len(df) > 1:
                
                df_retornos = (df['Close'].pct_change() + 1).cumprod() - 1
                rendimento_total = df_retornos.iloc[-1]
                
                rendimento_diario = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                variacao = rendimento_diario / 100
                
                colimg, colname = st.columns(2)
                
                with colimg:
                    if tipo == 'ETFs' or tipo == 'ETFs Americanos':
                        st.image(f'https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/BOVV.png', width=85)
                    elif tipo == 'Fundos Imobiliários':
                        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSaNUDgPvK_OIJ3RcMqrTqLEQXRZG8dPX-526Bfc_aNlA&s", width=85)
                    elif tipo == 'Stocks':
                        st.image(f"https://raw.githubusercontent.com/nvstly/icons/main/ticker_icons/{ativo}.png", width=85)
                    elif tipo == 'Cripto':
                        st.image(f"https://raw.githubusercontent.com/nvstly/icons/main/crypto_icons/{ativo}.png", width=85)
                    elif ativo == 'ROXO34':
                        st.image("https://cdn.worldvectorlogo.com/logos/nubank-3.svg", width=85)
                    elif ativo == 'INBR32':
                        st.image("https://www.idinheiro.com.br/wp-content/uploads/2021/02/inter.jpg", width=85)
                    else:
                        st.image(f'https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{ativo}.png', width=85)
 
                with colname:
                    if ativo in name_dict:
                        st.subheader(f'{name_dict[ativo]}')
                    elif ativo in name_dict_fii:
                        st.subheader(f'{name_dict_fii[ativo]}')
                    elif ativo in name_dict_bdr:
                        st.subheader(f'{name_dict_bdr[ativo]}')
                    elif ativo in name_dict_etf:
                        st.subheader(f'{name_dict_etf[ativo]}')
                    else:
                        st.write("")     

                st.subheader(f'{ativo}')

                if rendimento_diario < 0:
                    st.write(f"<span style='color:{color_negative}'>{variacao:.2%}</span>", unsafe_allow_html=True)
                else:
                    st.write(f"<span style='color:{color_positive}'>+{variacao:.2%}</span>", unsafe_allow_html=True)
                
                if ativo != '' and tipo == 'Ações':
                    st.write(f'Setor: {setor}')
                    st.write()
                
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    st.write("**Cotação:**")
                    if tipo != "Stocks" and tipo != "ETFs Americanos" and tipo != 'Cripto':
                        st.write(f"R$ {last_data['Close']:.2f}")
                    else:
                        st.write(f"US$ {last_data['Close']:.2f}")
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
                    elif ativo in pl_dict_bdr:
                        st.write("**P/L**")
                        st.write(f"{pl_dict_bdr[ativo]}")
                    elif ativo in liquidez_dict:
                        st.write("**LIQUIDEZ DIÁRIA**")
                        st.write(f"{liquidez_dict[ativo]}")
                    elif ativo in capital_dict_etf:
                        st.write("**Capitalização**")
                        st.write(f"{capital_dict_etf[ativo]}")
                with col4:
                    if ativo in pvp_dict:
                        st.write("**P/VP**")
                        st.write(f"{pvp_dict[ativo]}")
                    elif ativo in pvp_dict_fii:
                        st.write("**P/VP**")
                        st.write(f"{pvp_dict_fii[ativo]}")
                    elif ativo in pvp_dict_bdr:
                        st.write("**P/VP**")
                        st.write(f"{pvp_dict_bdr[ativo]}")
                    elif ativo in variacao_12_dict_etf:
                        st.write("**Variação (12m)**")
                        st.write(f"{variacao_12_dict_etf[ativo]}")
                with col5:
                    if ativo in yield_dict:
                        st.write("**DY**")
                        st.write(f"{yield_dict[ativo]}")
                    elif ativo in yield_dict_fii:
                        st.write("**DY**")
                        st.write(f"{yield_dict_fii[ativo]}")
                    elif ativo in yield_dict_bdr:
                        st.write("**DY**")
                        st.write(f"{yield_dict_bdr[ativo]}")
                    elif ativo in variacao_60_dict_etf:
                        st.write("**Variação (60m)**")
                        st.write(f"{variacao_60_dict_etf[ativo]}")
                with col6:
                    if ativo in preco_teto_dict:
                        st.write("**Preço Teto**")
                        st.write(f"R$ {preco_teto_dict[ativo]:.2f}")
                    elif ativo in preco_teto_dict_fii:
                        st.write("**Preço Teto**")
                        st.write(f"R$ {preco_teto_dict_fii[ativo]:.2f}")
                    elif ativo in yield_dict_etf:
                        st.write("**DY**")
                        st.write(f"{yield_dict_etf[ativo]}")
                    elif tipo == 'Stocks' and tipo == 'ETFs Americanos' and tipo == 'Cripto':
                        st.write("**Preço Teto**")
                        st.write("N/A")
                
            else:
                st.write("Não há dados suficientes para calcular retornos.")

            cola, colb, colc, cold = st.columns(4)
            
            with cola:
                if ativo != '' and tipo == 'Ações':
                    st.link_button(f"Veja mais sobre {ativo}", f"https://investidor10.com.br/acoes/{ativo}/")
                    
                if ativo != '' and tipo == 'Fundos Imobiliários':
                    st.link_button(f"Veja mais sobre {ativo}", f"https://www.fundsexplorer.com.br/funds/{ativo}")
                elif ativo != '' and tipo == 'BDR':
                    st.link_button(f"Veja mais sobre {ativo}", f"https://investidor10.com.br/bdrs/{ativo}/")
                elif ativo != '' and tipo == 'ETFs':
                    st.link_button(f"Veja mais sobre {ativo}", f"https://investidor10.com.br/etfs/{ativo}/")
                elif ativo != '' and tipo == 'ETFs Americanos':
                    st.link_button(f"Veja mais sobre {ativo}", f"https://investidor10.com.br/etfs-global/{ativo}/")
                elif ativo != '' and tipo == 'Stocks':
                    st.link_button(f"Veja mais sobre {ativo}", f"https://investidor10.com.br/stocks/{ativo}/")
                elif ativo != '' and tipo == 'Cripto':
                    st.link_button(f'Veja mais sobre {ativo}', f"https://finance.yahoo.com/quote/{ativo}-USD")
            
            with colb:
                if tipo == "Ações" and href == "None" and ativo != '':
                    st.warning(f"Não foi possível obter o RI de {ativo}")
                elif tipo == "Ações" and href != "None" and ativo != '':
                    st.link_button(f"Acessar o RI de {ativo}", f"{href}")
                elif tipo == "Fundos Imobiliários" and ativo != '':
                    ri_fii = (f"https://www.fundsexplorer.com.br/comunicados?ticker={ativo}")
                    st.link_button(f"Comunicados de {ativo}", f"{ri_fii}")
                elif tipo == 'Cripto' and ativo != '':
                    st.link_button(f"MarketCap de {ativo}", f"https://br.tradingview.com/symbols/{ativo}/")
                elif tipo == 'ETFs' and ativo != '':
                    st.link_button(f"Análise de {ativo}", f"https://br.tradingview.com/symbols/BMFBOVESPA-{ativo}/analysis/")
                elif tipo == 'ETFs Americanos' and ativo != '':
                    st.link_button(f"Análise de {ativo}", f"https://br.tradingview.com/symbols/{ativo}/analysis/")
                elif tipo == 'BDR' and ativo != '':
                    st.link_button(f"Análise de {ativo}", f"https://br.tradingview.com/symbols/BMFBOVESPA-{ativo}/technicals/")
                elif tipo == 'Stocks' and ativo != '':
                    st.link_button(f"Finanças de {ativo}", f"https://br.tradingview.com/symbols/{ativo}/financials-overview/")
            with colc:
                if ativo != '' and tipo != 'Stocks' and tipo != 'ETFs Americanos' and tipo != 'Cripto':
                    st.link_button(f"Notícias sobre {ativo}", f"https://br.tradingview.com/symbols/BMFBOVESPA-{ativo}/news/")
                elif tipo == 'Cripto' and ativo !='':
                    st.link_button(f"Notícias sobre Criptomoedas", f"https://br.tradingview.com/news/markets/?category=crypto")
                elif tipo == 'ETFs Americanos' and ativo != '':
                    st.link_button(f"Notícias sobre {ativo}", f"https://br.tradingview.com/symbols/{ativo}/news/")
                elif tipo == 'Stocks' and ativo != '':
                    st.link_button(f"Notícias sobre {ativo}", f"https://br.tradingview.com/symbols/{ativo}/news/")
            with cold:
                if ativo != '':
                    st.link_button(f"Estudos da Economática", "https://insight.economatica.com/category/estudos/")
                    
            st.write("\n---\n")
            
            colCotaçao, colDividendo = st.columns(2)
            
            with colCotaçao:
                # Plotando o gráfico de cotações
                st.subheader("Cotação")
                fig_cotacoes = go.Figure()

                for ativo, df in dados_ativos.items():
                    # Ignorar ativos que são iguais aos índices do mapa_indices
                    if ativo not in selected_indice:
                        fig_cotacoes.add_trace(go.Scatter(x=pd.to_datetime(df.index), y=df['Close'], mode='lines', name=ativo))

                if tipo != 'Stocks' and tipo != 'ETFs Americanos' and tipo != 'Cripto':
                    
                    # Adicionando legenda e título
                    fig_cotacoes.update_layout(
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        yaxis_tickprefix='R$',
                        yaxis_tickformat=',.2f',
                        title=f"Histórico de {ativo}",
                        xaxis_title='Data',
                        yaxis_title='Preço de Fechamento'
                    )
                
                else:
                    
                    # Adicionando legenda e título
                    fig_cotacoes.update_layout(
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        yaxis_tickprefix='US$',
                        yaxis_tickformat=',.2f',
                        title=f"Histórico de {ativo}",
                        xaxis_title='Data',
                        yaxis_title='Preço de Fechamento'
                    )

                # Exibindo o gráfico de cotações
                st.plotly_chart(fig_cotacoes)

                with st.expander("Histórico da cotação:"):
                    st.dataframe(df, width=850, height=350)
                    df = dados_ativos[ativo]

        with colDividendo:
            st.subheader("Proventos")
            
            if tipo == "Ações":           

                # Plotar gráfico de barras do total de proventos distribuídos por ano
                fig_proventos = go.Figure()

                fig_proventos.add_bar(x=somatoria_por_ano['Ano'], y=somatoria_por_ano['Valor'], marker_color='palegreen')

                fig_proventos.update_layout(
                    xaxis_title='Ano',
                    yaxis_title='Valor (R$)',
                    title='Total de Proventos Distribuídos por Ano',
                )

                for i, ano in enumerate(somatoria_por_ano['Ano']):
                    fig_proventos.add_annotation(
                        x=ano,
                        y=somatoria_por_ano['Valor'].iloc[i],
                        text=f"R$ {somatoria_por_ano['Valor'].iloc[i]:,.2f}",
                        showarrow=True,
                        arrowhead=1
                    )

                st.plotly_chart(fig_proventos)

                with st.expander("Histórico de dividendos:"):
                    st.dataframe(proventos, width=850, height=350)
                 
            elif tipo == "Fundos Imobiliários":
                    
                # Plotar gráfico de barras do total de proventos distribuídos por ano
                fig_proventos_fii = go.Figure()

                fig_proventos_fii.add_bar(x=somatoria_por_ano_fii['Ano'], y=somatoria_por_ano_fii['Valor'], marker_color='palegreen')

                fig_proventos_fii.update_layout(
                    xaxis_title='Ano',
                    yaxis_title='Valor (R$)',
                    title='Total de Proventos Distribuídos por Ano',
                )

                for i, ano in enumerate(somatoria_por_ano_fii['Ano']):
                    fig_proventos_fii.add_annotation(
                        x=ano,
                        y=somatoria_por_ano_fii['Valor'].iloc[i],
                        text=f"R$ {somatoria_por_ano_fii['Valor'].iloc[i]:,.2f}",
                        showarrow=True,
                        arrowhead=1
                    )

                st.plotly_chart(fig_proventos_fii)

                with st.expander("Histórico de dividendos:"):
                    st.dataframe(proventos_fii, width=850, height=350)
                        
            else:
                st.warning("Não foi possível obter a tabela de proventos")
                
        st.write("\n---\n")
        
        st.subheader("Indice x Cotação")

        if selected_indice == "":
            st.warning("Selecione o índice para analisar o rendimento")
        else:
            fig_retornos = go.Figure()
            dados_retornos_completo = {}

        # Carregar dados do índice
        if selected_indice == "BOVESPA":
            indice = yf.download('^BVSP', start=f"{de_data}", end=f"{para_data_correta}")
        elif selected_indice == "DÓLAR":
            indice = yf.download('BRL=X', start=f"{de_data}", end=f"{para_data_correta}")
        elif selected_indice == "EURO":
            indice = yf.download('EURBRL=X', start=f"{de_data}", end=f"{para_data_correta}")
        elif selected_indice == "S&P 500":
            indice = yf.download('^GSPC', start=f"{de_data}", end=f"{para_data_correta}")
        elif selected_indice == "DOW JONES":
            indice = yf.download('^DJI', start=f"{de_data}", end=f"{para_data_correta}")
        elif selected_indice == "NASDAQ":
            indice = yf.download('^IXIC', start=f"{de_data}", end=f"{para_data_correta}")
        elif selected_indice == "IBRX 50":
            indice = yf.download('^IBX50', start=f"{de_data}", end=f"{para_data_correta}")
            
        if selected_indice != '' and ativo != '':
            indice_retornos = (indice['Close'].pct_change() + 1).cumprod() - 1
            dados_retornos_completo[selected_indice] = indice_retornos
            fig_retornos.add_trace(go.Scatter(x=pd.to_datetime(indice_retornos.index), y=indice_retornos, mode='lines', name=selected_indice, line=dict(color='orange')))

            for ativo, df in dados_ativos.items():
                # Calcular os retornos apenas se houver dados disponíveis
                if len(df) > 1:
                    df_retornos = (df['Close'].pct_change() + 1).cumprod() - 1
                    dados_retornos_completo[ativo] = df_retornos
                    fig_retornos.add_trace(go.Scatter(x=pd.to_datetime(df_retornos.index), y=df_retornos, mode='lines', name=ativo, line=dict(color='blue')))

            fig_retornos.update_layout(
                title="Comparação de Rendimento de Ativos e Índice",
                xaxis_title="Data",
                yaxis_title="Rendimento",
                yaxis_tickformat=",.0%",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig_retornos, use_container_width=True)
        
        st.write("\n---\n")
        
        if ativo != '' and tipo == 'Ações':
            st.subheader("Indicadores Fundamentalistas")

            col1f, col2f, col3f, col4f, col5f, col6f = st.columns(6)

            with col1f:
                st.write("**P/L:**")
                st.write(f"{pl_dict[ativo]}")
            
            with col2f:
                st.write("**P/VP:**")
                st.write(f"{pvp_dict[ativo]}")

            with col3f:
                st.write("**DY:**")
                st.write(f"{yield_dict[ativo]}")
                
            with col4f:
                if lpa != '-':
                    st.write("**LPA:**")
                    valor_lpa = float(lpa) / 100
                    st.write(f"{valor_lpa:.2f}". replace('.',','))
                else:
                    st.write("**LPA:**")
                    st.write("-")
                    
            with col5f:
                if vpa != '-':
                    st.write("**VPA:**")
                    valor_vpa = float(vpa) / 100
                    st.write(f"{valor_vpa:.2f}". replace('.',','))
                else:
                    st.write("**VPA:**")
                    st.write("-")
                
            with col6f:
                if roe != '-':
                    st.write("**ROE:**")
                    st.write(f"{roe}")
                else:
                    st.write("**ROE:**")
                    st.write("-")
                
            col13f, col14f, col15f, col16f, col17f, col18f = st.columns(6)

            with col13f:
                if roic != '-':
                    st.write("**ROIC:**")
                    st.write(f"{roic}")
                else:
                    st.write("**ROIC:**")
                    st.write("-")
            
            with col14f:
                if evebit != '-':
                    st.write("**EV/EBIT:**")
                    valor_pebit = float(evebit) / 100
                    st.write(f"{valor_pebit:.2f}". replace('.',','))
                else:
                    st.write("**EV/EBIT:**")
                    st.write("-")
                    
            with col15f:
                if evebitda != '-':
                    st.write("**EV/EBITDA:**")
                    valor_evebitda = float(evebitda) / 100
                    st.write(f"{valor_evebitda:.2f}". replace('.',','))
                else:
                    st.write("**EV/EBITDA:**")
                    st.write("-")
            
            with col16f:
                if pebit != '-':
                    st.write("**P/EBIT:**")
                    valor_pebit = float(pebit) / 100
                    st.write(f"{valor_pebit:.2f}". replace('.',','))
                else:
                    st.write("**P/EBIT:**")
                    st.write("-")
                    
            with col17f:
                if psr != '-':
                    st.write("**PSR:**")
                    valor_psr = float(psr) / 100
                    st.write(f"{valor_psr:.2f}". replace('.',','))
                else:
                    st.write("**PSR:**")
                    st.write("-")
                
            with col18f:
                if cre != '-':
                    st.write("**Cres. Receita Líquida (5a) :**")
                    st.write(f"{cre}")
                else:
                    st.write("**Cres. Receita Líquida (5a) :**")
                    st.write("-")
                
            col7f, col8f, col9f, col10f, col11f, col12f = st.columns(6)    

            with col7f:
                if margbruta != '-':
                    st.write("**Marg Bruta:**")
                    st.write(f"{margbruta}")
                else:
                    st.write("**Marg Bruta:**")
                    st.write("-")  
                    
            with col8f:
                if margebit != '-':
                    st.write("**Marg Ebit:**")
                    st.write(f"{margebit}")
                else:
                    st.write("**Marg Ebit:**")
                    st.write("-")  
                
            with col9f:
                if margliq != '-':
                    st.write("**Marg Líquida:**")
                    st.write(f"{margliq}")
                else:
                    st.write("**Marg Líquida:**")
                    st.write("-")
            
            with col10f:
                if divbruta != '-' and divbruta != None:
                    st.write("**Dívida Bruta:**")
                    valor_divbruta = float(divbruta)
                    st.write(f"{valor_divbruta:,.0f}")
                else:
                    st.write("**Dív. Bruta:**")
                    st.write("-")
            
            with col11f:
                if divliq != '-' and divliq != None:
                    st.write("**Dív. Liquida:**")
                    valor_divliq = float(divliq)
                    st.write(f"{valor_divliq:,.0f}")
                else:
                    st.write("**Dív. Liquida:**")
                    st.write("-")
            
            with col12f:
                if patrliq != '-':
                    st.write("**Patr. Líquido:**")
                    valor_patrliq = float(patrliq)
                    st.write(f"{valor_patrliq:,.0f}")
                else:
                    st.write("**Patr. Líquido:**")
                    st.write("-")
                    
            st.write("\n---\n")
                
            st.subheader(f"Sobre {ativo}")
            
            if sobre_ativo is None:
                st.write(f"**Razão social:** {text_razao}")
                st.write(f"**CNJP:** {text_cnpj}")
                st.write(f"**Código ISIN:** {text_isin}")
                st.write(f"**Classificação setorial B3:** {text_setorial}")
            else:
                st.write(sobre_ativo)
                st.write(f"**Razão social:** {text_razao}")
                st.write(f"**CNJP:** {text_cnpj}")
                st.write(f"**Código ISIN:** {text_isin}")
                st.write(f"**Classificação setorial B3:** {text_setorial}")

            
# Aba da calculadora de juros simples        

with aba2:
    
    st.header("Calculadora de Juros Simples")

    valor_inicial = st.number_input("Valor Inicial:", min_value=0.0)
    taxa_juros_simples = st.number_input("Taxa de Juros:", min_value=0.0, step=0.5, format="%g") / 100
    tempo_anos_simples = st.number_input("Tempo (anos):", min_value=1, step=1, key="initial_value")

    juros = (valor_inicial * taxa_juros_simples * tempo_anos_simples)
    montante_simples = valor_inicial + juros
    
    if st.button("Calcular"):
        st.write(f"**Montante Total:** R$ {montante_simples}")
        st.write(f"**Valor Total de Juros:** R$ {juros}")

# Aba de calculadora de juros compostos

with aba3:
    
    st.header("Calculadora de Juros Compostos")
    
    capital = st.number_input("Valor Inicial:", min_value=0.0, key="capital_input")
    aporte_mensal = st.number_input("Aporte Mensal:", min_value=0.0, key="aporte_input")
    taxa_juros_ano = st.number_input("Taxa de Juros (Anual):", min_value=0.0, step=0.5, format="%g", key="taxa_juros_input") / 100
    tempo_anos = st.number_input("Tempo (anos):", min_value=1, step=1, key="tempo_anos_input")
    
    meses = int(tempo_anos * 12)
    total = capital
    deposito = 0

    taxa_juros_mes = ((1 + taxa_juros_ano)**(1/12) - 1) * 100

    for vezes in range(1, (meses + 1)):
        deposito += aporte_mensal
        total += (total * (taxa_juros_mes / 100))
        total += aporte_mensal
        
    deposito = deposito + capital
    juros_compostos = total - deposito
    
    deposito_formatado = "R$ {:,.2f}".format(deposito).replace('.', '.')
    juros_formatado = "R$ {:,.2f}".format(juros_compostos).replace('.', '.')
    total_formatado = "R$ {:,.2f}".format(total).replace('.', '.')
    
    if st.button("Calcular", key="calcular_button"):
        st.write(f"**Total Investido:** {deposito_formatado}")
        st.write(f"**Total em Juros:** {juros_formatado}")
        st.write(f"**Montante Total:** {total_formatado}")

# Aba simulador de carteira

with aba4:

    lista_carteira = list(pd.read_excel('lists/listativos.xls')['Código'].values)
    lista_carteira.sort()
    lista_ativos_carteira = [ativo + '.SA' for ativo in lista_carteira]

    st.header("Simulador de Carteira - Rentabilidade")

    qtd_ativo = st.number_input("Insira a quantidade:", min_value=0, step=1)

    # Função para simular carteira
    def simulador_carteira(de_data, para_data_correta, carteira):
        if not carteira:
            st.warning("Adicione ativos à carteira antes de simular.")
            return None
        
        carteira_sa = {}
        for valor, ativo in carteira.items():
            ativo_sa = ativo + '.SA'
            carteira_sa[ativo_sa] = float(valor)  # Convertendo o valor para float
        
        try:
            precos_cotacao = yf.download(list(carteira_sa.keys()), start=de_data, end=para_data_correta, progress=False)['Adj Close']
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
            ibov = yf.download('^BVSP', start=de_data, end=para_data_correta, progress=False)['Adj Close'].rename('IBOV')
        except Exception as e:
            st.error(f"Erro ao baixar dados do Ibovespa: {e}")
            return None
        
        dado_consolidado = pd.concat([ibov, pl], axis=1, join='inner')
        dado_consolidado_adj = dado_consolidado / dado_consolidado.iloc[0]
        
        # Criar o gráfico com Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dado_consolidado_adj.index, y=dado_consolidado_adj['IBOV'], mode='lines', name='BOVESPA', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=dado_consolidado_adj.index, y=dado_consolidado_adj['PL Total'], mode='lines', name='CARTEIRA'))
        fig.update_layout(title="Carteira x Bovespa", xaxis_title="Data", yaxis_title="Rendimento")
        
        # Exibir o gráfico comparativo
        st.plotly_chart(fig, use_container_width=True)

    # Carteira de ativos
    carteira = {}
    contador = 0

    try:
        while contador < qtd_ativo:
            ativo = st.selectbox(f"Selecione o ativo {contador + 1}", [''] + lista_carteira, key=f"select_ativo_{contador}")
            preco = st.text_input(f"Insira o valor em R$ a ser investido em {ativo}", key=f"input_preco_{contador}")

            if ativo != '' and preco != '':
                preco_float = float(preco)
                carteira[preco_float] = ativo
                contador += 1

    except Exception as e:
        st.warning("Selecione o ativo e insira o valor aportado")

    if qtd_ativo != 0:
        if st.button("Comparar rendimento") and carteira:
            simulador_carteira(de_data, para_data_correta, carteira)
    else:
        st.warning("Informe a quantidade de ativos em sua carteira")
