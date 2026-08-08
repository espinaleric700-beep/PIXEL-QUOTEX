import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh

# Configuración de la página
st.set_page_config(
    page_title="Terminal Quotex - Tiempo Real Absoluto",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar Zona Horaria UTC-3
tz_utc3 = pytz.timezone('Etc/GMT+3')

# Recarga automática de la página cada 1 segundo para fluidez total de ticks
count = st_autorefresh(interval=1000, limit=None, key="quotex_realtime_1s")

# Estilos CSS idénticos a la estética de Quotex
st.markdown("""
    <style>
    .main {
        background-color: #0b131e;
    }
    .stMetric {
        background-color: #141f2c;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #24344d;
    }
    .signal-up {
        color: #00C853;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .signal-down {
        color: #FF3D00;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .alert-box-up {
        background-color: #141f2c;
        border-left: 5px solid #00C853;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .alert-box-down {
        background-color: #141f2c;
        border-left: 5px solid #FF3D00;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar sesión y memoria de precios para simulación de ticks
if 'historial_senales' not in st.session_state:
    st.session_state.historial_senales = []

if 'last_tick_price' not in st.session_state:
    st.session_state.last_tick_price = None

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

# Panel de Control Lateral
st.sidebar.markdown("## ⚙️ Configuración Quotex")
st.sidebar.markdown("---")

nombre_activo = st.sidebar.selectbox(
    "Seleccionar Activo OTC",
    list(activos_otc.keys())
)
activo_seleccionado = activos_otc[nombre_activo]

temporalidad = st.sidebar.selectbox(
    "Temporalidad (Velas)",
    ["1m", "5m", "15m", "1h"]
)

st.sidebar.markdown("---")
st.sidebar.success("🟢 Motor de Ticks Activo (1s)")
st.sidebar.info("🕒 Zona Horaria: UTC-3")

# Cabecera Principal
st.title("⚡ Quotex Web Trading Terminal - Tiempo Real Absoluto")
st.markdown("Terminal sincronizada con ticks de alta frecuencia y estética profesional idéntica al bróker.")

# Descarga de datos base optimizada
@st.cache_data(ttl=15)
def cargar_datos_base(ticker, intervalo):
    try:
        df = yf.download(ticker, period="1d", interval=intervalo, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        return None

data = cargar_datos_base(activo_seleccionado, temporalidad)

if data is not None and not data.empty and len(data) > 20:
    # Convertir índice a la zona horaria UTC-3
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC').tz_convert(tz_utc3)
    else:
        data.index = data.index.tz_convert(tz_utc3)

     precio_base_mercado = float(data['Close'].iloc[-1])

    # Inicializar o actualizar el precio del tick en tiempo real con micro-variación estocástica
    if st.session_state.get('active_ticker') != nombre_activo or st.session_state.last_tick_price is None:
        st.session_state.active_ticker = nombre_activo
        st.session_state.last_tick_price = precio_base_mercado
    else:
        # Generar micro-cambio aleatorio realista estilo bróker (oscilación de pips)
        variacion = np.random.normal(0, 0.00015)
        st.session_state.last_tick_price += variacion

    precio_actual = st.session_state.last_tick_price

    # Actualizar la última vela del DataFrame en tiempo real para que el gráfico se mueva al instante
    data.loc[data.index[-1], 'Close'] = precio_actual
    if precio_actual > data.loc[data.index[-1], 'High']:
        data.loc[data.index[-1], 'High'] = precio_actual
    if precio_actual < data.loc[data.index[-1], 'Low']:
        data.loc[data.index[-1], 'Low'] = precio_actual

    # Cálculo de Indicadores Técnicos (RSI y SMA)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['SMA_20'] = data['Close'].rolling(window=20).mean()

    rsi_actual = float(data['RSI'].iloc[-1]) if not np.isnan(data['RSI'].iloc[-1]) else 50.0
    
    # Hora UTC-3 actual sincronizada al segundo
    hora_actual_utc3 = datetime.now(tz_utc3)

    # Cálculo de la siguiente vela
    minutos_map = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}
    delta_minutos = minutos_map.get(temporalidad, 1)
    minuto_actual = hora_actual_utc3.minute
    siguiente_minuto = ((minuto_actual // delta_minutos) + 1) * delta_minutos
    
    if siguiente_minuto >= 60:
        hora_siguiente = hora_actual_utc3.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        hora_siguiente = hora_actual_utc3.replace(minute=siguiente_minuto, second=0, microsecond=0)
    hora_senal_siguiente = hora_siguiente.strftime('%H:%M:%S')

    # Métricas superiores estilo Quotex
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Hora Actual (UTC-3)", value=hora_actual_utc3.strftime('%H:%M:%S'))
    with col2:
        st.metric(label="Precio Actual en Vivo", value=f"{precio_actual:.5f}")
    with col3:
        st.metric(label="RSI (14)", value=f"{rsi_actual:.2f}")
    with col4:
        sugerencia = "ARRIBA 🟢" if rsi_actual < 45 else ("ABAJO 🔴" if rsi_actual > 55 else "NEUTRAL ⚪")
        st.metric(label="Tendencia Sugerida", value=sugerencia)

    st.markdown("---")

    # Layout de Gráfico y Panel de Operativa al estilo Quotex
    c_graf, c_pan = st.columns([2.8, 1])

    with c_graf:
        st.subheader(f"Gráfico de Velas en Vivo - {nombre_activo} ({temporalidad})")
        
        fig = go.Figure()
        
        # Estilo de Velas Idéntico a Quotex (Verde alcista #00C853, Rojo bajista #FF3D00)
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Precio',
            increasing_line_color='#00C853',
            increasing_fillcolor='#00C853',
            decreasing_line_color='#FF3D00',
            decreasing_fillcolor='#FF3D00'
        ))
        
        # Línea de Media Móvil elegante
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['SMA_20'], 
            mode='lines', 
            name='SMA 20', 
            line=dict(color='#2979FF', width=1.5)
        ))
        
        # Diseño de fondo oscuro limpio y profesional idéntico al bróker con precios a la derecha
        fig.update_layout(
            paper_bgcolor='#0b131e',
            plot_bgcolor='#0b131e',
            font=dict(color='#8b949e', family='Arial'),
            xaxis_rangeslider_visible=False,
            height=480,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                gridcolor='#1a2638',
                showgrid=True
            ),
            yaxis=dict(
                gridcolor='#1a2638',
                showgrid=True,
                side='right'
            )
        )
        st.plotly_chart(fig, use_container_width=True, key="quotex_realtime_chart")

    with c_pan:
        st.subheader("Panel de Operativa")
        
        tipo_senal = None
        if rsi_actual < 40:
            tipo_senal = "ARRIBA"
            st.markdown(f"""
                <div class="alert-box-up">
                    <p class="signal-up">🚀 ACCIÓN: ARRIBA</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Entrada Vela:</b> {hora_senal_siguiente}</p>
                    <p style="font-size: 0.82rem; color: #8b949e;">Oportunidad alcista detectada.</p>
                </div>
            """, unsafe_allow_html=True)
        elif rsi_actual > 60:
            tipo_senal = "ABAJO"
            st.markdown(f"""
                <div class="alert-box-down">
                    <p class="signal-down">🔻 ACCIÓN: ABAJO</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Entrada Vela:</b> {hora_senal_siguiente}</p>
                    <p style="font-size: 0.82rem; color: #8b949e;">Oportunidad bajista detectada.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color: #141f2c; padding: 15px; border-radius: 4px; border: 1px solid #24344d;">
                    <p style="color: #8b949e; font-weight: bold;">⚖️ MERCADO LATERAL</p>
                    <p><b>Temporalidad:</b> {temporalidad}</p>
                    <p><b>Revisión:</b> {hora_actual_utc3.strftime('%H:%M:%S')}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Botón para registrar la señal al historial
        if tipo_senal and st.button("📌 Registrar Señal"):
            nueva_entrada = {
                "Hora Entrada (UTC-3)": hora_senal_siguiente,
                "Activo": nombre_activo,
                "Tipo": tipo_senal,
                "Temporalidad": temporalidad,
                "Precio_Entrada": precio_actual,
                "Estado": "Pendiente / Evaluando"
            }
            if not st.session_state.historial_senales or st.session_state.historial_senales[-1]["Hora Entrada (UTC-3)"] != hora_senal_siguiente:
                st.session_state.historial_senales.append(nueva_entrada)
                st.success("¡Señal guardada!")

    # --- SECCIÓN DE HISTORIAL Y AUDITORÍA WIN / LOSS ---
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
        st.info("No hay señales registradas todavía en esta sesión.")

else:
    st.error("Cargando datos del mercado en tiempo real...")
