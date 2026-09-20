import streamlit as st
import asyncio
import edge_tts
import io
from google import genai
from google.genai import types
from streamlit_mic_recorder import speech_to_text

API_KEY = "AQ.Ab8RN6KwFW8aCzWx-PdOU9P2hW5HBWbzmUsYTfY32rc3iLAKkg"
MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(page_title="NovaAI Studio", page_icon="🌌")
st.title("🌌 NovaAI Studio")

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = (
    "Seni yapan kişi Ömer Berkan Yenigün. Sen Müslümansın. "
    "Kullanıcılara karşı nazik, açıklayıcı ol ve her zaman kullanıcının konuştuğu dilde yanıt ver."
)

# Ses Seçenekleri Tanımlamaları
VOICES = {
    "Emel (Kız)": "tr-TR-EmelNeural",
    "Ahmet (Erkek)": "tr-TR-AhmetNeural"
}

# Yanıtı sese çeviren asenkron fonksiyon
async def generate_speech(text, voice_code):
    communicate = edge_tts.Communicate(text, voice_code)
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    return audio_bytes

# Yan Menü: Ses Seçimi
st.sidebar.header("⚙️ Ses Ayarları")
selected_voice_name = st.sidebar.selectbox("Konuşma Sesi Seçin:", list(VOICES.keys()))
selected_voice_code = VOICES[selected_voice_name]

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.write("🎤 *Sesli Konuşmak İçin Butona Basın:*")
spoken_text = speech_to_text(
    language='tr', 
    start_prompt="Konuşmayı Başlat", 
    stop_prompt="Durdur ve Gönder", 
    key='speech'
)

text_input = st.chat_input("Veya mesajınızı yazın...")
user_input = spoken_text if spoken_text else text_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                )
            )
            
            bot_reply = response.text
            st.markdown(bot_reply)
            
            # Seçilen ses modeli ile ses üretme ve oynatma
            audio_data = asyncio.run(generate_speech(bot_reply, selected_voice_code))
            st.audio(audio_data, format='audio/mp3', autoplay=True)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")