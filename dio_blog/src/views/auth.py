from pydantic import BaseModel

class LoginOut(BaseModel):
    acess_token: str