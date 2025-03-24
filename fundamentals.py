from pynvest.scrappers.fundamentus import Fundamentus

stock_data = Fundamentus()

class Fundamental:
    """Coletar dados fundamentalistas das ações"""
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.df_fundamental = stock_data.coleta_indicadores_de_ativo(symbol)

    def ticker(self) -> str:
        """Retorna o código de negociação"""
        ticker_code = self.df_fundamental['nome_papel'].values[0]
        return str(ticker_code)

    def name(self) -> str:
        """Retorna o nome do ativo"""
        ticker_name = self.df_fundamental['nome_empresa'].values[0]
        return str(ticker_name)

    def variation(self) -> str:
        """Variação diária do preço do ativo"""
        ticker_variation = self.df_fundamental["pct_var_dia"].values[0]
        return str(ticker_variation)

    def dividend_yield(self) -> str:
        """Retorna o dividend yield"""
        ticker_dy = self.df_fundamental['vlr_ind_div_yield'].values[0]
        return str(ticker_dy)

    def sector(self) -> str:
        """Retorna o setor do ativo"""
        ticker_sector = self.df_fundamental['nome_setor'].values[0]
        return str(ticker_sector)

    def price(self) -> str:
        """Retorna o preço atual do ativo"""
        ticker_price = self.df_fundamental['vlr_cot'].values[0]
        return str(ticker_price)

    def pl(self) -> str:
        """Retorna o preço sobre lucro da ação"""
        ticker_pl = self.df_fundamental['vlr_ind_p_sobre_l'].values[0]
        return str(ticker_pl)

    def pvp(self) -> str:
        """Retorna o preço sobre valor patrimonial da ação"""
        ticker_pvp = self.df_fundamental['vlr_ind_p_sobre_vp'].values[0]
        return str(ticker_pvp)

    def psr(self) -> str:
        """Retorna o preço da ação em relação as vendas"""
        ticker_psr = self.df_fundamental['vlr_ind_psr'].values[0]
        return str(ticker_psr)

    def ev_ebitda(self) -> str:
        """Retorna o valor da empresa sobre EBITDA"""
        ticker_evebitda = self.df_fundamental['vlr_ind_ev_sobre_ebitda'].values[0]
        return str(ticker_evebitda)

    def ev_ebit(self) -> str:
        """Retorna o valor da empresa sobre EBIT"""
        ticker_evebit = self.df_fundamental['vlr_ind_ev_sobre_ebit'].values[0]
        return str(ticker_evebit)

    def lpa(self) -> str:
        """Retorna o lucro por ação"""
        ticker_lpa = self.df_fundamental['vlr_ind_lpa'].values[0]
        return str(ticker_lpa)

    def vpa(self) -> str:
        """Retorna o valor patrimonial por ação"""
        ticker_vpa = self.df_fundamental['vlr_ind_vpa'].values[0]
        return str(ticker_vpa)

    def marg_bruta(self) -> str:
        """Retorna a margem bruta"""
        ticker_marg_bruta = self.df_fundamental['vlr_ind_margem_bruta'].values[0]
        return str(ticker_marg_bruta)

    def marg_ebit(self) -> str:
        """Retorna a margem ebit"""
        ticker_marg_ebit = self.df_fundamental['vlr_ind_margem_ebit'].values[0]
        return str(ticker_marg_ebit)

    def marg_liquida(self) -> str:
        """Retorna a margem líquida"""
        ticker_marg_liquida = self.df_fundamental['vlr_ind_margem_liq'].values[0]
        return str(ticker_marg_liquida)

    def roic(self) -> str:
        """Retorna o retorno sobre capital investido"""
        ticker_roic = self.df_fundamental['vlr_ind_roic'].values[0]
        return str(ticker_roic)

    def roe(self) -> str:
        """Retorna o retorno sobre patrimônio líquido"""
        ticker_roe = self.df_fundamental['vlr_ind_roe'].values[0]
        return str(ticker_roe)

    def div_bruta_patrim(self) -> str:
        """Retorna a divida bruta patrimonial"""
        ticker_div_bruta_patrim = self.df_fundamental['vlr_ind_divida_bruta_sobre_patrim'].values[0]
        return str(ticker_div_bruta_patrim)

class FII_Data:
    """Coletar dados fundamentalistas de fundos imobiliários"""
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.df_fundamental = stock_data.coleta_indicadores_de_ativo(symbol)

    def fii_ticker(self) -> str:
        """Retorna o código de negociação"""
        ticker_code = self.df_fundamental['fii'].values[0]
        return str(ticker_code)

    def fii_name(self) -> str:
        """Retorna o nome do fii"""
        ticker_name = self.df_fundamental['nome_fii'].values[0]
        return str(ticker_name)

    def fii_variation(self) -> str:
        """Retorna a variação diária do valor da cota"""
        ticker_variation = self.df_fundamental['pct_var_dia'].values[0]
        return str(ticker_variation)

    def fii_type(self) -> str:
        """Retorna o tipo de FII"""
        ticker_type = self.df_fundamental['tipo_mandato'].values[0]
        return str(ticker_type)

    def fii_value(self) -> str:
        """Valor da cota"""
        ticker_value = self.df_fundamental['vlr_cot'].values[0]
        return str(ticker_value)

    def fii_dy(self) -> str:
        """Dividend Yield do FII"""
        ticker_dy = self.df_fundamental['vlr_div_yield'].values[0]
        return str(ticker_dy)

    def fii_market_value(self) -> str:
        """Valor de mercado do FII"""
        ticker_market_value = self.df_fundamental['vlr_mercado'].values[0]
        return str(ticker_market_value)

    def fii_pvp(self) -> str:
        """Preço dividido pelo valor patrimonial"""
        ticker_pvp = self.df_fundamental['vlr_p_sobre_vp'].values[0]
        return str(ticker_pvp)
