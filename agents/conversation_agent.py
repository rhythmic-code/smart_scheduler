# agents/conversation_agent.py
from services.llm_service import LLMService
from agents.calendar_agent import CalendarAgent
from utils.time_utils import parse_relative_date
import re

# Response templates
RESPONSE_TEMPLATES = {
    "no_events": "No events on {date}",
    "events_found": "On {date}: {events}",
    "ask_duration": "How long?",
    "ask_time": "What time?",
    "confirm_schedule": "Scheduled {summary} at {time}",
    "fallback": "Could you repeat that?"
}

class ConversationAgent:
    def __init__(self):
        self.llm_service = LLMService()
        self.calendar_agent = CalendarAgent()
        self.context = {}
    
    def handle_user_request(self, user_input):
        # Step 1: Quick intent detection
        intent = self.detect_simple_intent(user_input)
        if intent:
            return RESPONSE_TEMPLATES[intent], [], []
        
        # Step 2: LLM parameter extraction
        params = self.llm_service.extract_parameters(user_input)
        
        # Step 3: Handle query intent
        if params.get("intent") == "query":
            date_str = params.get("date", user_input)
            return self.handle_date_query(date_str)
        
        # ... rest of scheduling logic ...
    
    def detect_simple_intent(self, user_input):
        """Quick regex-based intent detection"""
        lower_input = user_input.lower()
        
        if re.search(r"\b(any|events?|scheduled|on|for)\b.*\b(june|24|twenty fourth)\b", lower_input):
            return "no_events"
        if re.search(r"\b(how long|duration|length)\b", lower_input):
            return "ask_duration"
        if re.search(r"\b(when|what time|time)\b", lower_input):
            return "ask_time"
        return None
    
    def handle_date_query(self, date_str):
        """Handle date queries without LLM"""
        try:
            date_obj = parse_relative_date(date_str)
            events = self.calendar_agent.get_events_on_date(date_obj)
            
            if not events:
                return RESPONSE_TEMPLATES["no_events"].format(date=date_str), [], []
            
            event_list = ", ".join([e['summary'] for e in events[:3]])
            if len(events) > 3:
                event_list += f" and {len(events)-3} more"
                
            return RESPONSE_TEMPLATES["events_found"].format(
                date=date_str,
                events=event_list
            ), events, []
        except:
            return RESPONSE_TEMPLATES["fallback"], [], []