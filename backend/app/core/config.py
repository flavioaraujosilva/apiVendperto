from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Configurações da Aplicação
    app_name: str = "VendPerto ERP"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "sua_chave_super_secreta_aqui_mude_em_producao"
    
    # Banco de Dados - usar banco remoto configurado
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://vendperto:nxq8n8m0qh7lnrqz@5.161.218.248:5432/vendperto"
    )
    
    # JWT
    jwt_secret: str = "jwt_secret_key_mude_em_producao"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://ambientedeteste.dev"
    ]
    
    # Logs
    log_level: str = "DEBUG"
    log_file: str = "logs/vendperto.log"
    
    class Config:
        env_file = ".env"

configuracoes = Settings() 