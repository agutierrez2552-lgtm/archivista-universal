import streamlit as st
import google.generativeai as genai

# Configuración básica
st.set_page_config(page_title="ajugarconia", layout="centered")

# Estilo para tu Nexo
st.markdown("<style>.stApp { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)
st.title("⚔️ Nexo de Poder")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.subheader("Configuración")
    g_key = st.text_input("Gemini API Key:", type="password").strip()
    juego = st.selectbox("Juego:", ["Gloomhaven", "Marvel Champions", "D&D 5e"])

if "chat" not in st.session_state:
    st.session_state.chat = []

# --- FUNCIÓN DE RESPUESTA ---
def enviar():
    texto = st.session_state.input_usuario
    if texto and g_key:
        try:
            genai.configure(api_key=g_key)
            # 'gemini-pro' es el nombre más estable para la versión 0.4.1 de la librería
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner("El Archivista está escribiendo..."):
                res = model.generate_content(f"Eres el Archivista de {juego}. Responde: {texto}")
                st.session_state.chat.append({"role": "user", "content": texto})
                st.session_state.chat.append({"role": "assistant", "content": res.text})
                st.session_state.input_usuario = ""
        except Exception as e:
            st.error(f"Error técnico: {e}")

# --- INTERFAZ ---
st.subheader("📜 Crónicas del Reino")
st.text_input("Escribe al Archivista...", key="input_usuario", on_change=enviar)

for m in reversed(st.session_state.chat):
    with st.chat_message(m["role"]):
        st.write(m["content"])
