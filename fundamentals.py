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

    def ticker(self) -> str:
        """Retorna o código de negociação"""
        ticker_code = self.df_fundamental['Papel'].values[0]
        return str(ticker_code)
        
    def name(self) -> str:
        """Retorna o nome do ativo"""
        ticker_name = self.df_fundamental['Empresa'].values[0]
        return str(ticker_name)
    
    def dividend_yield(self) -> str:
        """Retorna o dividend yield"""
        ticker_dy = self.df_fundamental['Div_Yield'].values[0]
        return str(ticker_dy)
    
    def sector(self) -> str:
        """Retorna o setor do ativo"""
        ticker_sector = self.df_fundamental['Setor'].values[0]
        return str(ticker_sector)

    def price(self) -> str:
        """Retorna o preço atual do ativo"""
        ticker_price = self.df_fundamental['Cotacao'].values[0]
        return str(ticker_price)
    
    def pl(self) -> str:
        """Retorna o preço sobre lucro da ação"""
        ticker_pl = float(self.df_fundamental['PL'].values[0])
        ticker_pl = ticker_pl / 100
        return f"{ticker_pl:.2f}"
    
    def pvp(self) -> str:
        """Retorna o preço sobre valor patrimonial da ação"""
        ticker_pvp = float(self.df_fundamental['PVP'].values[0])
        ticker_pvp = ticker_pvp / 100
        return f"{ticker_pvp:.2f}"

    def psr(self) -> str:
        """Retorna o preço da ação em relação as vendas"""
        ticker_psr = float(self.df_fundamental['PSR'].values[0])
        ticker_psr = ticker_psr / 100
        return f"{ticker_psr:.2f}"

    def ev_ebitda(self) -> str:
        """Retorna o valor da empresa sobre EBITDA"""
        ticker_evebitda = float(self.df_fundamental['EV_EBITDA'].values[0])
        ticker_evebitda = ticker_evebitda / 100
        return f"{ticker_evebitda:.2f}"

    def ev_ebit(self) -> str:
        """Retorna o valor da empresa sobre EBIT"""
        ticker_evebit = float(self.df_fundamental['EV_EBIT'].values[0])
        ticker_evebit = ticker_evebit / 100
        return f"{ticker_evebit:.2f}"

    def lpa(self) -> str:
        """Retorna o lucro por ação"""
        ticker_lpa = float(self.df_fundamental['LPA'].values[0])
        ticker_lpa = ticker_lpa / 100
        return f"{ticker_lpa:.2f}"

    def vpa(self) -> str:
        """Retorna o valor patrimonial por ação"""
        ticker_vpa = float(self.df_fundamental['VPA'].values[0])
        ticker_vpa = ticker_vpa / 100
        return f"{ticker_vpa:.2f}"

    def marg_bruta(self) -> str:
        """Retorna a margem bruta"""
        ticker_marg_bruta = self.df_fundamental['Marg_Bruta'].values[0]
        return str(ticker_marg_bruta)

    def marg_ebit(self) -> str:
        """Retorna a margem ebit"""
        ticker_marg_ebit = self.df_fundamental['Marg_EBIT'].values[0]
        return str(ticker_marg_ebit)

    def marg_liquida(self) -> str:
        """Retorna a margem líquida"""
        ticker_marg_liquida = self.df_fundamental['Marg_Liquida'].values[0]
        return str(ticker_marg_liquida)

    def roic(self) -> str:
        """Retorna o retorno sobre capital investido"""
        ticker_roic = self.df_fundamental['ROIC'].values[0]
        return str(ticker_roic)

    def roe(self) -> str:
        """Retorna o retorno sobre patrimônio líquido"""
        ticker_roe = self.df_fundamental['ROE'].values[0]
        return str(ticker_roe)

    def div_bruta_patrim(self) -> str:
        """Retorna a divida bruta patrimonial"""
        ticker_div_bruta_patrim = float(self.df_fundamental['Div_Br_Patrim'].values[0])
        ticker_div_bruta_patrim = ticker_div_bruta_patrim / 100
        return f"{ticker_div_bruta_patrim:.2f}"
