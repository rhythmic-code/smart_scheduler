# config.py
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Google Calendar configuration
CALENDAR_TIMEZONE = 'Asia/Kolkata'
WORKING_HOURS = (9, 18)  # 9AM to 6PM
DEFAULT_DURATION = 30  # minutes
SLOT_INTERVAL = 15  # minutes
SCOPES = ['https://www.googleapis.com/auth/calendar']
GCAL_CREDS_PATH = os.path.join(BASE_DIR, "gcal", "credentials.json")
GCAL_TOKEN_PATH = os.path.join(BASE_DIR, "gcal", "token.json")

# Voice configuration
VOICE_SAMPLE_RATE = 16000
VOICE_CHANNELS = 1
VOICE_SUBTYPE = "PCM_16"

# Vosk configuration
VOSK_MODEL_NAME = "vosk-model-en-us-0.22"  # Model name for auto-download

# LLM configuration (Ollama)
LLM_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3"  # powerful model
LLM_TEMPERATURE = 0.1  # For structured responses
LLM_CONVERSATION_TEMP = 0.7  # For conversational responses

# Speech Recognition
ENERGY_THRESHOLD = 4000  # Adjust based on mic sensitivity
PAUSE_THRESHOLD = 0.8  # seconds of silence to end speech

# Add Rasa SDK endpoint
RASA_ACTION_ENDPOINT = "http://localhost:5055/webhook"