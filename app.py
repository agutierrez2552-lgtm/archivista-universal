import streamlit as st
import google.generativeai as genai
from PIL import Image
import io, base64, requests

st.set_page_config(layout="wide", page_title="ajugarconia")

# Estilo rápido
st.markdown("<style>.stApp { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚔️ Nexo de Poder")
    g_key = st.text_input("Gemini API Key:", type="password").strip()
    juego = st.selectbox("Juego:", ["Gloomhaven", "Marvel Champions", "D&D 5e"])
    st.button("🔮 Despertar")

if "chat" not in st.session_state: st.session_state.chat = []

def procesar(texto, img_b64=None):
    if not g_key:
        st.error("Pegá tu API Key en la izquierda.")
        return
    try:
        genai.configure(api_key=g_key)
        # Usamos el nombre más genérico para evitar el error 404
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        cuerpo = [f"Eres el Archivista de {juego}. {texto}"]
        if img_b64:
            img = Image.open(io.BytesIO(base64.b64decode(img_b64.split(",")[1])))
            cuerpo.append(img)
            
        res = model.generate_content(cuerpo)
        st.session_state.chat.append({"role": "user", "content": texto})
        st.session_state.chat.append({"role": "assistant", "content": res.text})
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

col_v, col_c = st.columns([1.2, 1])

with col_v:
    st.subheader("👁️ Visión")
    st.components.v1.html("""
    <div style="background:#1a1a1a; padding:10px; border-radius:10px; border:1px solid #d4af37;">
        <video id="vid" autoplay style="width:100%; border-radius:5px;"></video>
        <button onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>document.getElementById('vid').srcObject=s)" style="width:100%; margin-top:5px; padding:10px; background:#d4af37; border:none; font-weight:bold; border-radius:5px; cursor:pointer">COMPARTIR PANTALLA</button>
    </div>
    """, height=350)
    
    with st.form("chat", clear_on_submit=True):
        m = st.text_input("Escribe al Archivista...")
        if st.form_submit_button("Enviar") and m:
            procesar(m)

with col_c:
    st.subheader("📜 Crónicas")
    for m in st.session_state.chat[::-1]:
        with st.chat_message(m["role"]):
            st.write(m["content"])
