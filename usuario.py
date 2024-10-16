from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from usuario_model import UsuarioModel
from usuario_schema import Usuario, UsuarioCartoes, UsuarioAtualizar, UsuarioCriarSenha
from app.core.deps import get_session, get_current_user
from app.core.security import gerar_hash_senha
from app.core.auth import autenticar, criar_token_acesso

router = APIRouter()


@router.post("/cadastro", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def post_cadastro(usuario: UsuarioCriarSenha, db: AsyncSession = Depends(get_session)) -> Usuario:
    novo_usuario = UsuarioModel(
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        senha=gerar_hash_senha(usuario.senha)
    )
    try:
        db.add(novo_usuario)
        await db.commit()
        await db.refresh(novo_usuario)
        return Usuario.model_validate(novo_usuario)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Já existe um usuário com esse e-mail cadastrado."
        )


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_session)) -> JSONResponse:
    usuario = await autenticar(email=form_data.username, senha=form_data.password, db=db)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dados de acesso incorretos."
        )

    return JSONResponse(
        content={
            "access_token": criar_token_acesso(sub=str(usuario.id)),
            "token_type": "bearer"
        },
        status_code=status.HTTP_200_OK
    )


@router.get("/atual", response_model=Usuario)
def get_logado(usuario_logado: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario_logado


@router.get("/{usuario_id}", response_model=UsuarioCartoes, status_code=status.HTTP_200_OK)
async def get_usuario(usuario_id: int, db: AsyncSession = Depends(get_session)) -> UsuarioCartoes:
    query = select(UsuarioModel).filter_by(id=usuario_id)
    result = await db.execute(query)
    usuario = result.scalars().unique().one_or_none()

    if usuario:
        return UsuarioCartoes.model_validate(usuario)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )


@router.put("/{usuario_id}", response_model=Usuario, status_code=status.HTTP_202_ACCEPTED)
async def put_usuario(usuario_id: int,
                      usuario_atualizado: UsuarioAtualizar,
                      db: AsyncSession = Depends(get_session)) -> Usuario:
    query = select(UsuarioModel).filter_by(id=usuario_id)
    result = await db.execute(query)
    usuario = result.scalars().unique().one_or_none()

    if usuario:
        if usuario_atualizado.nome_completo is not None:
            usuario.nome_completo = usuario_atualizado.nome_completo
        if usuario_atualizado.email is not None:
            usuario.email = usuario_atualizado.email
        if usuario_atualizado.senha is not None:
            usuario.senha = gerar_hash_senha(usuario_atualizado.senha)

        await db.commit()
        return Usuario.model_validate(usuario)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id: int, db: AsyncSession = Depends(get_session)) -> JSONResponse:
    query = select(UsuarioModel).filter_by(id=usuario_id)
    result = await db.execute(query)
    usuario = result.scalars().unique().one_or_none()

    if usuario:
        await db.delete(usuario)
        await db.commit()
        return JSONResponse(
            content={"message": "Exclusão feita com sucesso."},
            status_code=status.HTTP_200_OK
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
