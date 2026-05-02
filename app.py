import streamlit as st
import google.generativeai as genai
from PIL import Image
import io, base64, requests

# --- CONFIGURACIÓN BASE ---
st.set_page_config(layout="wide", page_title="ajugarconia", page_icon="📜")

# Estilo para que combine con tu ludoteca
st.markdown("<style>.stApp { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.title("⚔️ Nexo de Poder")
    # El .strip() es la clave: limpia la API Key de espacios accidentales
    g_raw = st.text_input("Gemini API Key:", type="password")
    g_key = g_raw.strip() if g_raw else None
    
    e_raw = st.text_input("ElevenLabs API Key (Opcional):", type="password")
    e_key = e_raw.strip() if e_raw else None
    
    juego = st.selectbox("Juego:", ["Gloomhaven", "Marvel Champions", "Las Mansiones de la Locura", "D&D 5e"])
    
    if st.button("🔮 Despertar al Archivista"):
        if g_key and g_key.startswith("AIza"):
            st.session_state.ready = True
            st.balloons()
            st.success("¡El Archivista ha despertado!")
        else:
            st.error("Revisá la Gemini Key (debe empezar con AIza)")

# --- LÓGICA DE PROCESAMIENTO ---
if "chat" not in st.session_state: st.session_state.chat = []

def procesar_evento(texto, img_b64=None):
    if not g_key:
        st.error("❌ No hay API Key válida.")
        return
    try:
        genai.configure(api_key=g_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt épico para tus juegos
        prompt = f"Actúa como el Archivista de {juego}. Eres un narrador inmersivo. Analiza y responde: {texto}"
        cuerpo = [prompt]
        
        if img_b64:
            img_data = base64.b64decode(img_b64.split(",")[1])
            img = Image.open(io.BytesIO(img_data))
            cuerpo.append(img)
            
        with st.spinner("Consultando los tomos antiguos..."):
            res = model.generate_content(cuerpo)
            st.session_state.chat.append({"role": "user", "content": texto})
            st.session_state.chat.append({"role": "assistant", "content": res.text})
            
            if e_key:
                try:
                    url = "https://api.elevenlabs.io/v1/text-to-speech/CwhSss6Y92671G8AbaQ1"
                    requests.post(url, json={"text": res.text, "model_id": "eleven_multilingual_v2"}, 
                                  headers={"xi-api-key": e_key}, timeout=3)
                except: pass
        st.rerun()
    except Exception as e:
        st.error(f"Error en el Nexo: {e}")

# --- INTERFAZ ---
col_v, col_c = st.columns([1.2, 1])

with col_v:
    st.subheader("👁️ Visión del Archivista")
    st.components.v1.html("""
    <div style="background:#1a1a1a; padding:10px; border-radius:10px; border:1px solid #d4af37;">
        <video id="vid" autoplay style="width:100%; border-radius:5px;"></video>
        <button onclick="start()" style="width:100%; margin-top:5px; padding:10px; background:#d4af37; border:none; font-weight:bold; border-radius:5px; cursor:pointer">COMPARTIR PANTALLA</button>
        <button onclick="toggle()" style="width:100%; margin-top:5px; padding:10px; background:#4CAF50; color:white; border:none; font-weight:bold; border-radius:5px; cursor:pointer">HABLAR</button>
    </div>
    <canvas id="canvas" style="display:none;"></canvas>
    <script>
        const v = document.getElementById('vid');
        const c = document.getElementById('canvas');
        async function start() { v.srcObject = await navigator.mediaDevices.getDisplayMedia({video: true}); }
        const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        rec.lang = 'es-AR';
        rec.onresult = (e) => {
            const t = e.results[0][0].transcript;
            c.width = v.videoWidth; c.height = v.videoHeight;
            c.getContext('2d').drawImage(v, 0, 0);
            const img = c.toDataURL('image/jpeg', 0.5);
            window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'datos_voz', value: {t: t, f: img, id: Date.now()}}, '*');
        };
        function toggle() { rec.start(); }
    </script>
    """, height=440)
    
    with st.form("chat_manual", clear_on_submit=True):
        m_txt = st.text_input("Escribe al Archivista...")
        if st.form_submit_button("Enviar Mensaje") and m_txt:
            procesar_evento(m_txt)

with col_c:
    st.subheader("📜 Crónicas del Reino")
    voz = st.session_state.get('datos_voz')
    if voz and (st.session_state.get('l_id') != voz['id']):
        st.session_state.l_id = voz['id']
        procesar_evento(voz['t'], voz['f'])

    for m in st.session_state.chat[::-1]:
        with st.chat_message(m["role"]):
            st.write(m["content"])
