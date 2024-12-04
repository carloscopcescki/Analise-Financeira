import pandas as pd
import yfinance as yf
import streamlit as st

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