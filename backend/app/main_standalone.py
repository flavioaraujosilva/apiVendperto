import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

# Imports locais
from core.database import obter_db, engine, Base
from core.seguranca import criarTokenAcesso, verificarToken
from esquemas.usuario import UsuarioCreate, UsuarioResponse, Token, RespostaPadrao, UsuarioLogin
from servicos.usuario_fixed import usuario_service

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="VendPerto ERP",
    description="Sistema ERP moderno - APIs de Cadastro e Login",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8001",
        "*"  # Para desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ==================== ENDPOINTS DE AUTENTICAÇÃO ====================

@app.post("/api/v1/auth/registrar", response_model=RespostaPadrao)
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

@app.post("/api/v1/auth/login", response_model=Token)
async def fazer_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(obter_db)
):
    """Realiza login do usuário (OAuth2 format)"""
    
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

@app.post("/api/v1/auth/login-json", response_model=Token)
async def fazer_login_json(
    dados_login: UsuarioLogin,
    db: Session = Depends(obter_db)
):
    """Realiza login do usuário (JSON format)"""
    
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

@app.get("/api/v1/auth/usuario-atual", response_model=UsuarioResponse)
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

# ==================== ENDPOINTS UTILITÁRIOS ====================

@app.get("/health")
async def health_check():
    """Endpoint para verificar saúde da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "app": "VendPerto ERP"
    }

@app.get("/")
async def root():
    """Redireciona para a documentação da API"""
    return RedirectResponse(url="/docs")

# ==================== EVENTOS DE STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Eventos executados no startup da aplicação"""
    logger.info("🚀 Iniciando VendPerto ERP - APIs de Cadastro e Login")
    
    # Criar tabelas no banco
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos executados no shutdown da aplicação"""
    logger.info("🛑 Finalizando VendPerto ERP")

if __name__ == "__main__":
    import uvicorn
    logger.info("🔥 Iniciando servidor na porta 8001...")
    uvicorn.run(
        "main_standalone:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 