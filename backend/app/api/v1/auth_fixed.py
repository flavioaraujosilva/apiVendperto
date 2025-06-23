import sys
sys.path.append('/app/app')

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

# Imports absolutos
from core.database import obter_db
from core.seguranca import criarTokenAcesso, verificarToken
from esquemas.usuario import UsuarioCreate, UsuarioResponse, Token, RespostaPadrao, UsuarioLogin
from servicos.usuario import usuario_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/registrar", response_model=RespostaPadrao)
async def registrar_usuario(
    dados_usuario: UsuarioCreate,
    db: Session = Depends(obter_db)
):
    """Registra um novo usuário no sistema"""
    
    # Verificar se usuário já existe
    usuario_existente = usuario_service.obterUsuarioPorEmail(db, dados_usuario.email)
    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado no sistema"
        )
    
    # Validar CPF se fornecido
    if dados_usuario.cpf and not usuario_service.validarCpf(dados_usuario.cpf):
        raise HTTPException(
            status_code=400,
            detail="CPF inválido"
        )
    
    # Criar usuário
    usuario = usuario_service.criarUsuario(db, dados_usuario)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Usuário registrado com sucesso",
        dados={"usuario_id": usuario.id, "email": usuario.email},
        timestamp=datetime.now()
    )

@router.post("/login", response_model=Token)
async def fazer_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(obter_db)
):
    """Realiza login do usuário"""
    
    usuario = usuario_service.autenticarUsuario(
        db, 
        email=form_data.username, 
        senha=form_data.password
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo",
        )
    
    # Criar token de acesso
    access_token = criarTokenAcesso(
        dados={"sub": usuario.email, "perfil": usuario.perfil}
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/login-json", response_model=Token)
async def fazer_login_json(
    dados_login: UsuarioLogin,
    db: Session = Depends(obter_db)
):
    """Realiza login do usuário com JSON"""
    
    usuario = usuario_service.autenticarUsuario(
        db, 
        email=dados_login.email, 
        senha=dados_login.senha
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo",
        )
    
    # Criar token de acesso
    access_token = criarTokenAcesso(
        dados={"sub": usuario.email, "perfil": usuario.perfil}
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/usuario-atual", response_model=UsuarioResponse)
async def obter_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(obter_db)
):
    """Obtém dados do usuário logado"""
    
    email = verificarToken(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    usuario = usuario_service.obterUsuarioPorEmail(db, email)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return usuario 