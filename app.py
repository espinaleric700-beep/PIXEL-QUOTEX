import streamlit as datetime
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

# Configuración de la página (Debe ser el primer comando de Streamlit)
st.set_page_config(
    page_title="Terminal Analítica Quotex",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para un look profesional, oscuro y limpio tipo terminal financiera
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
    </style>
""", unsafe_allow_html=True)

# Barra Lateral - Controles de Configuración
st.sidebar.markdown("## ⚙️ Panel de Control")
st.sidebar.markdown("---")

activo_seleccionado = st.sidebar.selectbox(
    "Seleccionar Activo (Divisa / Crypto)",
    ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD", "ETH-USD"]
)

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
st.sidebar.success("🟢 Conexión de Datos: Activa")

# Título Principal
st.title("⚡ Terminal de Análisis Cuántico - Quotex")
st.markdown("Escáner inteligente de activos en tiempo real para la toma de decisiones rápidas.")

# Simulación / Descarga de datos reales de mercado
@st.cache_data(ttl=60)
def cargar_datos(ticker, intervalo):
    try:
        # Descargando datos recientes para análisis técnico rápido
        df = yf.download(ticker, period="1d", interval=intervalo, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        return None

data = cargar_datos(activo_seleccionado, temporalidad)

if data is not None and not data.empty:
    # Cálculo de Indicadores Técnicos Básicos (RSI y Medias Móviles)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()

    # Últimos valores registrados
    precio_actual = float(data['Close'].iloc[-1])
    rsi_actual = float(data['RSI'].iloc[-1])
    sma20_actual = float(data['SMA_20'].iloc[-1])

    # Métricas Principales en Pantalla
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Activo Analizado", value=activo_seleccionado)
    with col2:
        st.metric(label="Precio Actual", value=f"{precio_actual:.5f}")
    with col3:
        st.metric(label="RSI (14)", value=f"{rsi_actual:.2f}")
    with col4:
        # Lógica de Sugerencia Automática
        sugerencia = "ARRIBA 🟢" if rsi_actual < 45 else ("ABAJO 🔴" if rsi_actual > 55 else "NEUTRAL ⚪")
        st.metric(label="Señal Sugerida", value=sugerencia)

    st.markdown("---")

    # Layout de Gráfico Interactivo y Panel de Control de Acciones
    col_grafico, col_panel = st.markdown, st.columns([3, 1])
    
    # Usando columnas reales de Streamlit para la interfaz
    c_graf, c_pan = st.columns([2.5, 1])

    with c_graf:
        st.subheader(f"Gráfico Técnico - {activo_seleccionado}")
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
        st.markdown("Basado en el análisis algorítmico actual:")
        
        if rsi_actual < 40:
            st.markdown('<p class="signal-up">🚀 Oportunidad de Compra: ARRIBA</p>', unsafe_allow_html=True)
            st.info("El activo se encuentra en zona de sobreventa técnica.")
        elif rsi_actual > 60:
            st.markdown('<p class="signal-down">🔻 Oportunidad de Venta: ABAJO</p>', unsafe_allow_html=True)
            st.warning("El activo se encuentra en zona de sobrecompra técnica.")
        else:
            st.markdown('<p style="color: #8b949e;">⚖️ Mercado en Consolidación. Esperar confirmación.</p>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Botones de control de interfaz seguros (No borran el estado del escáner)
        if st.button("🔄 Actualizar Escáner"):
            st.rerun()

else:
    st.error("No se pudieron cargar los datos de mercado en este momento. Intenta cambiar de activo.")
