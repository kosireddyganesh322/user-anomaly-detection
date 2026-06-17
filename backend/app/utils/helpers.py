from datetime import datetime

def is_off_hours(dt: datetime) -> bool:
    """Returns True if login is outside 08:00–18:00 Mon–Fri."""
    if dt.weekday() >= 5:
        return True
    return not (8 <= dt.hour < 18)
