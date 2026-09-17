from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.schemas import HistoricoPontoOut, ProdutoCreate, ProdutoOut, ProdutoUpdate
from app.database.models import Usuario
from app.services import product_service
from app.services.price_checker import verificar_produto

router = APIRouter(prefix="/api/produtos", tags=["produtos"])


@router.get("", response_model=list[ProdutoOut])
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return product_service.listar_produtos(db, usuario.id)


@router.post("", response_model=ProdutoOut, status_code=201)
def cadastrar(
    payload: ProdutoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return product_service.cadastrar_via_url(db, usuario.id, payload.url, payload.preco_alvo)
    except ValueError as e:
        # Ex: domínio sem scraper implementado, URL sem ID reconhecível
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Ex: site fora do ar, produto não encontrado na API do marketplace
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível buscar os dados do produto: {e}"
        )


@router.patch("/{produto_id}", response_model=ProdutoOut)
def atualizar(
    produto_id: int,
    payload: ProdutoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    produto = product_service.atualizar_produto(
        db, produto_id, usuario.id, preco_alvo=payload.preco_alvo, ativo=payload.ativo
    )
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.delete("/{produto_id}", status_code=204)
def remover(
    produto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    ok = product_service.remover_produto(db, produto_id, usuario.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Produto não encontrado")


@router.get("/{produto_id}/historico", response_model=list[HistoricoPontoOut])
def historico(
    produto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    resultado = product_service.obter_historico(db, produto_id, usuario.id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return resultado


@router.post("/{produto_id}/verificar", response_model=ProdutoOut)
def verificar_agora(
    produto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    produto = product_service.obter_produto(db, produto_id, usuario.id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    try:
        verificar_produto(db, produto)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao verificar preço: {e}")

    db.refresh(produto)
    return produto