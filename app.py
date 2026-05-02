import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configuración de página
st.set_page_config(layout="wide", page_title="ajugarconia")
st.markdown("<style>.stApp { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.title("⚔️ Nexo de Poder")
    # El .strip() limpia espacios invisibles
    g_key = st.text_input("Gemini API Key:", type="password").strip()
    juego = st.selectbox("Juego:", ["Gloomhaven", "Marvel Champions", "D&D 5e", "Las Mansiones de la Locura"])
    if st.button("🔮 Despertar"):
        st.success("¡Nexo vinculado!")

if "chat" not in st.session_state: 
    st.session_state.chat = []

# --- LÓGICA DE PROCESAMIENTO REFORZADA ---
def procesar_mensaje():
    texto = st.session_state.input_usuario
    if texto and g_key:
        try:
            genai.configure(api_key=g_key)
            
            # SOLUCIÓN AL 404: Usamos el nombre de modelo más moderno y compatible
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Prompt directo
            prompt = f"Actúa como el Archivista de {juego}. Narrador épico. Responde: {texto}"
            
            with st.spinner("Consultando los tomos antiguos..."):
                response = model.generate_content(prompt)
                
                # Guardar historial
                st.session_state.chat.append({"role": "user", "content": texto})
                st.session_state.chat.append({"role": "assistant", "content": response.text})
                
                # Limpiar entrada
                st.session_state.input_usuario = ""
        except Exception as e:
            # Si el 'flash-latest' falla, intentamos con el nombre base
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Eres el Archivista de {juego}. {texto}")
                st.session_state.chat.append({"role": "user", "content": texto})
                st.session_state.chat.append({"role": "assistant", "content": response.text})
                st.session_state.input_usuario = ""
            except Exception as e2:
                st.error(f"Error técnico persistente: {e2}")
    elif not g_key:
        st.warning("⚠️ Pegá tu API Key en el panel izquierdo.")

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
