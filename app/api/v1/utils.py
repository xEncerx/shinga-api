from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


def exception_handler(_: Request, exc: HTTPException):
    """
    Built-in exception handler for HTTP exceptions.

    Returns a JSON response with the following structure:
    - Status code
    - Error name
    - Error detail
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error": exc.__class__.__name__,
            "detail": exc.detail,
        },
        headers=exc.headers,
    )
