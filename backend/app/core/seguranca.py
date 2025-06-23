from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import configuracoes

# Configuração para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criarHashSenha(senha: str) -> str:
    """Cria hash da senha"""
    return pwd_context.hash(senha)

def verificarSenha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(senha_plana, senha_hash)

def criarTokenAcesso(dados: dict, expira_delta: Optional[timedelta] = None):
    """Cria token JWT de acesso"""
    para_codificar = dados.copy()
    
    if expira_delta:
        expirar = datetime.utcnow() + expira_delta
    else:
        expirar = datetime.utcnow() + timedelta(minutes=configuracoes.jwt_expire_minutes)
    
    para_codificar.update({"exp": expirar})
    token_codificado = jwt.encode(
        para_codificar, 
        configuracoes.jwt_secret, 
        algorithm=configuracoes.jwt_algorithm
    )
    return token_codificado

def verificarToken(token: str) -> Optional[str]:
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(
            token, 
            configuracoes.jwt_secret, 
            algorithms=[configuracoes.jwt_algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None 