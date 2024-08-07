import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import date, datetime, timedelta

class Market:
    """Classe para obter os dados de forma de investimento e ativo"""
    def __init__(self, market_name) -> None:
        self.market = market_name
    
    def get_stock_list(self):
        """Obtém lista de ativos para cada tipo de renda"""
        if self.market == 'Ações':
            stock_list = list(pd.read_excel('lists/listativos.xls')['Código'].values)  
            stock_list.sort()
            return [stock for stock in stock_list]
        elif self.market == 'Fundos Imobiliários':
            stock_list = list(pd.read_excel('lists/listafii.xls')['Código'].values)  
            stock_list.sort()
            return [stock for stock in stock_list]
        else:
            st.warning("Selecione um tipo de renda variável")
        return []
    
    def date_interval(self, date_start, date_final):
        """Seta o intervalo entre cada data"""
        self.date_start = date_start
        self.date_final = date_final
        interval = (self.date_start - self.date_final).total_seconds() / 86400
        return interval
    
    def get_stock_data(self, symbol):
        self.symbol_data = {}
        call_symbol = yf.Ticker(f'{symbol}').history(start=f"{self.date_start}", end=f"{self.date_final}")
        self.symbol_data[symbol] = pd.DataFrame(call_symbol)
        df = self.symbol_data[symbol]
        return df
    
    
     