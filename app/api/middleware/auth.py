from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      SimpleUser)

from app.utils import TokenManager


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "X-Auth-Token" not in conn.headers:
            return

        auth = conn.headers["X-Auth-Token"]
        _data = TokenManager.decode_access_token(auth)

        return AuthCredentials(["authenticated"]), SimpleUser(_data.username)
