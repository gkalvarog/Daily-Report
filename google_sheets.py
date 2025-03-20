import datetime
import time  
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from collections import defaultdict
from functools import lru_cache
from config import CREDENTIALS_PATH, SCOPES, SHEET_IDS, COLUMN_MAP, REQUIRED_COLUMNS
from custom_exceptions import GoogleSheetsAPIError, DataValidationError
from log_config import logger
from filtering import filter_entries_by_date

_cache = {}

def authenticate():
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        return creds
    except Exception as e:
        logger.error(f"Google Sheets authentication failed: {str(e)}")
        raise GoogleSheetsAPIError("Failed to authenticate with Google Sheets", details=str(e))

def get_entries_in_range(sheet_id, start_date_str, end_date_str):
    """Fetch entries between dates with 'Ready' or 'In Progress' status using Sheets API v4"""
    cache_key = f"{sheet_id}-{start_date_str}-{end_date_str}"
    if cache_key in _cache:
        return _cache[cache_key]
    
    try:
        creds = authenticate()
        service = build('sheets', 'v4', credentials=creds)
    except GoogleSheetsAPIError as e:
        logger.error(f"Google Sheets API Error: {e.details}")
        raise
    
    all_entries = []
    try:
        spreadsheet_metadata = service.spreadsheets().get(spreadsheetId=sheet_id, includeGridData=False).execute()
        sheet_titles = [sheet['properties']['title'] for sheet in spreadsheet_metadata.get('sheets', [])]
    except Exception as e:
        logger.error(f"Failed to fetch spreadsheet metadata: {str(e)}")
        raise GoogleSheetsAPIError("Failed to fetch spreadsheet metadata", details=str(e))
    
    ranges = [f"{title}!A1:Z" for title in sheet_titles]
    try:
        batch_data = service.spreadsheets().values().batchGet(
            spreadsheetId=sheet_id,
            ranges=ranges,
            valueRenderOption="UNFORMATTED_VALUE",
            dateTimeRenderOption="FORMATTED_STRING"
        ).execute()
    except Exception as e:
        logger.error(f"Failed to fetch sheet data: {str(e)}")
        raise GoogleSheetsAPIError("Failed to fetch sheet data", details=str(e))
    
    for sheet_data in batch_data.get('valueRanges', []):
        sheet_title = sheet_data['range'].split('!')[0].strip("'\"")
        rows = sheet_data.get('values', [])
        
        if not rows:
            logger.warning(f"Skipping sheet {sheet_title} - No data found")
            continue
        
        headers = [cell.strip().lower() for cell in rows[0]]
        header_index = {COLUMN_MAP.get(header, header): idx for idx, header in enumerate(headers)}
        
        logger.info(f"Detected headers in sheet {sheet_title}: {headers}")
        
        if 'employee id' not in headers or 'vip' not in headers:
            logger.error(f"Missing required columns in sheet {sheet_title}: {set(['employee id', 'vip']) - set(headers)}")
            continue
        
        missing = REQUIRED_COLUMNS - set(header_index.keys())
        if missing:
            logger.warning(f"Skipping sheet {sheet_title} - Missing columns: {missing}")
            continue
        
        for row_idx, row in enumerate(rows[1:], start=2):
            try:
                values = [str(cell).strip() for cell in row]
                
                employee_id_index = headers.index('employee id')
                vip_index = headers.index('vip')
                employee_id = values[employee_id_index] if len(values) > employee_id_index else "Unknown"
                vip = values[vip_index] if len(values) > vip_index else "Unknown"
                
                entry = {
                    'agent': sheet_title,
                    'date_check': values[header_index['date_check']] if len(values) > header_index['date_check'] else '',
                    'status': values[header_index['status']].lower().strip() if len(values) > header_index['status'] else '',
                    'VIP': vip,
                    'Employee ID': employee_id,
                    'timing': float(values[header_index['timing']] or 0),
                    'crit': float(values[header_index['crit']] or 0),
                    'crit_type': (values[header_index['crit_type']] if len(values) > header_index['crit_type'] else '').strip(),
                    'crit_50': 0,
                    'crit_50_type': [],
                    'crit_100': 0,
                    'crit_100_type': []
                }
                
                if entry['timing'] == -100.0:
                    entry['crit_100'] += 1
                    entry['crit_100_type'].append("Timing")
                if entry['timing'] == -50.0:
                    entry['crit_50'] += 1
                    entry['crit_50_type'].append("Timing")
                
                if entry['crit'] == -50.0:
                    entry['crit_50'] += 1
                    entry['crit_50_type'].append(entry['crit_type'])
                elif entry['crit'] == -100.0:
                    entry['crit_100'] += 1
                    entry['crit_100_type'].append(entry['crit_type'])
                
                entry['crit_50_type'] = ', '.join(entry['crit_50_type']) if entry['crit_50_type'] else ''
                entry['crit_100_type'] = ', '.join(entry['crit_100_type']) if entry['crit_100_type'] else ''
                
                all_entries.append(entry)
            except Exception as e:
                logger.error(f"Error processing row {row_idx} in sheet {sheet_title}: {str(e)}")
                continue  
    
    logger.info(f"Total raw entries fetched: {len(all_entries)}")
    _cache[cache_key] = filter_entries_by_date(all_entries, start_date_str, end_date_str)
    logger.info(f"Total entries after filtering: {len(_cache[cache_key])}")
    return _cache[cache_key]