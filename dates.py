from datetime import datetime
from custom_exceptions import DataValidationError
from config import DATE_FORMAT

def parse_date(date_str):
    """Convert a date string to a datetime object, ensuring it matches the expected format."""
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except ValueError as e:
        raise DataValidationError(f"Invalid date format: {date_str}", invalid_data=date_str)