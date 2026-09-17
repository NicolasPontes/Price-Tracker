from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decodificar_token
from app.database.connection import SessionLocal
from app.database.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:

    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar suas credenciais",
        headers={"WWW-Authenticate": "Bearer"}
    )

    usuario_id = decodificar_token(token)
    if usuario_id is None:
        raise credenciais_invalidas

    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise credenciais_invalidas

    return usuario