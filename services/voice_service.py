# services/voice_service.py
import os
import json
import queue
import threading
import tempfile
import sounddevice as sd
import soundfile as sf
import win32com.client  # For Windows TTS
import pyttsx3
from vosk import Model, KaldiRecognizer
from config import VOICE_SAMPLE_RATE, VOICE_CHANNELS, VOICE_SUBTYPE, VOSK_MODEL_NAME

class VoiceInterface:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.vosk_model = None
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")  # Windows TTS
    
    def _download_vosk_model(self):
        """Download and extract Vosk model if not available"""
        try:
            from vosk import Model
            model_dir = os.path.join(os.path.expanduser("~"), ".cache", "vosk")
            model_path = os.path.join(model_dir, VOSK_MODEL_NAME)
            
            # Create cache directory if needed
            os.makedirs(model_dir, exist_ok=True)
            
            # Check if model exists
            if not os.path.exists(model_path):
                print(f"Downloading Vosk model: {VOSK_MODEL_NAME}")
                
                # Download model
                url = f"https://alphacephei.com/vosk/models/{VOSK_MODEL_NAME}.zip"
                zip_path = os.path.join(model_dir, f"{VOSK_MODEL_NAME}.zip")
                
                # Download the zip file
                import requests
                response = requests.get(url, stream=True)
                with open(zip_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract the model
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(model_dir)
                
                # Clean up
                os.remove(zip_path)
                print("Vosk model downloaded successfully")
            
            return Model(model_path)
        except Exception as e:
            print(f"Error downloading Vosk model: {str(e)}")
            return None
    
    def record_audio(self, duration=5):
        """Record audio from microphone"""
        print("Listening...")
        try:
            audio_data = sd.rec(
                int(duration * VOICE_SAMPLE_RATE),
                samplerate=VOICE_SAMPLE_RATE,
                channels=VOICE_CHANNELS,
                dtype='int16'
            )
            sd.wait()
            return audio_data
        except Exception as e:
            print(f"Recording error: {str(e)}")
            return None
    
    # def text_to_speech(self, text):
    #     """Convert text to speech using Windows built-in TTS"""
    #     try:
    #         self.speaker.Speak(text)
            
    #     except Exception as e:
    #         print(f"TTS Error: {str(e)}")
    #         print(f"TTS Output: {text}")



    def text_to_speech(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def speech_to_text(self, audio_data):
        """Convert speech to text using Vosk"""
        try:
            # Lazy-load Vosk model (download if needed)
            if not self.vosk_model:
                self.vosk_model = self._download_vosk_model()
                if not self.vosk_model:
                    return ""
            
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_path = temp_wav.name
                sf.write(temp_path, audio_data, VOICE_SAMPLE_RATE, subtype=VOICE_SUBTYPE)
            
            # Use Vosk recognizer
            recognizer = KaldiRecognizer(self.vosk_model, VOICE_SAMPLE_RATE)
            recognizer.SetWords(False)
            
            result_text = ""
            with open(temp_path, "rb") as audio_file:
                while True:
                    data = audio_file.read(4000)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        result_text += result.get("text", "") + " "
            
            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            result_text += final_result.get("text", "")
            
            # Clean up
            os.remove(temp_path)
            return result_text.strip()
        except Exception as e:
            print(f"STT Error: {str(e)}")
            return ""