class GoyaxScrapperError(Exception):
    """Base exception class for all GoyaxScrapper related errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RequestExceptionError(GoyaxScrapperError):
    """Raised when there's an error making the HTTP request."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DataExtractionError(GoyaxScrapperError):
    """Raised when there's an error extracting data from the page."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TableDataExtractionError(GoyaxScrapperError):
    """Raised when there's an error extracting table data."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UnlistedDataExtractionError(GoyaxScrapperError):
    """Raised when there's an error extracting unlisted (side) data."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class FileSaveError(GoyaxScrapperError):
    """Raised when there's an error saving data to a file."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
