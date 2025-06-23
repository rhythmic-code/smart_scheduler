# # main.py
# import time
# from agents.conversation_agent import ConversationAgent
# from services.voice_service import VoiceInterface  # Fixed import
# from utils.logging_utils import LatencyMonitor
# from datetime import timedelta

# def main():
#     print("=== Smart Scheduler AI Agent ===")
#     print("Initializing components...")
    
#     # Create agent and voice interface
#     agent = ConversationAgent()
#     voice_interface = VoiceInterface()  # Create instance
#     latency_monitor = LatencyMonitor()
    
#     print("Starting voice interface...")
#     voice_interface.text_to_speech("Hello! I'm your meeting scheduling assistant. How can I help?")
    
#     while True:
#         try:
#             # Listen for user input
#             audio = voice_interface.record_audio(duration=5)
#             if audio is None:
#                 continue
            
#             # Convert speech to text
#             user_input = voice_interface.speech_to_text(audio)
#             if not user_input:
#                 voice_interface.text_to_speech("Sorry, I didn't catch that. Could you please repeat?")
#                 continue
            
#             print(f"User: {user_input}")
            
#             # Check for exit command
#             if "exit" in user_input.lower() or "quit" in user_input.lower():
#                 voice_interface.text_to_speech("Goodbye! Have a great day.")
#                 break
            
#             # Process with agent
#             latency_monitor.start()
#             agent_response, slots, alternatives = agent.handle_user_request(user_input)
#             processing_time = latency_monitor.stop()
            
#             print(f"Agent ({processing_time:.2f}s): {agent_response}")
            
#             # Convert response to speech
#             tts_start = time.time()
#             voice_interface.text_to_speech(agent_response)
#             tts_time = time.time() - tts_start
            
#             # Maintain low latency (<800ms)
#             total_time = processing_time + tts_time
#             if total_time > 0.8:
#                 print(f"Warning: Response latency {total_time:.2f}s exceeds 800ms")
            
#             # Handle slot selection
#             if slots:
#                 voice_interface.text_to_speech("Please say the number of your preferred option.")
#                 audio = voice_interface.record_audio(duration=3)
#                 choice = voice_interface.speech_to_text(audio)
                
#                 if choice and choice.isdigit():
#                     choice_idx = int(choice) - 1
#                     if 0 <= choice_idx < len(slots):
#                         selected_slot = slots[choice_idx]
#                         # Schedule meeting - use context from agent
#                         meeting_summary = agent.context.get("summary", "Meeting")
#                         meeting_link = agent.calendar_agent.schedule_event(
#                             meeting_summary,
#                             selected_slot
#                         )
#                         voice_interface.text_to_speech(
#                             f"Meeting scheduled for {selected_slot.strftime('%A at %I:%M %p')}"
#                         )
#                     else:
#                         voice_interface.text_to_speech("Invalid selection. Let's start over.")
#                 else:
#                     voice_interface.text_to_speech("I didn't understand your choice. Let's start over.")
#             elif alternatives:
#                 voice_interface.text_to_speech("Please say which alternative you prefer.")
#                 audio = voice_interface.record_audio(duration=5)
#                 choice = voice_interface.speech_to_text(audio)
#                 # Handle alternative selection would go here
        
#         except KeyboardInterrupt:
#             break
#         except Exception as e:
#             print(f"Error in main loop: {str(e)}")
#             voice_interface.text_to_speech("I encountered an error. Let's try again.")

# if __name__ == "__main__":
#     main()

import speech_recognition as sr
import re
import json
import pyttsx3  # Add this import
from datetime import datetime, timedelta
from services.calendar_service import find_available_slots, create_event
from config import CALENDAR_TIMEZONE  # Import your config

class ConversationState:
    """Manage the conversation flow and context"""
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.stage = "START"
        self.duration = 60
        self.preferred_date = None
        self.preferred_time_range = None
        self.available_slots = []
        self.selected_slot = None
        
    def to_dict(self):
        return {
            "stage": self.stage,
            "duration": self.duration,
            "preferred_date": str(self.preferred_date) if self.preferred_date else None,
            "preferred_time_range": self.preferred_time_range,
            "available_slots": [str(s) for s in self.available_slots],
            "selected_slot": str(self.selected_slot) if self.selected_slot else None
        }

class SmartScheduler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.pause_threshold = 0.8
        self.state = ConversationState()
        self.engine = pyttsx3.init()  # Initialize TTS engine once
        
    def text_to_speech(self, text):
        """Convert text to speech and print to console"""
        print(f"Assistant: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def listen(self):
        """Capture voice input and convert to text"""
        with sr.Microphone() as source:
            print("\nListening... (say 'exit' to quit)")
            try:
                audio = self.recognizer.listen(source, timeout=10)
                return self.recognizer.recognize_google(audio)
            except sr.WaitTimeoutError:
                return None
            except Exception as e:
                print(f"Voice error: {e}")
                return None
    
    def parse_command(self, text):
        """Extract information from voice command based on current state"""
        text = text.lower()
        response = ""
        
        # Debug: print current state
        print(f"Current state: {json.dumps(self.state.to_dict(), indent=2)}")
        
        # State machine
        if self.state.stage == "START":
            if "schedule" in text or "meeting" in text:
                self.state.stage = "DURATION"
                response = "Okay! How long should the meeting be in minutes?"
        
        elif self.state.stage == "DURATION":
            # Try to extract duration
            duration_match = re.search(r'(\d+)\s*(minute|min|hour|hr|h|m)', text) or re.search(r'(\d+)', text)
            if duration_match:
                value = int(duration_match.group(1))
                unit = duration_match.group(2) if len(duration_match.groups()) > 1 else "minute"
                
                if unit in ["hour", "hr", "h"]:
                    self.state.duration = value * 60
                else:
                    self.state.duration = value
                
                self.state.stage = "PREFERENCE"
                response = f"Got it. I'm checking for {self.state.duration}-minute slots. " \
                           "Do you have a preferred day or time?"
            else:
                response = "Sorry, I didn't catch the duration. How long should the meeting be?"
        
        elif self.state.stage == "PREFERENCE":
            # Extract date preference
            today = datetime.now().date()
            if "today" in text:
                self.state.preferred_date = today
            elif "tomorrow" in text:
                self.state.preferred_date = today + timedelta(days=1)
            elif "monday" in text:
                self.state.preferred_date = self.next_weekday(today, 0)
            elif "tuesday" in text:
                self.state.preferred_date = self.next_weekday(today, 1)
            elif "wednesday" in text:
                self.state.preferred_date = self.next_weekday(today, 2)
            elif "thursday" in text:
                self.state.preferred_date = self.next_weekday(today, 3)
            elif "friday" in text:
                self.state.preferred_date = self.next_weekday(today, 4)
            elif "saturday" in text:
                self.state.preferred_date = self.next_weekday(today, 5)
            elif "sunday" in text:
                self.state.preferred_date = self.next_weekday(today, 6)
            
            # Extract time preference
            if "morning" in text:
                self.state.preferred_time_range = "morning"
            elif "afternoon" in text:
                self.state.preferred_time_range = "afternoon"
            elif "evening" in text:
                self.state.preferred_time_range = "evening"
            
            # Find available slots
            self.state.available_slots = find_available_slots(
                self.state.duration,
                preferred_date=self.state.preferred_date,
                preferred_time_range=self.state.preferred_time_range
            )
            
            if self.state.available_slots:
                self.state.stage = "OFFER_SLOTS"
                # Format available slots for response
                slots_str = ", ".join(
                    [slot.strftime("%I:%M %p") for slot in self.state.available_slots[:2]]
                )
                day_name = self.state.available_slots[0].strftime("%A") if self.state.preferred_date else "your preferred day"
                response = f"Great. I have {slots_str} available on {day_name}. Which one works for you?"
            else:
                response = "Sorry, I couldn't find available slots. Would you like to try another day or time?"
                self.state.stage = "PREFERENCE"
        
        elif self.state.stage == "OFFER_SLOTS":
            # Try to match selected time
            time_match = re.search(r'(\d{1,2}):?(\d{2})?\s?(am|pm)?', text)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                period = time_match.group(3)
                
                # Convert to 24-hour format
                if period == "pm" and hour < 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                
                # Find matching slot
                for slot in self.state.available_slots:
                    if slot.hour == hour and slot.minute == minute:
                        self.state.selected_slot = slot
                        break
            
            # If no time match, try ordinal selection
            if not self.state.selected_slot:
                if "first" in text or "one" in text or "1" in text:
                    self.state.selected_slot = self.state.available_slots[0] if self.state.available_slots else None
                elif "second" in text or "two" in text or "2" in text:
                    self.state.selected_slot = self.state.available_slots[1] if len(self.state.available_slots) > 1 else None
            
            if self.state.selected_slot:
                self.state.stage = "CONFIRM"
                response = f"Got it. Should I schedule the meeting for {self.state.selected_slot.strftime('%A at %I:%M %p')}?"
            else:
                response = "Sorry, I didn't catch your choice. Please say the time like '2:00 PM' or 'first option'."
        
        elif self.state.stage == "CONFIRM":
            if "yes" in text or "confirm" in text or "sure" in text or "ok" in text:
                # Schedule the meeting
                start_time = self.state.selected_slot
                end_time = start_time + timedelta(minutes=self.state.duration)
                
                start_iso = start_time.isoformat()
                end_iso = end_time.isoformat()
                
                try:
                    event_link = create_event("Scheduled Meeting", start_iso, end_iso)
                    response = f"Meeting scheduled! You can view it at: {event_link}"
                    
                    # Immediately update available slots
                    self.state.available_slots = []
                except Exception as e:
                    response = f"Failed to schedule meeting: {str(e)}"
                
                self.state.reset()
            elif "no" in text or "cancel" in text:
                response = "Okay, let's start over."
                self.state.reset()
            else:
                response = "Please say 'yes' to confirm or 'no' to cancel."
        
        return response

    def next_weekday(self, d, weekday):
        """Get next specific weekday (0=Monday, 6=Sunday)"""
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + timedelta(days_ahead)

    def run(self):
        """Main scheduling loop"""
        self.text_to_speech("Hello! I'm your meeting scheduling assistant.")
        print("Say something like:")
        print("  'Schedule a meeting tomorrow at 3pm'")
        print("  'Set up a meeting on Friday at 11:30am'")
        
        while True:
            try:
                # Get voice input
                text = self.listen()
                if not text:
                    continue
                    
                print(f"You said: {text}")
                
                # Check for exit command
                if "exit" in text.lower() or "quit" in text.lower():
                    self.text_to_speech("Goodbye!")
                    break
                
                # Process the command through state machine
                response = self.parse_command(text)
                self.text_to_speech(response)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                self.text_to_speech("Sorry, I encountered an error. Let's try again.")

if __name__ == "__main__":
    scheduler = SmartScheduler()
    scheduler.run()