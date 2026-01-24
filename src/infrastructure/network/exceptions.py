class NetworkError(Exception):
    """Base class for network-related exceptions."""

    pass


# --- HTTP Errors ---
class HttpError(NetworkError):
    """Base class for HTTP-related exceptions."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class HttpTimeoutError(HttpError):
    """Exception raised for HTTP timeout errors."""

    pass


class HttpClientError(HttpError):
    """
    Exception raised for HTTP client errors.

    4xx status codes (Bad Request, Unauthorized, Forbidden, Not Found, etc.)
    """

    pass


class HttpServerError(HttpError):
    """
    Exception raised for HTTP server errors.

    5xx status codes (Internal Server Error, Bad Gateway, Service Unavailable, etc.)
    """


class HttpConnectionError(HttpError):
    """Exception raised for HTTP connection errors. (DNS failure, refused connection, etc.)"""

    pass
