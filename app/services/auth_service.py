from sqlalchemy.orm import Session

from app.auth.security import hash_senha, verificar_senha
from app.database.models import Usuario


def registrar_usuario(session: Session, email: str, senha: str) -> Usuario:
    existente = session.query(Usuario).filter(Usuario.email == email).first()

    if existente:
        raise ValueError("Já existe uma conta cadastrada com esse e-mail.")

    usuario = Usuario(email=email, senha_hash=hash_senha(senha))
    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return usuario


def autenticar_usuario(session: Session, email: str, senha: str) -> Usuario | None:
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        return None

    return usuario