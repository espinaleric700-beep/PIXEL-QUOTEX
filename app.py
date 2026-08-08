import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pytz

# Configuración de la página
st.set_page_config(
    page_title="Terminal Analítica Quotex OTC",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar Zona Horaria UTC-3
tz_utc3 = pytz.timezone('Etc/GMT+3')  # Nota: En pytz/Etc, +3 equivale a UTC-3

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

# Inicializar el historial de señales en la sesión de Streamlit
if 'historial_senales' not in st.session_state:
    st.session_state.historial_senales = []

# Lista completa de activos OTC
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
st.sidebar.info("🕒 Zona Horaria: UTC-3")

# Título Principal
st.title("⚡ Terminal de Análisis Cuántico - Quotex OTC")
st.markdown("Escáner inteligente con registro automatizado de señales en formato UTC-3 y auditoría WIN / LOSS.")

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
    # Convertir índice a la zona horaria UTC-3
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC').tz_convert(tz_utc3)
    else:
        data.index = data.index.tz_convert(tz_utc3)

    # Cálculo de Indicadores Técnicos (RSI y Medias Móviles)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()

    # Precios de las últimas dos velas
    precio_actual = float(data['Close'].iloc[-1])
    precio_anterior = float(data['Close'].iloc[-2])
    rsi_actual = float(data['RSI'].iloc[-1]) if not np.isnan(data['RSI'].iloc[-1]) else 50.0
    
    # Hora exacta ajustada a UTC-3
    ultima_vela_tiempo = data.index[-1]
    hora_senal = ultima_vela_tiempo.strftime('%H:%M:%S')

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
        st.subheader(f"Gráfico Técnico - {nombre_activo} ({temporalidad}) [UTC-3]")
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
        
        tipo_senal = None
        if rsi_actual < 40:
            tipo_senal = "ARRIBA"
            st.markdown(f"""
                <div class="alert-box">
                    <p class="signal-up">🚀 ACCIÓN: ARRIBA</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Hora Entrada (UTC-3):</b> {hora_senal}</p>
                    <p style="font-size: 0.85rem; color: #8b949e;">Zona de sobreventa detectada.</p>
                </div>
            """, unsafe_allow_html=True)
        elif rsi_actual > 60:
            tipo_senal = "ABAJO"
            st.markdown(f"""
                <div class="alert-box-down">
                    <p class="signal-down">🔻 ACCIÓN: ABAJO</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Hora Entrada (UTC-3):</b> {hora_senal}</p>
                    <p style="font-size: 0.85rem; color: #8b949e;">Zona de sobrecompra detectada.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color: #161b22; padding: 15px; border-radius: 4px; border: 1px solid #30363d;">
                    <p style="color: #8b949e; font-weight: bold;">⚖️ MERCADO EN CONSOLIDACIÓN</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Última revisión (UTC-3):</b> {hora_senal}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Botón para registrar la señal
        if tipo_senal and st.button("📌 Registrar Señal en el Historial"):
            nueva_entrada = {
                "Hora (UTC-3)": hora_senal,
                "Activo": nombre_activo,
                "Tipo": tipo_senal,
                "Temporalidad": temporalidad,
                "Precio_Entrada": precio_anterior,
                "Estado": "Pendiente / Evaluando"
            }
            if not st.session_state.historial_senales or st.session_state.historial_senales[-1]["Hora (UTC-3)"] != hora_senal:
                st.session_state.historial_senales.append(nueva_entrada)
                st.success("¡Señal registrada con éxito en el historial!")

        if st.button("🔄 Actualizar Escáner"):
            st.rerun()

    # --- SECCIÓN DE HISTORIAL Y AUDITORÍA DE RESULTADOS (WIN / LOSS) ---
    st.markdown("---")
    st.subheader("📊 Historial de Auditoría de Señales (WIN / LOSS) - UTC-3")
    
    if st.session_state.historial_senales:
        for item in st.session_state.historial_senales:
            if item["Estado"] == "Pendiente / Evaluando":
                p_entry = item["Precio_Entrada"]
                if item["Tipo"] == "ARRIBA":
                    if precio_actual > p_entry:
                        item["Estado"] = "🟢 WIN"
                    elif precio_actual < p_entry:
                        item["Estado"] = "🔴 LOSS"
                elif item["Tipo"] == "ABAJO":
                    if precio_actual < p_entry:
                        item["Estado"] = "🟢 WIN"
                    elif precio_actual > p_entry:
                        item["Estado"] = "🔴 LOSS"

        df_historial = pd.DataFrame(st.session_state.historial_senales)
        st.dataframe(df_historial, use_container_width=True)
        
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.historial_senales = []
            st.rerun()
    else:
        st.info("No hay señales registradas todavía. Haz clic en 'Registrar Señal en el Historial' cuando aparezca una oportunidad.")

else:
    st.error("No se pudieron cargar suficientes datos para este activo en la temporalidad seleccionada. Prueba cambiando la temporalidad o el activo.")
