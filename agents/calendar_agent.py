# agents/calendar_agent.py
from datetime import datetime, timedelta
from services.calendar_service import find_available_slots, get_upcoming_events, create_event
from utils.time_utils import parse_relative_date, parse_time_constraint  # Ensure imports

class CalendarAgent:
    def __init__(self):
        self.context = {}
    
    def find_available_slots(self, duration_minutes, preferred_date=None, preferred_time_range=None, constraints=None):
        """Find available slots with advanced constraints handling"""
        parsed_date = preferred_date
        
        # Handle relative dates
        if preferred_date and isinstance(preferred_date, str):
            parsed_date = parse_relative_date(preferred_date)
        
        # Handle complex constraints
        if constraints:
            parsed_date, preferred_time_range = parse_time_constraint(
                constraints, 
                existing_events=get_upcoming_events(7),
                current_date=parsed_date,
                current_time_range=preferred_time_range
            )
        
        # Find available slots
        return find_available_slots(
            duration_minutes=duration_minutes,
            preferred_date=parsed_date,
            preferred_time_range=preferred_time_range
        )
    
    def handle_no_slots(self, original_date):
        """Generate alternative suggestions when no slots are available"""
        alternatives = []
        
        # Try next day
        next_day = original_date + timedelta(days=1)
        next_day_slots = find_available_slots(60, preferred_date=next_day)
        if next_day_slots:
            alternatives.append({
                "date": next_day,
                "slots": next_day_slots[:2]  # First two slots
            })
        
        # Try same day different time range
        for time_range in ["morning", "afternoon", "evening"]:
            range_slots = find_available_slots(60, preferred_date=original_date, preferred_time_range=time_range)
            if range_slots:
                alternatives.append({
                    "time_range": time_range,
                    "slots": range_slots[:2]
                })
        
        return alternatives
    
    def schedule_event(self, summary, slot):
        """Schedule an event at a specific time slot"""
        start_iso = slot.isoformat()
        end_iso = (slot + timedelta(minutes=60)).isoformat()
        return create_event(summary, start_iso, end_iso)