from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.authentication import AuthenticationError

def http_exception_error(request: Request, exc: HTTPException):
    print(exc.detail)
    return JSONResponse(status_code=exc.status_code,
                        content={"desc": f"{exc.detail}"})


class UserAuthenticationError(AuthenticationError):

    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

    def __str__(self):
        return f"{self.status_code}: {self.detail}"


def auth_user_error(request: Request, exc: UserAuthenticationError):
    return JSONResponse(status_code=exc.status_code,
                        content={"desc": exc.detail})
