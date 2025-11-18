import streamlit as st
import requests
from datetime import datetime
import random # Para simular lluvia si no hay dato real

# --- 1. LÓGICA DEL ENTORNO (El "Cerebro" Visual) ---
def obtener_estilo_dinamico(clima_actual):
    hora = datetime.now().hour
    es_dia = 6 <= hora < 18 # Día entre 6 AM y 6 PM
    
    # Colores según horario
    if es_dia:
        fondo = "#FFFFFF" # Blanco
        texto = "#000000" # Negro
        icono_sol_luna = "☀️"
        tema = "Modo Día"
    else:
        fondo = "#0E1117" # Azul Oscuro Profundo (Noche)
        texto = "#FFFFFF" # Blanco
        icono_sol_luna = "🌙"
        tema = "Modo Noche"

    # Efecto de Lluvia (CSS Avanzado)
    css_lluvia = ""
    if "Lluvia" in clima_actual:
        # Esto crea gotitas cayendo sobre la pantalla
        css_lluvia = """
        body:before {
            content: "";
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            background-image: url('https://i.gifer.com/7scx.gif'); /* GIF de lluvia transparente */
            background-size: cover;
            opacity: 0.3;
            pointer-events: none;
            z-index: 9999;
        }
        """

    # Inyectamos el CSS
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {fondo};
            color: {texto};
        }}
        /* Forzamos color de textos grandes */
        h1, h2, h3, p, div, span {{
            color: {texto} !important;
        }}
        {css_lluvia}
        </style>
        """,
        unsafe_allow_html=True
    )
    return icono_sol_luna, tema

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="AquaData Live", page_icon="🦐", layout="centered")

# Simulamos el dato del clima (En producción vendría de la API)
# Puedes cambiar esto manualmente para probar el efecto
clima_simulado = st.selectbox("Simular Clima (Prueba los efectos):", ["Soleado", "Lluvia", "Nublado"])

# Aplicamos el estilo mágico
icono, tema_actual = obtener_estilo_dinamico(clima_simulado)

# --- 3. INTERFAZ VISUAL ---
st.title(f"🦐 AquaData {icono}")
st.caption(f"Ambiente detectado: {tema_actual} | Clima: {clima_simulado}")

# El Camarón Reactivo
col1, col2 = st.columns([1, 2])

with col1:
    # Imagen del camarón que cambia si llueve
    if clima_simulado == "Lluvia":
        st.image("https://cdn-icons-png.flaticon.com/512/1858/1858068.png", caption="¡Está lloviendo! Cuidado con el pH.")
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/1998/1998610.png", caption="Camarón Feliz")

with col2:
    st.metric("Temperatura Agua", "26.5 °C", "Estable")
    st.metric("Oxígeno Disuelto", "4.5 mg/L", "-0.2 mg/L")

# Tarjeta de Acción
if clima_simulado == "Lluvia":
    st.error("🌧️ ALERTA DE LLUVIA: La lluvia baja la salinidad y el pH bruscamente. Suspender fertilización.")
else:
    st.success("✅ Condiciones estables. Continuar protocolo estándar.")