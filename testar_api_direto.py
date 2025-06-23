#!/usr/bin/env python3
"""
Script para testar as APIs de cadastro e login do VendPerto ERP
sem dependências complexas
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import hashlib
import json

# Criar aplicação FastAPI
app = FastAPI(
    title="VendPerto ERP - APIs Completas",
    description="APIs de Usuários, Produtos e Vendas - Sistema Completo",
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

# "Banco de dados" em memória para teste
usuarios_db = []
produtos_db = []
vendas_db = []

# ==================== SCHEMAS USUÁRIOS ====================
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str = "operador"

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

# ==================== SCHEMAS PRODUTOS ====================
class ProdutoCreate(BaseModel):
    nome: str
    descricao: str
    preco: float
    categoria: str
    estoque: int = 0

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float
    categoria: str
    estoque: int
    ativo: bool
    data_criacao: datetime

# ==================== SCHEMAS VENDAS ====================
class ItemVenda(BaseModel):
    produto_id: int
    quantidade: int

class VendaCreate(BaseModel):
    cliente_email: str
    itens: List[ItemVenda]

class VendaResponse(BaseModel):
    id: int
    cliente_email: str
    itens: List[dict]
    total: float
    data_venda: datetime

# ==================== SCHEMAS GERAIS ====================
class Token(BaseModel):
    access_token: str
    token_type: str

class RespostaPadrao(BaseModel):
    sucesso: bool
    mensagem: str
    dados: Optional[dict] = None
    timestamp: datetime

# ==================== FUNÇÕES AUXILIARES ====================
def hash_senha(senha: str) -> str:
    """Cria hash simples da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Verifica se a senha está correta"""
    return hash_senha(senha) == hash_armazenado

def criar_token(email: str) -> str:
    """Cria token simples (apenas para teste)"""
    import base64
    token_data = {"email": email, "timestamp": datetime.now().isoformat()}
    token_json = json.dumps(token_data)
    return base64.b64encode(token_json.encode()).decode()

def buscar_usuario_por_email(email: str):
    """Busca usuário por email"""
    for usuario in usuarios_db:
        if usuario["email"] == email:
            return usuario
    return None

def buscar_produto_por_id(produto_id: int):
    """Busca produto por ID"""
    for produto in produtos_db:
        if produto["id"] == produto_id:
            return produto
    return None

def calcular_total_venda(itens: List[ItemVenda]) -> float:
    """Calcula o total da venda"""
    total = 0.0
    for item in itens:
        produto = buscar_produto_por_id(item.produto_id)
        if produto:
            total += produto["preco"] * item.quantidade
    return total

# ==================== ENDPOINTS USUÁRIOS ====================

@app.get("/health")
async def health_check():
    """Endpoint para verificar saúde da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "app": "VendPerto ERP",
        "usuarios_cadastrados": len(usuarios_db),
        "produtos_cadastrados": len(produtos_db),
        "vendas_realizadas": len(vendas_db)
    }

@app.post("/api/v1/auth/registrar", response_model=RespostaPadrao)
async def registrar_usuario(dados_usuario: UsuarioCreate):
    """Registra um novo usuário no sistema"""
    
    # Verificar se usuário já existe
    if buscar_usuario_por_email(dados_usuario.email):
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado no sistema"
        )
    
    # Criar usuário
    novo_usuario = {
        "id": len(usuarios_db) + 1,
        "nome": dados_usuario.nome,
        "email": dados_usuario.email,
        "senha_hash": hash_senha(dados_usuario.senha),
        "perfil": dados_usuario.perfil,
        "ativo": True,
        "data_criacao": datetime.now()
    }
    
    usuarios_db.append(novo_usuario)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Usuário registrado com sucesso",
        dados={"usuario_id": novo_usuario["id"], "email": novo_usuario["email"]},
        timestamp=datetime.now()
    )

@app.post("/api/v1/auth/login-json", response_model=Token)
async def fazer_login_json(dados_login: UsuarioLogin):
    """Realiza login do usuário"""
    
    usuario = buscar_usuario_por_email(dados_login.email)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not verificar_senha(dados_login.senha, usuario["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not usuario["ativo"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    # Criar token de acesso
    access_token = criar_token(usuario["email"])
    
    return Token(access_token=access_token, token_type="bearer")

@app.get("/api/v1/auth/usuarios")
async def listar_usuarios():
    """Lista todos os usuários cadastrados (para teste)"""
    usuarios_sem_senha = []
    for usuario in usuarios_db:
        usuario_limpo = usuario.copy()
        del usuario_limpo["senha_hash"]
        usuarios_sem_senha.append(usuario_limpo)
    
    return {
        "total": len(usuarios_sem_senha),
        "usuarios": usuarios_sem_senha
    }

# ==================== ENDPOINTS PRODUTOS ====================

@app.post("/api/v1/produtos/cadastrar", response_model=RespostaPadrao)
async def cadastrar_produto(dados_produto: ProdutoCreate):
    """Cadastra um novo produto no sistema"""
    
    # Criar produto
    novo_produto = {
        "id": len(produtos_db) + 1,
        "nome": dados_produto.nome,
        "descricao": dados_produto.descricao,
        "preco": dados_produto.preco,
        "categoria": dados_produto.categoria,
        "estoque": dados_produto.estoque,
        "ativo": True,
        "data_criacao": datetime.now()
    }
    
    produtos_db.append(novo_produto)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Produto cadastrado com sucesso",
        dados={"produto_id": novo_produto["id"], "nome": novo_produto["nome"]},
        timestamp=datetime.now()
    )

@app.get("/api/v1/produtos/listar")
async def listar_produtos():
    """Lista todos os produtos disponíveis"""
    produtos_ativos = [produto for produto in produtos_db if produto["ativo"]]
    
    return {
        "total": len(produtos_ativos),
        "produtos": produtos_ativos
    }

@app.get("/api/v1/produtos/{produto_id}")
async def obter_produto(produto_id: int):
    """Obtém detalhes de um produto específico"""
    produto = buscar_produto_por_id(produto_id)
    
    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )
    
    return produto

@app.put("/api/v1/produtos/{produto_id}/estoque")
async def atualizar_estoque(produto_id: int, nova_quantidade: int):
    """Atualiza estoque de um produto"""
    produto = buscar_produto_por_id(produto_id)
    
    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )
    
    produto["estoque"] = nova_quantidade
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Estoque atualizado com sucesso",
        dados={"produto_id": produto_id, "novo_estoque": nova_quantidade},
        timestamp=datetime.now()
    )

# ==================== ENDPOINTS VENDAS ====================

@app.post("/api/v1/vendas/realizar", response_model=RespostaPadrao)
async def realizar_venda(dados_venda: VendaCreate):
    """Realiza uma nova venda"""
    
    # Verificar se cliente existe
    cliente = buscar_usuario_por_email(dados_venda.cliente_email)
    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )
    
    # Validar produtos e estoque
    itens_venda = []
    total = 0.0
    
    for item in dados_venda.itens:
        produto = buscar_produto_por_id(item.produto_id)
        
        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto {item.produto_id} não encontrado"
            )
        
        if produto["estoque"] < item.quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para o produto {produto['nome']}"
            )
        
        # Calcular subtotal
        subtotal = produto["preco"] * item.quantidade
        total += subtotal
        
        # Preparar item da venda
        itens_venda.append({
            "produto_id": produto["id"],
            "produto_nome": produto["nome"],
            "preco_unitario": produto["preco"],
            "quantidade": item.quantidade,
            "subtotal": subtotal
        })
        
        # Reduzir estoque
        produto["estoque"] -= item.quantidade
    
    # Criar venda
    nova_venda = {
        "id": len(vendas_db) + 1,
        "cliente_email": dados_venda.cliente_email,
        "cliente_nome": cliente["nome"],
        "itens": itens_venda,
        "total": total,
        "data_venda": datetime.now()
    }
    
    vendas_db.append(nova_venda)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Venda realizada com sucesso",
        dados={
            "venda_id": nova_venda["id"],
            "total": total,
            "itens": len(itens_venda)
        },
        timestamp=datetime.now()
    )

@app.get("/api/v1/vendas/listar")
async def listar_vendas():
    """Lista todas as vendas realizadas"""
    return {
        "total": len(vendas_db),
        "vendas": vendas_db
    }

@app.get("/api/v1/vendas/{venda_id}")
async def obter_venda(venda_id: int):
    """Obtém detalhes de uma venda específica"""
    for venda in vendas_db:
        if venda["id"] == venda_id:
            return venda
    
    raise HTTPException(
        status_code=404,
        detail="Venda não encontrada"
    )

@app.get("/api/v1/vendas/cliente/{cliente_email}")
async def listar_vendas_cliente(cliente_email: str):
    """Lista vendas de um cliente específico"""
    vendas_cliente = [venda for venda in vendas_db if venda["cliente_email"] == cliente_email]
    
    return {
        "total": len(vendas_cliente),
        "vendas": vendas_cliente
    }

# ==================== ENDPOINT PRINCIPAL ====================

@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "message": "VendPerto ERP - Sistema Completo",
        "status": "funcionando",
        "modulos": ["Usuários", "Produtos", "Vendas"],
        "endpoints": {
            "usuarios": [
                "/api/v1/auth/registrar",
                "/api/v1/auth/login-json",
                "/api/v1/auth/usuarios"
            ],
            "produtos": [
                "/api/v1/produtos/cadastrar",
                "/api/v1/produtos/listar",
                "/api/v1/produtos/{id}",
                "/api/v1/produtos/{id}/estoque"
            ],
            "vendas": [
                "/api/v1/vendas/realizar",
                "/api/v1/vendas/listar",
                "/api/v1/vendas/{id}",
                "/api/v1/vendas/cliente/{email}"
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando VendPerto ERP - Sistema Completo")
    print("📖 Documentação: http://localhost:8001/docs")
    print("🔗 Endpoints: http://localhost:8001/")
    print("👥 Usuários | 📦 Produtos | 💰 Vendas")
    
    uvicorn.run(
        "testar_api_direto:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    ) 