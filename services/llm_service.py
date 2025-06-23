# services/llm_service.py
import requests
import json
import re
from config import LLM_URL, LLM_MODEL, LLM_TEMPERATURE, LLM_CONVERSATION_TEMP

class LLMService:
    def __init__(self):
        self.base_url = LLM_URL
        self.default_model = LLM_MODEL
    
    def extract_parameters(self, user_input):
        """Improved parameter extraction with fallback to faster model"""
        # Use smaller model for short queries
        model = "llama3" if len(user_input.split()) < 10 else self.default_model
        
        prompt = f"""
        You are an expert calendar assistant. Extract meeting parameters from:
        "{user_input}"
        
        Focus on:
        - Event summary
        - Date (handle formats like 'twenty fourth june')
        - Time/duration
        
        Return JSON with:
        - "summary": string or null
        - "date": string (natural language date)
        - "time_range": string
        - "duration": integer or null
        - "intent": "schedule/query/cancel"
        """
        
        payload = {
            "model": model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 100}
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=3)
            return response.json().get("response", {})
        except:
            return {"intent": "query", "date": user_input}  # Fallback
    
    def generate_conversation_response(self, conversation_state):
        """Generate response with optimized prompt"""
        prompt = f"""
        You are a scheduling assistant. Given this context:
        {json.dumps(conversation_state, indent=2)}
        
        Respond in 1 SHORT sentence. Be concise.
        """
        
        payload = {
            "model": "gemma:2b",  # Always use fast model for responses
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 50}
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=3)
            return response.json().get("response", "").strip()
        except:
            return "Please repeat that."