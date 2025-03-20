class ReportError(Exception):
    """Base class for report-related errors."""
    pass

class GoogleSheetsAPIError(ReportError):
    """Raised when there is an issue with Google Sheets API calls."""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details

class DataValidationError(ReportError):
    """Raised when data does not meet validation criteria."""
    def __init__(self, message, invalid_data=None):
        super().__init__(message)
        self.invalid_data = invalid_data

class ReportGenerationError(ReportError):
    """Raised when an error occurs during report generation."""
    def __init__(self, message):
        super().__init__(message)
