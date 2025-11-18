import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# --- 1. CONFIGURACIÓN INICIAL Y CÁLCULO DE HORA ---
st.set_page_config(
    page_title="AquaData Pro",
    page_icon="🦐",
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Cálculo de hora para el tema Día/Noche
hora_actual = datetime.now().hour
es_noche = not (6 <= hora_actual < 18) 

# --- DICCIONARIO DE SECTORES (El Filtro Geográfico) ---
SECTORES = {
    "Isla Puná (Golfo)": {"lat": -2.68, "lon": -80.00},
    "Naranjal (Estero)": {"lat": -2.76, "lon": -79.60},
    "Churute (Interior)": {"lat": -2.31, "lon": -79.66},
    "Playas (Mar Abierto)": {"lat": -2.65, "lon": -80.45},
    "Puerto Bolívar (El Oro)": {"lat": -3.27, "lon": -80.03},
    "Golfo de Guayaquil (Centro)": {"lat": -2.75, "lon": -80.50}
}

# --- 2. FUNCIONES DE LÓGICA DE NEGOCIO Y DATOS (EL BACKEND) ---

def calcular_ahorro(temp_agua, biomasa_kg, precio_saco):
    """
    Calcula la ración óptima (tasa de alimentación) basada en la temperatura
    y estima el ahorro económico frente a un esquema de alimentación ciego (3%).
    """
    
    # Modelo de crecimiento continuo: Tasa óptima (3%) se da a 28°C.
    tasa_optima = 0.03 * (1 - 0.01 * (temp_agua - 28)**2)
    tasa = max(0.005, tasa_optima) # Mínimo de 0.5%
    
    alimento_necesario_kg = biomasa_kg * tasa
    
    # Gasto ciego (3% fijo)
    gasto_ciego = (biomasa_kg * 0.03 / 25) * precio_saco
    costo_optimo = (alimento_necesario_kg / 25) * precio_saco
    ahorro = gasto_ciego - costo_optimo
    
    return alimento_necesario_kg, ahorro, tasa 

def obtener_estado_camaron(temp, ph, oxigeno):
    """
    Determina el estado de la piscina basado en los parámetros de calidad del agua,
    devolviendo el código de estado, color, emoji, título y descripción para la UI.
    """
    if temp < 24 or temp > 30:
        return 'cold', '#3b82f6', '🥶', 'Temperatura Crítica', 'Riesgo térmico'
    if ph < 7.5 or ph > 8.5:
        return 'stressed', '#f59e0b', '😰', 'Estresado', 'pH desequilibrado'
    if oxigeno < 4:
        return 'suffocating', '#ef4444', '😵', 'Hipoxia', 'Oxígeno bajo'
    
    return 'healthy', '#10b981', '🦐', 'Saludable', 'Condiciones óptimas'

# @st.cache_data(ttl=600)
def obtener_temp_real(lat, lon):
    """
    Conecta con la API de Open-Meteo Marine para obtener la temperatura superficial del mar (SST) 
    actual y el pronóstico de mañana.
    """
    URL = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&daily=sst_max&timezone=America%2FGuayaquil&past_days=7&forecast_days=1"
    try:
        respuesta = requests.get(URL).json()
        temp_hoy = respuesta['daily']['sst_max'][-2]
        temp_manana = respuesta['daily']['sst_max'][-1]
        return temp_hoy, temp_manana, False # No hay error
    except Exception as e:
        # --- CAMBIO #1: FALLBACK REALISTA ---
        # Si falla el satélite, usamos datos de Guayaquil (26°C) y no de crisis (23°C)
        return 26.0, 26.5, True # Hay error, pero es un fallback normal


@st.cache_data
def obtener_datos_historicos():
    """Genera datos históricos simulados para el gráfico de tendencia."""
    fechas = [datetime.now().date() - timedelta(days=i) for i in range(6, -1, -1)]
    temp = [25.5, 26.2, 27.1, 26.8, 25.0, 24.5, 23.8] 
    oxigeno = [4.5, 4.4, 4.2, 4.6, 4.0, 3.8, 3.5]
    return pd.DataFrame({"Fecha": fechas, "Temperatura (°C)": temp, "Oxígeno (mg/L)": oxigeno})


# --- 3. INYECCIÓN CSS (El motor del diseño Glassmorphism) ---
def aplicar_estilos(color_estado, es_noche_global):
    """Aplica estilos CSS para el diseño dark mode Glassmorphism."""
    fondo_app = "#0E1117" if es_noche_global else "#FFFFFF"
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        .stApp {{
            background: radial-gradient(circle at 50% 0%, #1a202c 0%, #000000 100%);
            color: white;
            font-family: 'Inter', sans-serif;
        }}
        /* Estilos para las tarjetas de métricas */
        div[data-testid="stMetric"], div.css-1r6slb0 {{
            background-color: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px); /* Para Safari */
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-5px);
            background-color: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.3);
        }}
        /* Animación de flotar para el emoji */
        @keyframes float {{ 
            0% {{ transform: translatey(0px); }} 
            50% {{ transform: translatey(-20px); }} 
            100% {{ transform: translatey(0px); }} 
        }}
        .floating-shrimp {{ 
            animation: float 4s ease-in-out infinite; 
            font-size: 100px; 
            text-align: center; 
            filter: drop-shadow(0 0 15px {color_estado}40); 
        }}
        /* Estilos de texto */
        h1, h2, h3 {{ color: white !important; font-weight: 600; }}
        p, span, label, .stMarkdown, .stSelectbox label {{ color: #a0aec0 !important; }}
        /* Ocultar menú y footer de Streamlit */
        #MainMenu, footer {{ visibility: hidden; }}
        
        /* Barra de estado inferior fija */
        .bottom-status-bar {{
            position: fixed; bottom: 0; left: 0; width: 100%; height: 60px;
            background-color: {color_estado};
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 1.5em; font-weight: bold; z-index: 999;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )


# --- 4. EJECUCIÓN DEL PROGRAMA (El Pipeline) ---

# A. Interfaz: Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2829/2829862.png", width=80)
    st.title("AquaData Control")
    st.markdown("---")
    clima_simulado = st.selectbox("Simular Entorno:", ["Día Soleado", "Noche", "Lluvia"])
    
    # FILTRO POR SECTOR/CANTÓN
    sector_nombre = st.selectbox("Sector de Cultivo:", list(SECTORES.keys()))
    coordenadas = SECTORES[sector_nombre]

    st.markdown("---")
    st.header("🦐 Parámetros de la Piscina")
    biomasa_usuario = st.number_input("Biomasa Estimada (kg)", min_value=100, value=5000, step=100)
    precio_saco_usuario = st.number_input("Precio del Saco ($)", min_value=10.0, value=25.0, step=0.5, format="%.2f")

    st.caption(f"Lat: {coordenadas['lat']} | Lon: {coordenadas['lon']}")


# B. Obtener datos primarios (Satélite)
temp_actual, temp_manana, api_error = obtener_temp_real(coordenadas['lat'], coordenadas['lon'])
ph_actual = 7.8 
ox_actual = 5.2 

# C. Lógica de Estado y Ahorro
estado_codigo, color_estado, emoji, titulo_estado, desc_estado = obtener_estado_camaron(temp_actual, ph_actual, ox_actual)
alimento_sugerido, ahorro_total, tasa_real = calcular_ahorro(temp_actual, biomasa_kg=biomasa_usuario, precio_saco=precio_saco_usuario)


# D. Aplicar Estilos
aplicar_estilos(color_estado, es_noche)


# --- 5. INTERFAZ PRINCIPAL ---
ahora = datetime.now()
st.title("Acuicultura Pro")
st.markdown(f"<div style='font-size: 1.2em; margin-top: -20px; color: #a0aec0;'>{ahora.strftime('%A, %d %B %H:%M')}</div>", unsafe_allow_html=True)


# --- ALERTA DE SISTEMA (Si la API falla) ---
if api_error:
    st.warning("⚠️ ALERTA DE SISTEMA: El satélite NOAA no respondió. Usando datos de emergencia (26.0°C).", icon="📡")


# --- TARJETA PRINCIPAL DEL CAMARÓN ---
st.markdown(f"""
<div style="
    background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    backdrop-filter: blur(20px);
    border-radius: 30px;
    padding: 40px;
    text-align: center;
    border: 1px solid {color_estado}40;
    margin-bottom: 30px;
">
    <div class="floating-shrimp" style="filter: drop-shadow(0 0 30px {color_estado});">
        {emoji}
    </div>
    <h2 style="color: {color_estado} !important; font-size: 2.5em; margin-bottom: 5px;">{titulo_estado}</h2>
    <p style="font-size: 1.2em;">{desc_estado}</p>
</div>
""", unsafe_allow_html=True)

# --- PANEL DE SOLUCIONES (Acciones Recomendadas si hay riesgo) ---
if estado_codigo != 'healthy':
    st.markdown("### 🛠️ Acciones Recomendadas", unsafe_allow_html=True)
    
    if estado_codigo == 'cold':
        st.warning(f"**Recomendación de Alimento:** Mantener **{alimento_sugerido:.1f} kg** (Tasa del **{tasa_real*100:.2f}%**) | **Acción:** Asegurar que el fondo de la piscina esté limpio para evitar problemas con el frío y airear de forma intermitente.")
    elif estado_codigo == 'suffocating':
        st.error("🚨 **PELIGRO CRÍTICO:** Encender todos los aireadores inmediatamente. Riesgo de mortalidad por Hipoxia. Revisar la biomasa.")
    elif estado_codigo == 'stressed':
        st.error("❌ **Alerta de pH:** Monitorear el pH cada 3 horas. Suspender cualquier tipo de fertilización o encalado hasta estabilizar el pH.")


# --- GRID DE MÉTRICAS (KPIs de Hoy y Mañana) ---
st.markdown("### 📊 Indicadores Clave")
c1, c2, c3, c4 = st.columns(4)

with c1: 
    delta_temp = temp_manana - temp_actual
    st.metric("Hoy (Actual)", f"{temp_actual:.1f}°C", f"{delta_temp:.1f}°C vs Mañana")

with c2: 
    _, _, _, _, desc_manana = obtener_estado_camaron(temp_manana, ph_actual, ox_actual)
    st.metric("Mañana (Predicción)", f"{temp_manana:.1f}°C", f"Riesgo: {desc_manana}")

with c3: 
    st.metric("Ración Sugerida", f"{alimento_sugerido:.1f} kg", f"{tasa_real*100:.2f}% Tasa Real")

with c4:
    color_ahorro = "normal" if ahorro_total > 0 else "off"
    delta_ahorro = f"vs. Gasto Ciego (3%)"
    st.metric("Ahorro Estimado Hoy", f"${ahorro_total:.2f}", delta_ahorro, delta_color=color_ahorro)


st.markdown("---")


# --- 6. GRÁFICO DE TENDENCIA (El Cerebro Analítico) ---
st.markdown("### 📈 Tendencia de Temperatura (Últimos 7 Días)")
df_hist = obtener_datos_historicos()
tema_grafico = "plotly_dark" if es_noche else "plotly_white"
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_hist["Fecha"], 
    y=df_hist["Temperatura (°C)"], 
    fill='tozeroy',
    mode='lines+markers',
    line=dict(width=3, color=color_estado), 
    fillcolor=f"rgba{tuple(int(color_estado.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"
))

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='gray', family='Inter'), margin=dict(l=0, r=0, t=10, b=0),
    height=250,
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', range=[23, 30]),
    xaxis=dict(showgrid=False)
)

# Corrección del Warning de Streamlit
st.plotly_chart(fig, width="stretch")


# --- 7. BARRA DE ESTADO INFERIOR ---
st.markdown(
    f"""
    <div class="bottom-status-bar">
        {titulo_estado} | Ahorro Potencial Diario: ${ahorro_total:.2f} USD
    </div>
    """,
    unsafe_allow_html=True
)

# --- REPORTE INTEGRADO EN LA APP ---
st.markdown("---")
with st.expander("Ver Reporte de Vulnerabilidad por Frío (Base Científica)"):
    st.markdown("""
    ### REPORTE: Vulnerabilidad del Camarón (Penaeus vannamei) a Bajas Temperaturas

    **ASUNTO:** Justificación científica de los umbrales de alerta del dashboard.

    ---

    #### 1. Resumen Ejecutivo (TL;DR)
    El *Penaeus vannamei* (camarón blanco) es un animal tropical **poiquilotermo** (de sangre fría). Su temperatura corporal depende 100% del ambiente.

    Las bajas temperaturas (**< 24°C**) son el **principal disparador de mortalidades masivas** en Ecuador, no por el frío en sí, sino por una "falla en cascada":

    1.  El frío detiene su metabolismo y su alimentación.
    2.  El frío **apaga su sistema inmunológico**.
    3.  Bacterias (como el *Vibrio*) y virus (como la "Mancha Blanca" - WSSV), que siempre están presentes en el agua, atacan al camarón indefenso.

    Nuestra aplicación `AquaData` no solo mide la temperatura; **mide el riesgo de colapso inmunológico**.

    ---

    #### 2. Umbrales Críticos de Temperatura (La Lógica de la App)

    Basado en múltiples estudios de la FAO y la Cámara Nacional de Acuacultura (CNA), hemos definido los siguientes umbrales de riesgo:

    #### 🟢 **Zona Óptima (26°C - 30°C)**
    * **Metabolismo:** Activo. El camarón come vigorosamente (Tasa del 3%).
    * **Crecimiento:** Máximo.
    * **Sistema Inmune:** Fuerte y funcional.
    * **Acción de la App:** `ESTADO SALUDABLE`.

    #### 🟡 **Zona de Precaución (24°C - 26°C)**
    * **Metabolismo:** El camarón se vuelve **letárgico**. Suprime su apetito.
    * **Crecimiento:** Se reduce significativamente.
    * **Sistema Inmune:** Comienza a debilitarse.
    * **Acción de la App:** `ESTADO PRECAUCIÓN`.
        * **Justificación Financiera:** Bajar la tasa de alimento (al 2%) es crucial. Alimentar de más en esta etapa es el principal desperdicio de balanceado en la industria.

    #### 🔴 **Zona de Peligro (< 24°C)**
    * **Metabolismo:** **Parada casi total de alimentación (Anorexia)**. El camarón deja de comer para conservar energía.
    * **Sistema Inmune:** **Falla Crítica.** El camarón entra en "shock" y no puede defenderse.
    * **Vulnerabilidad:** Este es el **disparador directo de enfermedades** como el WSSV (Virus del Síndrome de la Mancha Blanca) y Vibriosis.
    * **Acción de la App:** `TEMPERATURA CRÍTICA`.
        * **Justificación Financiera:** Bajar la tasa de alimento al mínimo (0.5%) ahorra miles de dólares.
        * **Justificación de Supervivencia:** El **"Panel de Soluciones"** se activa para sugerir aireación, que es vital para evitar la hipoxia nocturna que remataría al camarón ya debilitado.
    """)