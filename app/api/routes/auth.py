from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import TokenOut, UsuarioCreate, UsuarioOut
from app.auth.security import criar_token_acesso
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/registrar", response_model=UsuarioOut, status_code=201)
def registrar(payload: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return auth_service.registrar_usuario(db, payload.email, payload.senha)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form.username carrega o e-mail (padrão do OAuth2PasswordRequestForm)
    usuario = auth_service.autenticar_usuario(db, form.username, form.password)

    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    token = criar_token_acesso(usuario.id)
    return TokenOut(access_token=token)