import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
REPORT_OUTPUT_DIR = os.path.join(BASE_DIR, 'reports')

# Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_IDS = ['1HiHI8KJcke6vX3fZduMxTxOQrKtWhaDlwuL3JlIdR-4']

# Date formats
DATE_FORMAT = "%d.%m.%Y"

# Column mappings
COLUMN_MAP = {
    'employee id': 'Employee ID',
    'date check': 'date_check',
    'vip': 'vip',
    'ready/in progress': 'status',
    'timing': 'timing',
    'crit': 'crit',
    'crit type': 'crit_type'
}

# Required columns for processing sheets
REQUIRED_COLUMNS = {'date_check', 'status', 'timing', 'crit', 'crit_type', 'vip'}

# Report settings
REPORT_SETTINGS = {
    'FILENAME_FORMAT': 'Daily_Report_{date}.txt',
    'SEPARATOR': '=',
    'WIDTH': 50
}
