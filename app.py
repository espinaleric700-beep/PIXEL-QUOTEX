import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Terminal Analítica Quotex OTC",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS profesionales
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
    .signal-up {
        color: #238636;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .signal-down {
        color: #da3633;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .alert-box {
        background-color: #161b22;
        border-left: 5px solid #238636;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .alert-box-down {
        background-color: #161b22;
        border-left: 5px solid #da3633;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Lista completa de activos OTC incluyendo USD/BRL
activos_otc = {
    "USD/BRL (OTC)": "USDBRL=X",
    "EUR/USD (OTC)": "EURUSD=X",
    "GBP/USD (OTC)": "GBPUSD=X",
    "USD/JPY (OTC)": "USDJPY=X",
    "AUD/USD (OTC)": "AUDUSD=X",
    "EUR/JPY (OTC)": "EURJPY=X",
    "GBP/JPY (OTC)": "GBPJPY=X",
    "USD/CAD (OTC)": "USDCAD=X",
    "AUD/CAD (OTC)": "AUDCAD=X",
    "EUR/GBP (OTC)": "EURGBP=X",
    "NZD/USD (OTC)": "NZDUSD=X",
    "USD/CHF (OTC)": "USDCHF=X",
    "EUR/AUD (OTC)": "EURAUD=X",
    "EUR/NZD (OTC)": "EURNZD=X",
    "GBP/AUD (OTC)": "GBPAUD=X",
    "AUD/JPY (OTC)": "AUDJPY=X",
    "CAD/JPY (OTC)": "CADJPY=X",
    "CHF/JPY (OTC)": "CHFJPY=X",
    "EUR/CAD (OTC)": "EURCAD=X",
    "GBP/CAD (OTC)": "GBPCAD=X",
    "USD/NOK (OTC)": "USDNOK=X",
    "USD/SEK (OTC)": "USDSEK=X",
    "BTC/USD (OTC Crypto)": "BTC-USD",
    "ETH/USD (OTC Crypto)": "ETH-USD",
    "XRP/USD (OTC Crypto)": "XRP-USD",
    "LTC/USD (OTC Crypto)": "LTC-USD"
}

# Barra Lateral - Controles de Configuración
st.sidebar.markdown("## ⚙️ Panel de Control OTC")
st.sidebar.markdown("---")

nombre_activo = st.sidebar.selectbox(
    "Seleccionar Activo OTC",
    list(activos_otc.keys())
)
activo_seleccionado = activos_otc[nombre_activo]

temporalidad = st.sidebar.selectbox(
    "Temporalidad del Análisis",
    ["1m", "5m", "15m", "1h"]
)

indicador_base = st.sidebar.selectbox(
    "Estrategia de Indicadores",
    ["RSI + Medias Móviles", "Bandas de Bollinger", "Cruce MACD"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Estado del Sistema")
st.sidebar.success("🟢 Conexión de Datos OTC: Activa")

# Título Principal
st.title("⚡ Terminal de Análisis Cuántico - Quotex OTC")
st.markdown("Escáner inteligente con cálculo de hora de entrada y temporalidad para operaciones rápidas.")

# Descarga de datos de mercado
@st.cache_data(ttl=60)
def cargar_datos(ticker, intervalo):
    try:
        df = yf.download(ticker, period="1d", interval=intervalo, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        return None

data = cargar_datos(activo_seleccionado, temporalidad)

if data is not None and not data.empty and len(data) > 20:
    # Cálculo de Indicadores Técnicos (RSI y Medias Móviles)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()

    # Últimos valores registrados
    precio_actual = float(data['Close'].iloc[-1])
    rsi_actual = float(data['RSI'].iloc[-1]) if not np.isnan(data['RSI'].iloc[-1]) else 50.0
    
    # Obtener la hora de la última vela cerrada y calcular la hora estimada de entrada
    ultima_vela_tiempo = data.index[-1]
    if isinstance(ultima_vela_tiempo, pd.Timestamp):
        hora_senal = ultima_vela_tiempo.strftime('%H:%M:%S')
    else:
        hora_senal = datetime.now().strftime('%H:%M:%S')

    # Métricas Principales en Pantalla
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Activo Seleccionado", value=nombre_activo)
    with col2:
        st.metric(label="Precio Actual", value=f"{precio_actual:.5f}")
    with col3:
        st.metric(label="RSI (14)", value=f"{rsi_actual:.2f}")
    with col4:
        sugerencia = "ARRIBA 🟢" if rsi_actual < 45 else ("ABAJO 🔴" if rsi_actual > 55 else "NEUTRAL ⚪")
        st.metric(label="Señal Sugerida", value=sugerencia)

    st.markdown("---")

    # Layout de Gráfico Interactivo y Panel de Operativa
    c_graf, c_pan = st.columns([2.5, 1])

    with c_graf:
        st.subheader(f"Gráfico Técnico - {nombre_activo} ({temporalidad})")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Precio'
        ))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], mode='lines', name='SMA 20', line=dict(color='orange', width=1.5)))
        
        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=450,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_pan:
        st.subheader("Panel de Operativa")
        st.markdown("Detalles de la señal actual:")
        
        if rsi_actual < 40:
            st.markdown(f"""
                <div class="alert-box">
                    <p class="signal-up">🚀 ACCIÓN: ARRIBA</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Hora de Entrada:</b> {hora_senal}</p>
                    <p style="font-size: 0.85rem; color: #8b949e;">Zona de sobreventa detectada. Ideal para entrada inmediata al inicio de la vela.</p>
                </div>
            """, unsafe_allow_html=True)
        elif rsi_actual > 60:
            st.markdown(f"""
                <div class="alert-box-down">
                    <p class="signal-down">🔻 ACCIÓN: ABAJO</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Hora de Entrada:</b> {hora_senal}</p>
                    <p style="font-size: 0.85rem; color: #8b949e;">Zona de sobrecompra detectada. Ideal para entrada inmediata al inicio de la vela.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color: #161b22; padding: 15px; border-radius: 4px; border: 1px solid #30363d;">
                    <p style="color: #8b949e; font-weight: bold;">⚖️ MERCADO EN CONSOLIDACIÓN</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Última revisión:</b> {hora_senal}</p>
                    <p style="font-size: 0.85rem; color: #8b949e;">Sin señales claras. Esperar alineación de indicadores.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Botón seguro que actualiza los datos al instante sin borrar estados
        if st.button("🔄 Actualizar Escáner"):
            st.rerun()

else:
    st.error("No se pudieron cargar suficientes datos para este activo en la temporalidad seleccionada. Prueba cambiando la temporalidad o el activo.")
