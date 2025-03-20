from dates import parse_date
from log_config import logger

def filter_entries_by_date(entries, start_date_str, end_date_str):
    """Filter entries to only include those within the given date range."""
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)

    logger.info(f"Filtering from {start_date.strftime('%d.%m.%Y')} to {end_date.strftime('%d.%m.%Y')}")

    filtered_entries = []
    for entry in entries:
        entry_date_str = entry.get('date_check')
        status = entry.get('status', '').strip().lower()
        
        if not entry_date_str or status not in ['ready', 'in progress']:
            continue
        
        try:
            entry_date = parse_date(entry_date_str)
            logger.info(f"Checking entry date: {entry_date.strftime('%d.%m.%Y')} (Parsed from {entry_date_str})")
            if start_date <= entry_date <= end_date:
                filtered_entries.append(entry)
        except ValueError:
            logger.warning(f"Skipping invalid date format: {entry_date_str}")
            continue  # Skip invalid date formats

    logger.info(f"Entries after filtering: {len(filtered_entries)}")
    return filtered_entries