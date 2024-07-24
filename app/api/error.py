from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


def http_exception_error(request: Request, exc: HTTPException):
    print(exc.detail)
    return JSONResponse(status_code=exc.status_code,
                        content={"desc": f"{exc.detail}"})
