from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from app.core import *

from app.api.v1 import routers


app = FastAPI()
app.include_router(routers.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error": exc.__class__.__name__,
            "message": exc.detail,
        },
    )


if __name__ == "__main__":
    setup_logging()

    uvicorn.run(app, log_config=None)
