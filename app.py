import streamlit as st
import google.generativeai as genai
from PIL import Image
import io, base64, requests, os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="ajugarconia", page_icon="📜")

# --- ESTILO ÉPICO ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #262730; color: #d4af37; border: 1px solid #d4af37; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #1a1a1a; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚔️ Nexo de Poder")
    g_key = st.text_input("Gemini API Key:", type="password")
    e_key = st.text_input("ElevenLabs API Key:", type="password")
    
    juego = st.selectbox("¿Qué leyenda narramos?", 
                        ["Gloomhaven", "Las Mansiones de la Locura", "Descent", "Marvel Champions", "Munchkin", "D&D 5e"])
    
    if st.button("🔮 Despertar al Archivista"):
        if g_key:
            st.session_state.ready = True
            st.success(f"¡El Archivista de {juego} ha despertado!")
        else:
            st.error("Falta la llave de Gemini.")

# --- LÓGICA DE PROCESAMIENTO ---
def procesar_evento(texto, imagen_b64):
    if not g_key:
        st.error("Falta API Key de Gemini")
        return

    try:
        genai.configure(api_key=g_key)
        model = genai.GenerativeModel('gemini-1.5-flash', 
                                     system_instruction=f"Eres el Archivista de {juego}. Narrador épico y experto.")
        
        # Preparar imagen si existe
        contenido = [texto]
        if imagen_b64:
            header, encoded = imagen_b64.split(",", 1)
            img = Image.open(io.BytesIO(base64.b64decode(encoded)))
            contenido.append(img)
        
        respuesta = model.generate_content(contenido)
        st.session_state.chat.append({"role": "user", "content": texto})
        st.session_state.chat.append({"role": "assistant", "content": respuesta.text})
        
        # Voz opcional
        if e_key:
            try:
                url = "https://api.elevenlabs.io/v1/text-to-speech/CwhSss6Y92671G8AbaQ1"
                requests.post(url, json={"text": respuesta.text, "model_id": "eleven_multilingual_v2"}, 
                              headers={"xi-api-key": e_key}, timeout=5)
            except: pass
            
    except Exception as e:
        st.error(f"Error en el Nexo: {e}")

# --- INTERFAZ PRINCIPAL ---
if "chat" not in st.session_state: st.session_state.chat = []

col_vis, col_cro = st.columns([1.2, 1])

with col_vis:
    st.subheader("👁️ Visión del Archivista")
    # Capturador de pantalla y voz
    st.components.v1.html("""
    <div style="background:#1a1a1a; padding:15px; border-radius:10px; border:2px solid #d4af37; color:white">
        <video id="vid" autoplay style="width:100%; border-radius:5px; background:black"></video>
        <div style="margin-top:10px; display: flex; gap: 10px;">
            <button onclick="start()" style="flex:1; padding:10px; background:#d4af37; border:none; cursor:pointer; font-weight:bold; border-radius:5px">COMPARTIR PANTALLA</button>
            <button id="mic" onclick="toggle()" style="flex:1; padding:10px; background:#4CAF50; border:none; color:white; cursor:pointer; font-weight:bold; border-radius:5px">HABLAR</button>
        </div>
        <canvas id="canvas" style="display:none;"></canvas>
    </div>
    <script>
        const v = document.getElementById('vid');
        const c = document.getElementById('canvas');
        let rec; let esc = false;
        async function start() { v.srcObject = await navigator.mediaDevices.getDisplayMedia({video: true}); }
        
        if ('webkitSpeechRecognition' in window) {
            rec = new webkitSpeechRecognition();
            rec.continuous = false; rec.lang = 'es-AR';
            rec.onresult = (e) => {
                const t = e.results[0][0].transcript;
                c.width = v.videoWidth; c.height = v.videoHeight;
                c.getContext('2d').drawImage(v, 0, 0);
                const img = c.toDataURL('image/jpeg', 0.5);
                window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'datos_voz', value: {t: t, f: img, id: Date.now()}}, '*');
            };
        }
        function toggle() { rec.start(); }
    </script>
    """, height=450)
    
    # --- NUEVA FUNCIÓN: MENSAJE DE TEXTO ---
    st.markdown("---")
    st.write("⌨️ **Mensaje Manual (Si no usas micro)**")
    msj_texto = st.text_input("Escribe tu consulta aquí...", key="input_manual")
    if st.button("Enviar Mensaje"):
        if msj_texto:
            procesar_evento(msj_texto, None)
            st.rerun()

with col_cro:
    st.subheader("📜 Crónicas del Reino")
    
    # Detectar si entró algo por voz
    res_voz = st.session_state.get('datos_voz')
    if res_voz and (st.session_state.get('last_id') != res_voz['id']):
        st.session_state.last_id = res_voz['id']
        procesar_evento(res_voz['t'], res_voz['f'])
        st.rerun()

    for m in st.session_state.chat[::-1]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
