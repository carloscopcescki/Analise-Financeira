import pandas as pd
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import matplotlib.ticker as mtick
from bs4 import BeautifulSoup

class Page:
    """Criar dashboard para monitoramento de ativos"""
    def __init__(self) -> None:
        pass
    
    def webpage(self) -> None:
        """Elaboração da page"""
        st.set_page_config(
            page_title="Monitor Financeiro",
            page_icon="💰",
            layout="wide",
        )
        
        st.html('''
        <style>
        hr {
            border-color: #880808;
        }
        </style>
        ''')
        
        st.markdown(
        """
        <div style="background-color:#880808";padding:10px;border-radius:20px">
        </div>
        """,
        unsafe_allow_html=True,
        )
        
        st.sidebar.empty()
        st.sidebar.title("Stock Value")
        st.sidebar.header("Insira os dados")

class Market:
    """Classe para obter os dados de forma de investimento e ativo"""
    def __init__(self, market_name: str) -> None:
        self.market = market_name
    
    def stock_list(self) -> list[str]:
        """Obtém lista de ativos para cada tipo"""
        if self.market == 'Ações':
            stock_list = list(pd.read_excel('lists/listativos.xls')['Código'].values)  
            stock_list.sort()
            return [stock for stock in stock_list]
        else:
            stock_list = list(pd.read_excel('lists/listafii.xls')['Código'].values)  
            stock_list.sort()
            return [stock for stock in stock_list]
        return []
      
    def stock_data(self, symbol: str) -> pd.DataFrame:
        """Gera dataframe com os dados dos ativos"""
        self.symbol_data = {}
        self.stock = yf.Ticker(f'{symbol}.SA').history(period='1y')
        self.symbol_data[symbol] = pd.DataFrame(self.stock)
        df = self.symbol_data[symbol]
        return df

    def price_chart(self, symbol: str) -> None:
        """Gera gráfico de preço"""
        st.subheader(f"Cotação {symbol}")
        fig_cotacoes = go.Figure()

        for symbol, df in self.symbol_data.items():
            fig_cotacoes.add_trace(go.Scatter(x=pd.to_datetime(df.index), y=df['Close'], mode='lines', name=symbol))
        
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
            xaxis_title='Data',
            yaxis_title='Preço de Fechamento'
        )
        st.plotly_chart(fig_cotacoes)

    def dividends(self, symbol: str) -> None:
        """Coleta os dividendos distribúidos pela empresa"""
        dividend_table = soup.find('table')
        dividends = pd.DataFrame(columns=['Data Com', 'Valor', 'Tipo', 'Data de Pagamento', 'Por quantas ações'])

        if dividend_table:
            for row in dividend_table.tbody.find_all('tr'):
                columns = row.find_all('td')
                if (columns != []):
                    ult_data_table = columns[0].text.strip(' ')
                    valor_table = columns[1].text.strip(' ')
                    type_table = columns[2].text.strip(' ')
                    data_pag_table = columns[3].text.strip(' ')
                    qty_stock = columns[4].text.strip(' ')
                    dividends = pd.concat([dividends, pd.DataFrame.from_records([{'Data': ult_data_table, 'Valor': valor_table, 'Tipo': type_table, 'Data de Pagamento': data_pag_table, 'Por quantas ações': qty_stock}])])

            dividends.head(20)
            dividends['Valor'] = [x.replace(',','.') for x in dividends['Valor']]
            dividends = dividends.astype({'Valor': float})
            dividends = dividends.drop(columns=['Por quantas ações'])
            dividends.set_index('Tipo', inplace=True)
            dividends = dividends.rename(columns={'Data': 'Registro', 'Data de Pagamento': 'Pagamento'})
    
            dividends['Ano'] = pd.to_datetime(dividends['Registro'], dayfirst=True).dt.year.astype(str) 
            dividends['Ano'] = dividends['Ano'].str.replace(',', '')

            self.dv = dividends
        else:
            st.warning(f"Não foi possível obter dados de {symbol}")
            st.stop()

        # Obtendo o total de dividendos por ano
        self.total_dv_year = dividends.groupby('Ano')['Valor'].sum().reset_index()

    def dividends_chart(self, symbol: str) -> None:
        """Gera gráfico de dividendos"""
        st.subheader(f"Dividendos {symbol}")
        
        fig_dividends = go.Figure()
        fig_dividends.add_bar(x=self.total_dv_year['Ano'], y=self.total_dv_year['Valor'], marker_color='palegreen')

        fig_dividends.update_layout(
            xaxis_title='Ano',
            yaxis_title='Valor (R$)',
        )

        for i, ano in enumerate(self.total_dv_year['Ano']):
            fig_dividends.add_annotation(
                x=ano,
                y=self.total_dv_year['Valor'].iloc[i],
                text=f"R$ {self.total_dv_year['Valor'].iloc[i]:,.2f}",
                showarrow=True,
                arrowhead=1,
            )
        st.plotly_chart(fig_dividends)
        with st.expander("Histórico de dividendos"):
            st.dataframe(self.dv, width=850, height=350)
