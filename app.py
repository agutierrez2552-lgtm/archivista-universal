import streamlit as st
import google.generativeai as genai
from PIL import Image
import io, base64, requests, os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="El Archivista Universal", page_icon="📜")

# --- ESTILO PARA GRUPOS DE ROL ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #262730; color: #d4af37; border: 1px solid #d4af37; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #1a1a1a; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.title("⚔️ Nexo de Poder")
    st.markdown("Para que el Archivista despierte, entrega las llaves del reino.")
    
    # El usuario pone sus propias claves (Privacidad total)
    g_key = st.text_input("Gemini API Key:", type="password", help="Consíguela gratis en Google AI Studio")
    e_key = st.text_input("ElevenLabs API Key:", type="password", help="Opcional para que Roger hable")
    
    juego = st.selectbox("¿Qué leyenda narramos?", 
                        ["Gloomhaven", "Las Mansiones de la Locura", "Descent", "Marvel Champions", "Munchkin", "Dungeons & Dragons"])
    
    if st.button("🔮 Despertar al Archivista"):
        if g_key:
            st.session_state.ready = True
            st.success(f"¡El Archivista de {juego} ha despertado!")
        else:
            st.error("Falta la llave de Gemini.")

# --- MOTOR DE INTELIGENCIA ---
if g_key and st.session_state.get('ready'):
    genai.configure(api_key=g_key)
    # Personalización dinámica para la comunidad
    prompt_sistema = f"Eres el Archivista de {juego}. Tu tono es épico y narrativo. Ayuda al jugador analizando lo que ves en pantalla."
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=prompt_sistema)

# --- INTERFAZ DE CRÓNICA ---
col_vis, col_cro = st.columns([1.2, 1])

with col_vis:
    st.subheader("👁️ Visión del Archivista")
    st.components.v1.html("""
    <div style="background:#1a1a1a; padding:15px; border-radius:10px; border:2px solid #d4af37; color:white">
        <video id="vid" autoplay style="width:100%; border-radius:5px; background:black"></video>
        <div style="margin-top:10px; display: flex; gap: 10px;">
            <button onclick="start()" style="flex:1; padding:12px; background:#d4af37; border:none; cursor:pointer; font-weight:bold; border-radius:5px">COMPARTIR PANTALLA</button>
            <button id="mic" onclick="toggle()" style="flex:1; padding:12px; background:#4CAF50; border:none; color:white; cursor:pointer; font-weight:bold; border-radius:5px">HABLAR</button>
        </div>
        <canvas id="canvas" style="display:none;"></canvas>
    </div>
    <script>
        const v = document.getElementById('vid');
        const c = document.getElementById('canvas');
        let rec; let esc = false;

        async function start() {
            v.srcObject = await navigator.mediaDevices.getDisplayMedia({video: true});
        }

        if ('webkitSpeechRecognition' in window) {
            rec = new webkitSpeechRecognition();
            rec.continuous = true; rec.lang = 'es-AR';
            rec.onresult = (e) => {
                const t = e.results[e.results.length-1][0].transcript;
                c.width = v.videoWidth; c.height = v.videoHeight;
                c.getContext('2d').drawImage(v, 0, 0);
                const img = c.toDataURL('image/jpeg', 0.5);
                window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'datos_voz', value: {t: t, f: img, id: Date.now()}}, '*');
            };
        }

        function toggle() {
            if(!esc) { rec.start(); esc=true; document.getElementById('mic').style.background='#f44336'; }
            else { rec.stop(); esc=false; document.getElementById('mic').style.background='#4CAF50'; }
        }
    </script>
    """, height=520)

with col_cro:
    st.subheader("📜 Crónicas del Reino")
    if "chat" not in st.session_state: st.session_state.chat = []
    
    # Captura de datos del navegador
    res = st.session_state.get('datos_voz')
    if res and (st.session_state.get('last_id') != res['id']):
        st.session_state.last_id = res['id']
        
        with st.spinner("El Archivista está escribiendo..."):
            try:
                # Procesar imagen y texto
                header, encoded = res['f'].split(",", 1)
                img = Image.open(io.BytesIO(base64.b64decode(encoded)))
                
                respuesta = model.generate_content([res['t'], img])
                texto_final = respuesta.text
                
                st.session_state.chat.append({"role": "user", "content": res['t']})
                st.session_state.chat.append({"role": "assistant", "content": texto_final})
                
                # Voz opcional con ElevenLabs
                if e_key:
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/CwhSss6Y92671G8AbaQ1"
                    requests.post(url, json={"text": texto_final, "model_id": "eleven_multilingual_v2"}, headers={"xi-api-key": e_key})
                
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Mostrar la Bitácora
    for m in st.session_state.chat[::-1]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
# Voz opcional - Si falla o no hay clave, que no rompa el resto
if e_key:
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/CwhSss6Y92671G8AbaQ1"
        requests.post(url, json={"text": texto_final, "model_id": "eleven_multilingual_v2"}, headers={"xi-api-key": e_key})
    except:
        st.warning("No se pudo generar el audio, pero la crónica se guardó.")
