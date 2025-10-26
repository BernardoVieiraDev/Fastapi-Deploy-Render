from fastapi import APIRouter
from pydantic import BaseModel

from .security import sign_jwt, TokenResponse  # importa o gerador de token e modelo de resposta

router = APIRouter(prefix="/auth", tags=["auth"])


# Modelo de entrada para o login
class LoginRequest(BaseModel):
    user_id: int  # ou 'email', 'username', 'password' — conforme sua lógica


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    """
    Endpoint de login — retorna um token JWT para o usuário autenticado.
    """
    # Aqui você normalmente validaria o usuário no banco antes de gerar o token.
    # Exemplo: validar se o user_id existe e se a senha está correta.

    return sign_jwt(user_id=data.user_id)
