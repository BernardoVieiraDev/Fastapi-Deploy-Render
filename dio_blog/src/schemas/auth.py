from pydantic import BaseModel

from src.security import AccessToken

class LoginIn(BaseModel):
    user_id : int

class JWTToken(BaseModel):
    access_token: AccessToken
