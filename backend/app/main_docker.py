import sys
import os
sys.path.append('/app/app')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
from datetime import datetime

# Imports absolutos
from core.config import configuracoes
from core.database import engine, Base
from api.v1 import auth_fixed as auth

# Configurar logging
logging.basicConfig(
    level=getattr(logging, configuracoes.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title=configuracoes.app_name,
    description="Sistema ERP moderno e escalável para pequenas e médias empresas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logs das requisições
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    return response

# Incluir routers
app.include_router(auth.router, prefix="/api/v1")

# Endpoint de saúde
@app.get("/health")
async def health_check():
    """Endpoint para verificar saúde da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "app": configuracoes.app_name
    }

# Redirecionar root para documentação
@app.get("/")
async def root():
    """Redireciona para a documentação da API"""
    return RedirectResponse(url="/docs")

# Criar tabelas no banco (apenas para desenvolvimento)
@app.on_event("startup")
async def startup_event():
    """Eventos executados no startup da aplicação"""
    logger.info(f"Iniciando {configuracoes.app_name}")
    
    # Criar tabelas (em produção usar Alembic)
    if configuracoes.app_env == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos executados no shutdown da aplicação"""
    logger.info(f"Finalizando {configuracoes.app_name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=True
    ) 