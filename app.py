import pandas as pd
import numpy as np

class EstrategiasQuotex:
    """
    Módulo cuantitativo modular con la lógica de ejecución detallada 
    de las 10 estrategias profesionales para Quotex.
    """

    @staticmethod
    def breakout_retest(df: pd.DataFrame, window: int = 20) -> str:
        """
        1. Estrategia de Ruptura y Reboque (Breakout & Retest)
        Retorna: 'CALL', 'PUT' o 'NEUTRAL'
        """
        if len(df) < window + 3:
            return "NEUTRAL"
        
        # Calcular soporte y resistencia dinámicos basados en N velas anteriores
        resistencia = df['High'].iloc[-window:-1].max()
        soporte = df['Low'].iloc[-window:-1].min()
        
        close_actual = df['Close'].iloc[-1]
        low_actual = df['Low'].iloc[-1]
        high_actual = df['High'].iloc[-1]
        open_actual = df['Open'].iloc[-1]
        
        # Validación CALL: Ruptura previa de resistencia y retest con mecha de rechazo alcista
        cuerpo = abs(close_actual - open_actual)
        rango = high_actual - low_actual
        mecha_inferior = min(open_actual, close_actual) - low_actual
        
        if close_actual >= resistencia and low_actual <= resistencia and (mecha_inferior >= 0.4 * rango if rango > 0 else False):
            return "CALL"
            
        # Validación PUT: Ruptura previa de soporte y retest con mecha de rechazo bajista
        mecha_superior = high_actual - max(open_actual, close_actual)
        if close_actual <= soporte and high_actual >= soporte and (mecha_superior >= 0.4 * rango if rango > 0 else False):
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def bollinger_rsi(df: pd.DataFrame) -> str:
        """
        2. Estrategia RSI + Bandas de Bollinger
        Requisitos en el DataFrame: columnas 'Close', 'BB_Lower', 'BB_Upper', 'RSI'
        """
        if len(df) < 2:
            return "NEUTRAL"
            
        close = df['Close'].iloc[-1]
        bb_lower = df['BB_Lower'].iloc[-1]
        bb_upper = df['BB_Upper'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        
        if close <= bb_lower and rsi <= 30:
            return "CALL"
        elif close >= bb_upper and rsi >= 70:
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def ema_crossover(df: pd.DataFrame) -> str:
        """
        3. Estrategia de Cruce de Medias Móviles (EMA 9 / EMA 21)
        """
        if len(df) < 3:
            return "NEUTRAL"
            
        ema9 = df['EMA_9']
        ema21 = df['EMA_21']
        
        # Vela recién cerrada [1] y vela anterior [2]
        if ema9.iloc[-1] > ema21.iloc[-1] and ema9.iloc[-2] <= ema21.iloc[-2]:
            return "CALL"
        elif ema9.iloc[-1] < ema21.iloc[-1] and ema9.iloc[-2] >= ema21.iloc[-2]:
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def engolfing_pattern(df: pd.DataFrame) -> str:
        """
        4. Estrategia de Patrones Envolventes (Engolfing Patterns)
        """
        if len(df) < 3:
            return "NEUTRAL"
            
        o1, c1 = df['Open'].iloc[-1], df['Close'].iloc[-1]
        o2, c2 = df['Open'].iloc[-2], df['Close'].iloc[-2]
        
        # Vela [1] es la actual, Vela [2] es la anterior
        is_vela1_alcista = c1 > o1
        is_vela2_bajista = c2 < o2
        body_engulf_call = (o1 <= c2) and (c1 >= o2) and is_vela1_alcista and is_vela2_bajista
        
        if body_engulf_call:
            return "CALL"
            
        is_vela1_bajista = c1 < o1
        is_vela2_alcista = c2 > o2
        body_engulf_put = (o1 >= c2) and (c1 <= o2) and is_vela1_bajista and is_vela2_alcista
        
        if body_engulf_put:
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def support_resistance_rejection(df: pd.DataFrame, window: int = 15) -> str:
        """
        5. Estrategia de Rechazo en Soportes y Resistencias
        """
        if len(df) < window:
            return "NEUTRAL"
            
        soporte = df['Low'].iloc[-window:-1].min()
        resistencia = df['High'].iloc[-window:-1].max()
        
        o, h, l, c = df['Open'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1], df['Close'].iloc[-1]
        rango = h - l
        if rango == 0:
            return "NEUTRAL"
            
        mecha_inf = min(o, c) - l
        mecha_sup = h - max(o, c)
        
        # Condición CALL
        if l <= soporte and c > soporte and (mecha_inf / rango >= 0.6):
            return "CALL"
            
        # Condición PUT
        if h >= resistencia and c < resistencia and (mecha_sup / rango >= 0.6):
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def stochastic_oscillator(df: pd.DataFrame) -> str:
        """
        6. Estrategia del Oscilador Estocástico en Niveles Clave
        Requisitos: columnas 'Stoch_K', 'Stoch_D'
        """
        if len(df) < 3:
            return "NEUTRAL"
            
        k_curr, d_curr = df['Stoch_K'].iloc[-1], df['Stoch_D'].iloc[-1]
        k_prev, d_prev = df['Stoch_K'].iloc[-2], df['Stoch_D'].iloc[-2]
        
        if k_curr < 20 and d_curr < 20 and k_curr > d_curr and k_prev <= d_prev:
            return "CALL"
        elif k_curr > 80 and d_curr > 80 and k_curr < d_curr and k_prev >= d_prev:
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def macd_divergence(df: pd.DataFrame) -> str:
        """
        7. Estrategia de Divergencias con MACD
        """
        if len(df) < 20:
            return "NEUTRAL"
            
        # Simplificación de control de mínimos/máximos relativos recientes
        precio_min_actual = df['Low'].iloc[-5:].min()
        precio_min_previo = df['Low'].iloc[-15:-5].min()
        
        macd_actual = df['MACD_Hist'].iloc[-5:].min()
        macd_previo = df['MACD_Hist'].iloc[-15:-5].min()
        
        # Divergencia Alcista: Precio hace Lower Low, MACD hace Higher Low
        if precio_min_actual < precio_min_previo and macd_actual > macd_previo:
            return "CALL"
            
        precio_max_actual = df['High'].iloc[-5:].max()
        precio_max_previo = df['High'].iloc[-15:-5].max()
        macd_max_actual = df['MACD_Hist'].iloc[-5:].max()
        macd_max_previo = df['MACD_Hist'].iloc[-15:-5].max()
        
        # Divergencia Bajista: Precio hace Higher High, MACD hace Lower High
        if precio_max_actual > precio_max_previo and macd_max_actual < macd_max_previo:
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def range_channel(df: pd.DataFrame) -> str:
        """
        8. Estrategia de Operatividad en Rango / Canales Laterales (Requiere ADX < 20)
        """
        if len(df) < 20 or 'ADX' not in df.columns:
            return "NEUTRAL"
            
        adx = df['ADX'].iloc[-1]
        if adx >= 20:
            return "NEUTRAL"
            
        canal_sup = df['High'].iloc[-20:-1].max()
        canal_inf = df['Low'].iloc[-20:-1].min()
        
        close = df['Close'].iloc[-1]
        low = df['Low'].iloc[-1]
        high = df['High'].iloc[-1]
        
        if low <= canal_inf and close > canal_inf:
            return "CALL"
        elif high >= canal_sup and close < canal_sup:
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def pin_bar_reversal(df: pd.DataFrame) -> str:
        """
        9. Estrategia de Velas Martillo y Estrella Fugaz (Pin Bar Reversal)
        """
        if len(df) < 4:
            return "NEUTRAL"
            
        o, h, l, c = df['Open'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1], df['Close'].iloc[-1]
        cuerpo = abs(c - o)
        rango = h - l
        if rango == 0:
            return "NEUTRAL"
            
        mecha_inf = min(o, c) - l
        mecha_sup = h - max(o, c)
        
        # Validar tendencia bajista previa de 3 velas
        trend_bajista = (df['Close'].iloc[-2] < df['Open'].iloc[-2]) and \
                        (df['Close'].iloc[-3] < df['Open'].iloc[-3]) and \
                        (df['Close'].iloc[-4] < df['Open'].iloc[-4])
                        
        if trend_bajista and (mecha_inf >= 2 * cuerpo) and (mecha_sup <= 0.1 * rango):
            return "CALL"
            
        # Validar tendencia alcista previa de 3 velas
        trend_alcista = (df['Close'].iloc[-2] > df['Open'].iloc[-2]) and \
                        (df['Close'].iloc[-3] > df['Open'].iloc[-3]) and \
                        (df['Close'].iloc[-4] > df['Open'].iloc[-4])
                        
        if trend_alcista and (mecha_sup >= 2 * cuerpo) and (mecha_inf <= 0.1 * rango):
            return "PUT"
            
        return "NEUTRAL"

    @staticmethod
    def trend_following(df: pd.DataFrame) -> str:
        """
        10. Estrategia de Seguimiento de Tendencia (EMA 200 + EMA 20)
        """
        if len(df) < 200:
            return "NEUTRAL"
            
        close = df['Close'].iloc[-1]
        ema200 = df['EMA_200'].iloc[-1]
        ema20 = df['EMA_20'].iloc[-1]
        low = df['Low'].iloc[-1]
        high = df['High'].iloc[-1]
        
        # Tendencia alcista macro (Precio > EMA 200) con retroceso a EMA 20
        if close > ema200 and low <= ema20 and close > ema20:
            return "CALL"
            
        # Tendencia bajista macro (Precio < EMA 200) con rebote a EMA 20
        if close < ema200 and high >= ema20 and close < ema20:
            return "PUT"
            
        return "NEUTRAL"
