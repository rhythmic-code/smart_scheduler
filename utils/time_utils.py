# utils/time_utils.py
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re

# Mapping of ordinal words to numbers
ORDINAL_MAP = {
    'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
    'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10,
    'eleventh': 11, 'twelfth': 12, 'thirteenth': 13, 'fourteenth': 14,
    'fifteenth': 15, 'sixteenth': 16, 'seventeenth': 17, 'eighteenth': 18,
    'nineteenth': 19, 'twentieth': 20, 'twenty first': 21, 'twenty second': 22,
    'twenty third': 23, 'twenty fourth': 24, 'twenty fifth': 25, 
    'twenty sixth': 26, 'twenty seventh': 27, 'twenty eighth': 28,
    'twenty ninth': 29, 'thirtieth': 30, 'thirty first': 31
}

# Month names mapping
MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}

def parse_relative_date(date_str):
    """Parse relative date expressions including 'twenty fourth june' format"""
    if not date_str:
        return None
        
    # Convert to lowercase for case-insensitive matching
    date_str = date_str.lower()
    today = datetime.now().date()
    current_year = today.year
    
    # Handle special cases first
    if date_str == "tomorrow":
        return today + timedelta(days=1)
    elif date_str == "today":
        return today
    elif date_str == "yesterday":
        return today - timedelta(days=1)
    elif "next week" in date_str:
        return today + timedelta(weeks=1)
    elif "last week" in date_str:
        return today - timedelta(weeks=1)
    elif "next month" in date_str:
        return (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    elif "last month" in date_str:
        return (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    
    # Handle "next monday", "next tuesday", etc.
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(days):
        if f"next {day}" in date_str:
            # Calculate days until next occurrence
            days_ahead = (i - today.weekday() + 7) % 7
            if days_ahead == 0:  # Today is the day, so next week
                days_ahead = 7
            return today + timedelta(days=days_ahead)
    
    # Handle "twenty fourth june" format
    for ordinal, number in ORDINAL_MAP.items():
        if ordinal in date_str:
            # Extract the month name
            month_name = next((m for m in MONTH_MAP if m in date_str), None)
            if month_name:
                month_num = MONTH_MAP[month_name]
                # Try to create a date with current year
                try:
                    return datetime(current_year, month_num, number).date()
                except ValueError:
                    # Invalid date (e.g., February 30)
                    continue
    
    # Try standard parsing
    try:
        return date_parser.parse(date_str, default=datetime.now()).date()
    except:
        # Fallback: extract numbers from string
        numbers = re.findall(r'\d+', date_str)
        if numbers:
            try:
                day = int(numbers[0])
                month = today.month
                year = today.year
                
                # Check if month name is present
                month_name = next((m for m in MONTH_MAP if m in date_str), None)
                if month_name:
                    month = MONTH_MAP[month_name]
                
                # Check if year is mentioned
                year_match = re.search(r'\b(20\d{2})\b', date_str)
                if year_match:
                    year = int(year_match.group(1))
                
                return datetime(year, month, day).date()
            except:
                return None
        return None

def parse_time_constraint(constraint, existing_events, current_date=None, current_time_range=None):
    """Parse complex time constraints with better event name extraction"""
    if not constraint:
        return current_date, current_time_range
        
    constraint = constraint.lower()
    
    # Handle relative to events - improved pattern
    event_match = re.search(r'\b(before|after)\b\s+(?:my|the)?\s*(meeting|event|appointment)\s+(?:called|named|titled)?\s*["\']?(.*?)(?:\b|$|["\'])', constraint)
    
    if event_match:
        relation = event_match.group(1)  # "before" or "after"
        event_type = event_match.group(2)  # "meeting", "event", etc.
        event_name = event_match.group(3).strip()
        
        if event_name:
            # Find reference event - use the most similar event
            best_match = None
            best_score = 0
            
            for ev in existing_events:
                summary = ev['summary'].lower()
                # Simple similarity check - could be improved
                similarity = len(set(event_name.split()) & set(summary.split()))
                if similarity > best_score:
                    best_match = ev
                    best_score = similarity
            
            if best_match:
                ref_start = date_parser.parse(best_match['start'].get('dateTime', best_match['start'].get('date')))
                ref_end = date_parser.parse(best_match['end'].get('dateTime', best_match['end'].get('date')))
                
                if relation == "before":
                    current_date = ref_start.date()
                    current_time_range = f"before {ref_start.strftime('%H:%M')}"
                elif relation == "after":
                    current_date = ref_end.date()
                    current_time_range = f"after {ref_end.strftime('%H:%M')}"
    
    # Handle day of week constraints
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in days:
        if day in constraint:
            today = datetime.now().date()
            target_index = days.index(day)
            days_ahead = (target_index - today.weekday() + 7) % 7
            if days_ahead == 0:  # Today is the day, so next week
                days_ahead = 7
            current_date = today + timedelta(days=days_ahead)
    
    # Handle time of day constraints
    if "morning" in constraint:
        current_time_range = "morning"
    elif "afternoon" in constraint:
        current_time_range = "afternoon"
    elif "evening" in constraint:
        current_time_range = "evening"
    elif "night" in constraint:
        current_time_range = "night"
    
    # Handle specific time constraints
    time_match = re.search(r'\b(\d{1,2}:\d{2})\s*(am|pm)?\b', constraint, re.IGNORECASE)
    if time_match:
        time_str = time_match.group(1)
        period = time_match.group(2).lower() if time_match.group(2) else ""
        if period == "pm" and ":" in time_str:
            hours, minutes = time_str.split(":")
            if int(hours) < 12:
                time_str = f"{int(hours)+12}:{minutes}"
        elif period == "am" and time_str.startswith("12"):
            time_str = f"00:{time_str.split(':')[1]}"
        
        current_time_range = time_str
    
    return current_date, current_time_range