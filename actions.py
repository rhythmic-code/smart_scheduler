from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from services.calendar_service import find_available_slots, create_event

class ActionScheduleMeeting(Action):
    def name(self) -> Text:
        return "action_schedule_meeting"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = tracker.get_slot("date")
        time = tracker.get_slot("time")
        
        if not date or not time:
            dispatcher.utter_message("Please specify date and time")
            return []

        # Create event using calendar service
        event_link = create_event(
            summary="Scheduled Meeting",
            start_iso=f"{date}T{time}:00",
            end_iso=f"{date}T{int(time)+1}:00"  # 1-hour meeting
        )
        
        dispatcher.utter_message(f"Meeting scheduled! View here: {event_link}")
        return []