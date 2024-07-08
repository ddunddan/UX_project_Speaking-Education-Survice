import io
import requests
from pathlib import Path

import streamlit as st
from openai import OpenAI
from pydub import AudioSegment
import speech_recognition as sr

def recognize_speech_and_save_to_wav(
    recognizer,
    microphone,
    output_file_path
):
    with microphone as source:
        status_text.info("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        status_text.info("Listening...")
        audio = recognizer.listen(source)
    
    audio_data = audio.get_wav_data()

    with open(output_file_path, "wb") as wav_file:
        wav_file.write(audio_data)

def speech_to_text():
    api_key = st.secrets["OPENAI_API_KEY"]
        
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    status_text.info("Recognizing speech...")
    recognize_speech_and_save_to_wav(recognizer, microphone, 'audio.wav')
    
    audio_file = open("audio.wav", "rb")
    transcription = client.audio.transcriptions.create(
        model = "whisper-1", 
        file = audio_file,
        language = "en"
    )
    text = transcription.text
    st.session_state["voice_input"] = text  # STT 결과를 session_state에 저장
    status_text.info("Speech recognition completed successfully.")
    
    status_text.empty()  # 상태 메시지 초기화

def text_to_speech(text, output_file_path):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    
    response.stream_to_file(output_file_path)
        
# Set title
st.title("LAPT")
# Set sidebar title
st.sidebar.title("History")
st.sidebar.write("- UX 발표 잘하는 법")

st.sidebar.write('# Situation')
st.sidebar.write('- 호그와트 입학식')
st.sidebar.write('- 공항 입국 심사')
st.sidebar.write('- 식당 음식 주문')

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
# 초기 프롬프트 설정

# initial_prompt = "You are a helpful assistant. Answer only in English. Answer as if you were speaking directly to a human voice. Please keep your answers brief and sentence-linked."
initial_prompt = "You are a helpful assistant that converses with people who are learning English. Your role is to help them practice their English conversation skills. Please use simple language and keep sentences short and clear.Provide encouragement and correct any mistakes gently. Make the conversation feel natural and friendly. Always respond in English. You have to answer like a human."

if "initialized" not in st.session_state:
    st.session_state["messages"].append({"role": "system", "content": initial_prompt})
    st.session_state["initialized"] = True

# 상태 메시지 설정
status_text = st.empty()

# 음성 인식 버튼
st.button("음성으로 대화하기", on_click = speech_to_text)

# 음성 인식 결과를 prompt로 사용
prompt = st.session_state.get("voice_input", "")

# 채팅 메시지 표시
st.markdown("## Free Talk")
chat_container = st.container()

with chat_container:
    for message in st.session_state["messages"]:
        if message["role"] != "system":  # 시스템 메시지를 렌더링하지 않음
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
        text_to_speech(response, "speech.mp3")
        st.audio("speech.mp3")
    
    st.session_state.messages.append({"role": "assistant", "content": response})

    # 음성 인식 결과를 초기화
    st.session_state["voice_input"] = ""