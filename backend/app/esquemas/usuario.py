from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schema base do usuário
class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str
    cpf: Optional[str] = None
    perfil: str = "operador"

# Schema para criação de usuário
class UsuarioCreate(UsuarioBase):
    senha: str

# Schema para login
class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

# Schema de resposta do usuário (sem senha)
class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    data_criacao: datetime
    data_atualizacao: datetime
    
    class Config:
        from_attributes = True

# Schema para token JWT
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema para resposta padrão da API
class RespostaPadrao(BaseModel):
    sucesso: bool
    mensagem: str
    dados: Optional[dict] = None
    timestamp: datetime 