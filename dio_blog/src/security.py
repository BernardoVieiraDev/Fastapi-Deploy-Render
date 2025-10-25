import time
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

# Configurações do JWT
SECRET = "my-secret"
ALGORITHM = "HS256"


# ===== MODELOS =====

class AccessToken(BaseModel):
    iss: str    #issuer: quem emitiu o token.
    sub: int    #subject: quem é o dono do token (ex: o ID do usuário).
    aud: str    #audience: para quem o token é destinado.
    exp: float  #expiration time: quando o token expira.
    iat: float  #issued at: quando o token foi emitido.
    nbf: float  #not before: o token só é válido depois desse tempo.
    jti: str    #JWT ID: um identificador único do token (para rastreamento/revogação).


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


# ===== FUNÇÕES DE TOKEN =====

def sign_jwt(user_id: int) -> TokenResponse:
    """
    Gera e retorna um JWT válido para o usuário.
    """
    now = time.time()
    payload = {
        "iss": "curso-fastapi.com.br",
        "sub": user_id,
        "aud": "curso-fastapi",
        "exp": now + (60 * 30),  # expira em 30 minutos
        "iat": now,
        "nbf": now,
        "jti": uuid4().hex,
    }

    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    # Compatibilidade caso o retorno seja bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return TokenResponse(access_token=token) #type: ignore


async def decode_jwt(token: str) -> AccessToken | None:
    """
    Decodifica e valida o JWT recebido.
    Retorna o payload decodificado como AccessToken se válido, senão None.
    """
    try:
        decoded_token = jwt.decode(
            token,
            SECRET,
            audience="curso-fastapi",
            algorithms=[ALGORITHM]
        )
        access_token = AccessToken(**decoded_token)

        # Verifica se o token ainda é válido
        if access_token.exp < time.time():
            return None

        return access_token
    except Exception:
        return None


# ===== MIDDLEWARE DE AUTENTICAÇÃO =====

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> AccessToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization token."
            )

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme."
            )

        access_token = await decode_jwt(credentials)
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token."
            )

        return access_token


# ===== DEPENDÊNCIAS DE USUÁRIO =====

async def get_current_user(token: Annotated[AccessToken, Depends(JWTBearer())]) -> dict[str, int]:
    """
    Retorna o usuário atual autenticado.
    """
    return {"user_id": token.sub}


def login_required(current_user: Annotated[dict[str, int], Depends(get_current_user)]):
    """
    Garante que a rota seja acessada apenas por usuários autenticados.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return current_user
