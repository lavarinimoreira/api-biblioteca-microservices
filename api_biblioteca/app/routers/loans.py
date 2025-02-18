from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.models.loan import Emprestimo as EmprestimoModel
from app.models.user import Usuario as UsuarioModel
from app.models.book import Livro as LivroModel
from app.schemas.loan import EmprestimoCreate, EmprestimoOut, EmprestimoUpdate
from app.database import get_db
from app.services.security import get_current_user


router = APIRouter(prefix="/emprestimos", tags=["Emprestimos"])

# Criar um novo emprestimo (apenas usuários com "loan.create" podem criar empréstimos)
@router.post("/", response_model=EmprestimoOut, status_code=status.HTTP_201_CREATED)
async def criar_emprestimo(emprestimo: EmprestimoCreate, current_user: UsuarioModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if "loan.create" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para criar empréstimos.")
    # Verificar se o usuario existe
    usuario = await db.get(UsuarioModel, emprestimo.usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Verificar se o livro existe
    livro = await db.get(LivroModel, emprestimo.livro_id)
    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")

    # Verificar se o livro está disponível
    if livro.quantidade_disponivel <= 0:
        raise HTTPException(status_code=400, detail="Livro indisponível para empréstimo")

    # Criar o emprestimo com prazo de 7 dias
    novo_emprestimo = EmprestimoModel(
        usuario_id=emprestimo.usuario_id,
        livro_id=emprestimo.livro_id,
        data_emprestimo=datetime.now(),
        data_devolucao=datetime.now() + timedelta(days=7),
        numero_renovacoes=0,
        status="Ativo"
    )
    db.add(novo_emprestimo)

    # Atualizar a quantidade de livros disponíveis
    livro.quantidade_disponivel -= 1

    await db.commit()
    await db.refresh(novo_emprestimo)

    return novo_emprestimo

from sqlalchemy.future import select

# Listar todos os empréstimos de um determinado usuário (permitido apenas a usuários com o namespace "loan.read_by_client")
@router.get("/", response_model=list[EmprestimoOut])
async def listar_emprestimos(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verificar se o usuário tem a permissão necessária
    if "loan.read_by_client" not in current_user.get("permissoes", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada."
        )

    # Consultar os empréstimos do usuário autenticado
    query = select(EmprestimoModel).where(EmprestimoModel.usuario_id == current_user["id"])
    result = await db.execute(query)
    emprestimos = result.scalars().all()

    return emprestimos

# Obter emprestimo por ID (permitido apenas a usuários com o namespace "admin.read")
@router.get("/{emprestimo_id}", response_model=EmprestimoOut)
async def obter_emprestimo(emprestimo_id: int, current_user: UsuarioModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Verificar se o usuário tem a permissão necessária
    if "admin.read" not in current_user.get("permissoes", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada."
        )
    emprestimo = await db.get(EmprestimoModel, emprestimo_id)
    if not emprestimo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empréstimo não encontrado")
    return emprestimo


# Atualizar emprestimo (permitido apenas a usuários com o namespace "loan.renew")
@router.put("/{emprestimo_id}", response_model=EmprestimoOut)
async def atualizar_emprestimo(
    emprestimo_id: int, 
    emprestimo_update: EmprestimoUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    # Verificar se o usuário tem a permissão necessária
    if "loan.renew" not in current_user.get("permissoes", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada."
        )
    emprestimo = await db.get(EmprestimoModel, emprestimo_id)
    if not emprestimo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empréstimo não encontrado")

    # Impedir renovação se o status for 'Atrasado'
    # if emprestimo.status == "Atrasado":
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O empréstimo está atrasado.")

    # Renovar emprestimo
    if emprestimo_update.status == "Renovado":
        if emprestimo.numero_renovacoes >= 3:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Limite de renovações atingido")
        emprestimo.numero_renovacoes += 1
        emprestimo.data_devolucao += timedelta(days=7)
        emprestimo.status = "Renovado"

    # Devolução de empréstimo
    elif emprestimo_update.status == "Devolvido" and emprestimo.status != "Devolvido":
        livro = await db.get(LivroModel, emprestimo.livro_id)
        livro.quantidade_disponivel += 1
        emprestimo.status = "Devolvido"
        emprestimo.data_devolucao = datetime.now()

    await db.commit()
    await db.refresh(emprestimo)
    return emprestimo


# Deletar emprestimo (permitido apenas a usuários com o namespace "admin.delete")
@router.delete("/{emprestimo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_emprestimo(emprestimo_id: int, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Verificar se o usuário tem a permissão necessária
    if "loan.renew" not in current_user.get("permissoes", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada."
        )
    emprestimo = await db.get(EmprestimoModel, emprestimo_id)
    if not emprestimo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empréstimo não encontrado")

    # Se o empréstimo ainda estiver ativo, devolver o livro antes de deletar
    if emprestimo.status == "Ativo":
        livro = await db.get(LivroModel, emprestimo.livro_id)
        livro.quantidade_disponivel += 1

    await db.delete(emprestimo)
    await db.commit()
    return None