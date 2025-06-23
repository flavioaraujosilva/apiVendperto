from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="VendPerto ERP - Teste",
    description="Teste simples da API",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Endpoint para verificar saúde da aplicação"""
    logger.info("Health check chamado")
    return {
        "status": "healthy",
        "app": "VendPerto ERP",
        "service": "vendperto-api"
    }

@app.get("/")
async def root():
    """Rota raiz"""
    return {"message": "VendPerto ERP API funcionando!"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🔥 Iniciando servidor simples na porta 8001...")
    uvicorn.run(
        "main_simples:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    ) 