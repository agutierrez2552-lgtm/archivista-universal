import streamlit as st
import google.generativeai as genai

# Configuración básica
st.set_page_config(page_title="ajugarconia", layout="centered")

# Estilo para el Nexo
st.markdown("<style>.stApp { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

st.title("⚔️ Nexo de Poder")

# --- BARRA LATERAL ---
with st.sidebar:
    st.subheader("Configuración")
    # El .strip() es fundamental para limpiar la clave de espacios
    g_raw = st.text_input("Gemini API Key:", type="password")
    g_key = g_raw.strip() if g_raw else None
    
    juego = st.selectbox("Juego:", ["Gloomhaven", "Marvel Champions", "D&D 5e"])
    st.info("Pegá tu clave y dale a Enter en el chat.")

# Historial de chat
if "chat" not in st.session_state:
    st.session_state.chat = []

# --- FUNCIÓN DE RESPUESTA ---
def enviar():
    msj = st.session_state.input_usuario
    if msj and g_key:
        try:
            genai.configure(api_key=g_key)
            # 'gemini-1.5-flash' es el modelo más rápido y compatible
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("El Archivista está escribiendo..."):
                response = model.generate_content(f"Eres el Archivista de {juego}. {msj}")
                st.session_state.chat.append({"role": "user", "content": msj})
                st.session_state.chat.append({"role": "assistant", "content": response.text})
                # Limpiar el input
                st.session_state.input_usuario = ""
        except Exception as e:
            st.error(f"Error técnico: {e}")

# --- INTERFAZ DE CHAT ---
st.subheader("📜 Crónicas del Reino")

# Entrada de texto (On change dispara la función)
st.text_input("¿Qué deseas consultar?", key="input_usuario", on_change=enviar)

# Mostrar historial
for m in reversed(st.session_state.chat):
    with st.chat_message(m["role"]):
        st.write(m["content"])
