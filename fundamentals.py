from functions import Market
import fundamentus
import pandas as pd

class Fundamental:
    """Coleta os dados fundamentalistas das ações"""
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.df_fundamental = fundamentus.get_papel(symbol)
    
    def table(self, symbol: str) -> pd.DataFrame:
        self.df_fundamental = fundamentus.get_papel(symbol)
        return self.df_fundamental
        
    def name(self) -> str:
        ticker_name = self.df_fundamental['Empresa'].values[0]
        return str(ticker_name)
    
    def dividend_yield(self) -> str:
        ticker_dy = self.df_fundamental['Div_Yield'].values[0]
        return str(ticker_dy)
    
    def sector(self) -> str:
        ticker_sector = self.df_fundamental['Setor'].values[0]
        return str(ticker_sector)