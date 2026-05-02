import streamlit as st
import google.generativeai as genai
from PIL import Image
import io, base64

# Configuración básica
st.set_page_config(layout="wide", page_title="ajugarconia")

# Estilo visual
st.markdown("<style>.stApp { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.title("⚔️ Nexo de Poder")
    g_key = st.text_input("Gemini API Key:", type="password").strip()
    juego = st.selectbox("Juego:", ["Gloomhaven", "Marvel Champions", "D&D 5e", "Las Mansiones de la Locura"])
    if st.button("🔮 Despertar"):
        st.success("¡Nexo vinculado!")

if "chat" not in st.session_state: 
    st.session_state.chat = []

# --- FUNCIÓN DE PROCESAMIENTO REFORZADA ---
def procesar_mensaje():
    texto = st.session_state.input_usuario
    if texto and g_key:
        try:
            genai.configure(api_key=g_key)
            
            # PLAN A y PLAN B para evitar el error 404
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"Actúa como el Archivista de {juego}. {texto}")
            except:
                # Si el servidor es viejo, este nombre suele funcionar siempre
                model = genai.GenerativeModel('gemini-pro')
                res = model.generate_content(f"Actúa como el Archivista de {juego}. {texto}")
            
            st.session_state.chat.append({"role": "user", "content": texto})
            st.session_state.chat.append({"role": "assistant", "content": res.text})
            st.session_state.input_usuario = ""
        except Exception as e:
            st.error(f"Error técnico: {e}")
    elif not g_key:
        st.warning("⚠️ Pegá la Gemini Key a la izquierda.")

# --- INTERFAZ ---
col_v, col_c = st.columns([1.1, 1])

with col_v:
    st.subheader("👁️ Visión")
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
    st.text_input("Escribe al Archivista...", key="input_usuario", on_change=procesar_mensaje)

with col_c:
    st.subheader("📜 Crónicas")
    for m in reversed(st.session_state.chat):
        with st.chat_message(m["role"]):
            st.write(m["content"])
