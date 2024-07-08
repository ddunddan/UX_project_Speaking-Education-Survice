import io
import requests
import speech_recognition as sr
from pydub import AudioSegment

def recognize_speech_from_mic(
    recognizer,
    microphone,
    file_format='wav'
):
    with microphone as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
    
    audio_data = io.BytesIO(audio.get_wav_data())
    
    if file_format == 'wav':
        return audio_data
    elif file_format == 'mp3':
        audio_segment = AudioSegment.from_wav(audio_data)
        mp3_data = io.BytesIO()
        audio_segment.export(mp3_data, format="mp3")
        mp3_data.seek(0)
        return mp3_data
    else:
        raise ValueError("Unsupported file format. Use 'wav' or 'mp3'.")

def speech_to_text():
    api_key = "your keys"
    url = "https://api.openai.com/v1/audio/transcriptions"
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("Recognizing speech...")
    audio = recognize_speech_from_mic(recognizer, microphone)
    
    files = {
        'file': ('audio.wav', audio, 'audio/wav')
    }
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': 'whisper-1'
    }
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json().get('text', None)
    else:
        print(f"An error occurred: {response.status_code} - {response.json()}")
        return None
    

if __name__ == "__main__":
    text_temp = speech_to_text()
    print(text_temp)