import streamlit as st
import google.generativeai as genai
from PIL import Image
import io, base64

# Configuración básica
st.set_page_config(layout="wide", page_title="ajugarconia")

# Estilo para que combine con tu ludoteca
st.markdown("<style>.stApp { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.title("⚔️ Nexo de Poder")
    g_key = st.text_input("Gemini API Key:", type="password").strip()
    juego = st.selectbox("Juego:", ["Gloomhaven", "Marvel Champions", "D&D 5e", "Las Mansiones de la Locura"])
    if st.button("🔮 Despertar"):
        st.success("¡Nexo vinculado!")

# Historial de mensajes
if "chat" not in st.session_state: 
    st.session_state.chat = []

# --- FUNCIÓN DE PROCESAMIENTO ---
def procesar_mensaje():
    texto = st.session_state.input_usuario
    if texto and g_key:
        try:
            genai.configure(api_key=g_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Actúa como el Archivista de {juego}. Eres un narrador épico y experto. Responde a: {texto}"
            
            with st.spinner("El Archivista está consultando los tomos..."):
                res = model.generate_content(prompt)
                # Guardar en el historial
                st.session_state.chat.append({"role": "user", "content": texto})
                st.session_state.chat.append({"role": "assistant", "content": res.text})
                # Limpiar la entrada
                st.session_state.input_usuario = ""
        except Exception as e:
            st.error(f"Error en el Nexo: {e}")
    elif not g_key:
        st.warning("⚠️ Por favor, ingresá tu Gemini API Key en el panel izquierdo.")

# --- INTERFAZ PRINCIPAL ---
col_v, col_c = st.columns([1.1, 1])

with col_v:
    st.subheader("👁️ Visión del Archivista")
    # Capturador de pantalla simplificado
    st.components.v1.html("""
    <div style="background:#1a1a1a; padding:10px; border-radius:10px; border:1px solid #d4af37;">
        <video id="vid" autoplay style="width:100%; border-radius:5px; background:black"></video>
        <button onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>document.getElementById('vid').srcObject=s)" 
                style="width:100%; margin-top:10px; padding:12px; background:#d4af37; border:none; font-weight:bold; border-radius:5px; cursor:pointer">
                COMPARTIR PANTALLA
        </button>
    </div>
    """, height=380)
    
    st.markdown("---")
    # Entrada de texto directa sin st.form para evitar el error de ValueAssignment
    st.text_input("Escribe tu consulta aquí...", key="input_usuario", on_change=procesar_mensaje)
    st.caption("Presioná 'Enter' para enviar tu mensaje al Archivista.")

with col_c:
    st.subheader("📜 Crónicas del Reino")
    # Mostrar el chat del más nuevo al más viejo
    for m in reversed(st.session_state.chat):
        with st.chat_message(m["role"]):
            st.write(m["content"])
