#!/usr/bin/env python3
"""
VendPerto ERP - Sistema Completo de APIs
Módulos: Usuários, Produtos, Vendas, Categorias, Perfis, Fornecedores
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib
import json
import base64

# Configurar segurança
security = HTTPBearer()

# Criar aplicação FastAPI
app = FastAPI(
    title="VendPerto ERP - Sistema Completo",
    description="APIs de Usuários, Produtos, Vendas, Categorias, Perfis e Fornecedores",
    version="2.0.0"
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
categorias_db = []
fornecedores_db = []
configuracoes_db = []
logs_db = []

# ==================== SCHEMAS USUÁRIOS ====================
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str = "cliente"

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

# ==================== SCHEMAS CATEGORIAS ====================
class CategoriaCreate(BaseModel):
    nome: str
    descricao: str
    categoria_pai_id: Optional[int] = None
    ativo: bool = True

class CategoriaResponse(BaseModel):
    id: int
    nome: str
    descricao: str
    categoria_pai_id: Optional[int]
    categoria_pai_nome: Optional[str]
    subcategorias: List[dict]
    total_produtos: int
    ativo: bool
    data_criacao: datetime

# ==================== SCHEMAS PRODUTOS ====================
class ProdutoCreate(BaseModel):
    nome: str
    descricao: str
    preco: float
    categoria_id: int
    fornecedor_id: Optional[int] = None
    estoque: int = 0
    estoque_minimo: int = 5

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float
    categoria_id: int
    categoria_nome: str
    fornecedor_id: Optional[int]
    fornecedor_nome: Optional[str]
    estoque: int
    estoque_minimo: int
    ativo: bool
    data_criacao: datetime

# ==================== SCHEMAS FORNECEDORES ====================
class FornecedorCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    cnpj: str
    endereco: str
    cidade: str
    estado: str
    cep: str

class FornecedorResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    cnpj: str
    endereco: str
    cidade: str
    estado: str
    cep: str
    total_produtos: int
    ativo: bool
    data_criacao: datetime

# ==================== SCHEMAS VENDAS ====================
class ItemVenda(BaseModel):
    produto_id: int
    quantidade: int

class VendaCreate(BaseModel):
    cliente_email: str
    itens: List[ItemVenda]
    observacoes: Optional[str] = ""

class VendaResponse(BaseModel):
    id: int
    cliente_email: str
    itens: List[dict]
    total: float
    observacoes: str
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
    token_data = {"email": email, "timestamp": datetime.now().isoformat()}
    token_json = json.dumps(token_data)
    return base64.b64encode(token_json.encode()).decode()

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica se o token é válido"""
    try:
        token_data = base64.b64decode(credentials.credentials).decode()
        data = json.loads(token_data)
        return data["email"]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def buscar_usuario_por_email(email: str):
    """Busca usuário por email"""
    for usuario in usuarios_db:
        if usuario["email"] == email:
            return usuario
    return None

def buscar_categoria_por_id(categoria_id: int):
    """Busca categoria por ID"""
    for categoria in categorias_db:
        if categoria["id"] == categoria_id:
            return categoria
    return None

def buscar_fornecedor_por_id(fornecedor_id: int):
    """Busca fornecedor por ID"""
    for fornecedor in fornecedores_db:
        if fornecedor["id"] == fornecedor_id:
            return fornecedor
    return None

def buscar_produto_por_id(produto_id: int):
    """Busca produto por ID"""
    for produto in produtos_db:
        if produto["id"] == produto_id:
            return produto
    return None

def obter_subcategorias(categoria_id: int):
    """Obtém subcategorias de uma categoria"""
    return [cat for cat in categorias_db if cat["categoria_pai_id"] == categoria_id]

def contar_produtos_categoria(categoria_id: int):
    """Conta produtos de uma categoria"""
    return len([prod for prod in produtos_db if prod["categoria_id"] == categoria_id])

def registrar_log(acao: str, usuario_email: str, detalhes: dict):
    """Registra log de auditoria"""
    log = {
        "id": len(logs_db) + 1,
        "acao": acao,
        "usuario_email": usuario_email,
        "detalhes": detalhes,
        "timestamp": datetime.now()
    }
    logs_db.append(log)

# ==================== ENDPOINTS USUÁRIOS ====================

@app.get("/health")
async def health_check():
    """Endpoint para verificar saúde da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "2.0.0",
        "app": "VendPerto ERP",
        "modulos": {
            "usuarios": len(usuarios_db),
            "produtos": len(produtos_db),
            "categorias": len(categorias_db),
            "fornecedores": len(fornecedores_db),
            "vendas": len(vendas_db),
            "logs": len(logs_db)
        }
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
    
    # Registrar log
    registrar_log("usuario_criado", dados_usuario.email, {"usuario_id": novo_usuario["id"]})
    
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
    
    # Registrar log
    registrar_log("login_realizado", dados_login.email, {"usuario_id": usuario["id"]})
    
    # Criar token de acesso
    access_token = criar_token(usuario["email"])
    
    return Token(access_token=access_token, token_type="bearer")

@app.get("/api/v1/auth/usuarios")
async def listar_usuarios():
    """Lista todos os usuários cadastrados"""
    usuarios_sem_senha = []
    for usuario in usuarios_db:
        usuario_limpo = usuario.copy()
        del usuario_limpo["senha_hash"]
        usuarios_sem_senha.append(usuario_limpo)
    
    return {
        "total": len(usuarios_sem_senha),
        "usuarios": usuarios_sem_senha
    }

# ==================== ENDPOINTS CATEGORIAS ====================

@app.post("/api/v1/categorias/cadastrar", response_model=RespostaPadrao)
async def cadastrar_categoria(dados_categoria: CategoriaCreate, usuario_email: str = Depends(verificar_token)):
    """Cadastra uma nova categoria"""
    
    # Verificar se categoria pai existe (se informada)
    if dados_categoria.categoria_pai_id:
        categoria_pai = buscar_categoria_por_id(dados_categoria.categoria_pai_id)
        if not categoria_pai:
            raise HTTPException(
                status_code=404,
                detail="Categoria pai não encontrada"
            )
    
    # Criar categoria
    nova_categoria = {
        "id": len(categorias_db) + 1,
        "nome": dados_categoria.nome,
        "descricao": dados_categoria.descricao,
        "categoria_pai_id": dados_categoria.categoria_pai_id,
        "ativo": dados_categoria.ativo,
        "data_criacao": datetime.now()
    }
    
    categorias_db.append(nova_categoria)
    
    # Registrar log
    registrar_log("categoria_criada", usuario_email, {"categoria_id": nova_categoria["id"]})
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Categoria cadastrada com sucesso",
        dados={"categoria_id": nova_categoria["id"], "nome": nova_categoria["nome"]},
        timestamp=datetime.now()
    )

@app.get("/api/v1/categorias/listar")
async def listar_categorias():
    """Lista todas as categorias"""
    categorias_completas = []
    
    for categoria in categorias_db:
        if categoria["ativo"]:
            categoria_pai_nome = None
            if categoria["categoria_pai_id"]:
                categoria_pai = buscar_categoria_por_id(categoria["categoria_pai_id"])
                categoria_pai_nome = categoria_pai["nome"] if categoria_pai else None
            
            categoria_completa = {
                "id": categoria["id"],
                "nome": categoria["nome"],
                "descricao": categoria["descricao"],
                "categoria_pai_id": categoria["categoria_pai_id"],
                "categoria_pai_nome": categoria_pai_nome,
                "subcategorias": obter_subcategorias(categoria["id"]),
                "total_produtos": contar_produtos_categoria(categoria["id"]),
                "ativo": categoria["ativo"],
                "data_criacao": categoria["data_criacao"]
            }
            categorias_completas.append(categoria_completa)
    
    return {
        "total": len(categorias_completas),
        "categorias": categorias_completas
    }

@app.get("/api/v1/categorias/{categoria_id}")
async def obter_categoria(categoria_id: int):
    """Obtém detalhes de uma categoria específica"""
    categoria = buscar_categoria_por_id(categoria_id)
    
    if not categoria:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada"
        )
    
    # Obter categoria pai
    categoria_pai_nome = None
    if categoria["categoria_pai_id"]:
        categoria_pai = buscar_categoria_por_id(categoria["categoria_pai_id"])
        categoria_pai_nome = categoria_pai["nome"] if categoria_pai else None
    
    return {
        **categoria,
        "categoria_pai_nome": categoria_pai_nome,
        "subcategorias": obter_subcategorias(categoria_id),
        "total_produtos": contar_produtos_categoria(categoria_id)
    }

@app.put("/api/v1/categorias/{categoria_id}")
async def atualizar_categoria(categoria_id: int, dados_categoria: CategoriaCreate, usuario_email: str = Depends(verificar_token)):
    """Atualiza uma categoria"""
    categoria = buscar_categoria_por_id(categoria_id)
    
    if not categoria:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada"
        )
    
    # Atualizar dados
    categoria.update({
        "nome": dados_categoria.nome,
        "descricao": dados_categoria.descricao,
        "categoria_pai_id": dados_categoria.categoria_pai_id,
        "ativo": dados_categoria.ativo
    })
    
    # Registrar log
    registrar_log("categoria_atualizada", usuario_email, {"categoria_id": categoria_id})
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Categoria atualizada com sucesso",
        dados={"categoria_id": categoria_id},
        timestamp=datetime.now()
    )

# ==================== ENDPOINTS FORNECEDORES ====================

@app.post("/api/v1/fornecedores/cadastrar", response_model=RespostaPadrao)
async def cadastrar_fornecedor(dados_fornecedor: FornecedorCreate, usuario_email: str = Depends(verificar_token)):
    """Cadastra um novo fornecedor"""
    
    # Verificar se CNPJ já existe
    for fornecedor in fornecedores_db:
        if fornecedor["cnpj"] == dados_fornecedor.cnpj:
            raise HTTPException(
                status_code=400,
                detail="CNPJ já cadastrado no sistema"
            )
    
    # Criar fornecedor
    novo_fornecedor = {
        "id": len(fornecedores_db) + 1,
        "nome": dados_fornecedor.nome,
        "email": dados_fornecedor.email,
        "telefone": dados_fornecedor.telefone,
        "cnpj": dados_fornecedor.cnpj,
        "endereco": dados_fornecedor.endereco,
        "cidade": dados_fornecedor.cidade,
        "estado": dados_fornecedor.estado,
        "cep": dados_fornecedor.cep,
        "ativo": True,
        "data_criacao": datetime.now()
    }
    
    fornecedores_db.append(novo_fornecedor)
    
    # Registrar log
    registrar_log("fornecedor_criado", usuario_email, {"fornecedor_id": novo_fornecedor["id"]})
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Fornecedor cadastrado com sucesso",
        dados={"fornecedor_id": novo_fornecedor["id"], "nome": novo_fornecedor["nome"]},
        timestamp=datetime.now()
    )

@app.get("/api/v1/fornecedores/listar")
async def listar_fornecedores():
    """Lista todos os fornecedores"""
    fornecedores_completos = []
    
    for fornecedor in fornecedores_db:
        if fornecedor["ativo"]:
            total_produtos = len([prod for prod in produtos_db if prod.get("fornecedor_id") == fornecedor["id"]])
            
            fornecedor_completo = {
                **fornecedor,
                "total_produtos": total_produtos
            }
            fornecedores_completos.append(fornecedor_completo)
    
    return {
        "total": len(fornecedores_completos),
        "fornecedores": fornecedores_completos
    }

# ==================== ENDPOINTS PRODUTOS ATUALIZADOS ====================

@app.post("/api/v1/produtos/cadastrar", response_model=RespostaPadrao)
async def cadastrar_produto(dados_produto: ProdutoCreate, usuario_email: str = Depends(verificar_token)):
    """Cadastra um novo produto no sistema"""
    
    # Verificar se categoria existe
    categoria = buscar_categoria_por_id(dados_produto.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada"
        )
    
    # Verificar fornecedor (se informado)
    fornecedor = None
    if dados_produto.fornecedor_id:
        fornecedor = buscar_fornecedor_por_id(dados_produto.fornecedor_id)
        if not fornecedor:
            raise HTTPException(
                status_code=404,
                detail="Fornecedor não encontrado"
            )
    
    # Criar produto
    novo_produto = {
        "id": len(produtos_db) + 1,
        "nome": dados_produto.nome,
        "descricao": dados_produto.descricao,
        "preco": dados_produto.preco,
        "categoria_id": dados_produto.categoria_id,
        "fornecedor_id": dados_produto.fornecedor_id,
        "estoque": dados_produto.estoque,
        "estoque_minimo": dados_produto.estoque_minimo,
        "ativo": True,
        "data_criacao": datetime.now()
    }
    
    produtos_db.append(novo_produto)
    
    # Registrar log
    registrar_log("produto_criado", usuario_email, {"produto_id": novo_produto["id"]})
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Produto cadastrado com sucesso",
        dados={"produto_id": novo_produto["id"], "nome": novo_produto["nome"]},
        timestamp=datetime.now()
    )

@app.get("/api/v1/produtos/listar")
async def listar_produtos():
    """Lista todos os produtos disponíveis"""
    produtos_completos = []
    
    for produto in produtos_db:
        if produto["ativo"]:
            # Obter categoria
            categoria = buscar_categoria_por_id(produto["categoria_id"])
            categoria_nome = categoria["nome"] if categoria else "Sem categoria"
            
            # Obter fornecedor
            fornecedor = None
            fornecedor_nome = None
            if produto.get("fornecedor_id"):
                fornecedor = buscar_fornecedor_por_id(produto["fornecedor_id"])
                fornecedor_nome = fornecedor["nome"] if fornecedor else None
            
            produto_completo = {
                **produto,
                "categoria_nome": categoria_nome,
                "fornecedor_nome": fornecedor_nome,
                "estoque_baixo": produto["estoque"] <= produto["estoque_minimo"]
            }
            produtos_completos.append(produto_completo)
    
    return {
        "total": len(produtos_completos),
        "produtos": produtos_completos
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
    
    # Obter categoria e fornecedor
    categoria = buscar_categoria_por_id(produto["categoria_id"])
    fornecedor = buscar_fornecedor_por_id(produto.get("fornecedor_id")) if produto.get("fornecedor_id") else None
    
    return {
        **produto,
        "categoria_nome": categoria["nome"] if categoria else "Sem categoria",
        "fornecedor_nome": fornecedor["nome"] if fornecedor else None,
        "estoque_baixo": produto["estoque"] <= produto["estoque_minimo"]
    }

@app.put("/api/v1/produtos/{produto_id}/estoque")
async def atualizar_estoque(produto_id: int, nova_quantidade: int, usuario_email: str = Depends(verificar_token)):
    """Atualiza estoque de um produto"""
    produto = buscar_produto_por_id(produto_id)
    
    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )
    
    estoque_anterior = produto["estoque"]
    produto["estoque"] = nova_quantidade
    
    # Registrar log
    registrar_log("estoque_atualizado", usuario_email, {
        "produto_id": produto_id,
        "estoque_anterior": estoque_anterior,
        "estoque_novo": nova_quantidade
    })
    
    return RespostaPadrao(
        sucesso=True,
        mensagem="Estoque atualizado com sucesso",
        dados={"produto_id": produto_id, "novo_estoque": nova_quantidade},
        timestamp=datetime.now()
    )

# ==================== ENDPOINTS VENDAS ATUALIZADOS ====================

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
        "observacoes": dados_venda.observacoes,
        "data_venda": datetime.now()
    }
    
    vendas_db.append(nova_venda)
    
    # Registrar log
    registrar_log("venda_realizada", dados_venda.cliente_email, {
        "venda_id": nova_venda["id"],
        "total": total,
        "itens": len(itens_venda)
    })
    
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

# ==================== ENDPOINTS RELATÓRIOS ====================

@app.get("/api/v1/relatorios/dashboard")
async def obter_dashboard():
    """Obtém dados para dashboard principal"""
    
    # Vendas hoje
    hoje = datetime.now().date()
    vendas_hoje = [v for v in vendas_db if v["data_venda"].date() == hoje]
    total_vendas_hoje = sum(v["total"] for v in vendas_hoje)
    
    # Produtos com estoque baixo
    produtos_estoque_baixo = [
        p for p in produtos_db 
        if p["ativo"] and p["estoque"] <= p["estoque_minimo"]
    ]
    
    return {
        "resumo": {
            "total_usuarios": len(usuarios_db),
            "total_produtos": len([p for p in produtos_db if p["ativo"]]),
            "total_categorias": len([c for c in categorias_db if c["ativo"]]),
            "total_fornecedores": len([f for f in fornecedores_db if f["ativo"]]),
            "total_vendas": len(vendas_db),
            "vendas_hoje": len(vendas_hoje),
            "receita_hoje": total_vendas_hoje,
            "produtos_estoque_baixo": len(produtos_estoque_baixo)
        },
        "alertas": [
            {
                "tipo": "estoque_baixo",
                "quantidade": len(produtos_estoque_baixo),
                "produtos": [p["nome"] for p in produtos_estoque_baixo[:5]]
            }
        ]
    }

@app.get("/api/v1/relatorios/vendas")
async def relatorio_vendas(periodo: int = 30):
    """Relatório de vendas por período"""
    data_limite = datetime.now() - timedelta(days=periodo)
    vendas_periodo = [v for v in vendas_db if v["data_venda"] >= data_limite]
    
    total_vendas = len(vendas_periodo)
    receita_total = sum(v["total"] for v in vendas_periodo)
    ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
    
    return {
        "periodo_dias": periodo,
        "total_vendas": total_vendas,
        "receita_total": receita_total,
        "ticket_medio": ticket_medio,
        "vendas": vendas_periodo
    }

# ==================== ENDPOINTS LOGS ====================

@app.get("/api/v1/logs/listar")
async def listar_logs(limit: int = 100):
    """Lista logs de auditoria"""
    logs_recentes = sorted(logs_db, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    return {
        "total": len(logs_db),
        "exibindo": len(logs_recentes),
        "logs": logs_recentes
    }

# ==================== ENDPOINT PRINCIPAL ====================

@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "message": "VendPerto ERP - Sistema Completo v2.0",
        "status": "funcionando",
        "modulos": ["Usuários", "Produtos", "Categorias", "Fornecedores", "Vendas", "Relatórios"],
        "endpoints": {
            "usuarios": [
                "POST /api/v1/auth/registrar",
                "POST /api/v1/auth/login-json",
                "GET  /api/v1/auth/usuarios"
            ],
            "categorias": [
                "POST /api/v1/categorias/cadastrar",
                "GET  /api/v1/categorias/listar",
                "GET  /api/v1/categorias/{id}",
                "PUT  /api/v1/categorias/{id}"
            ],
            "fornecedores": [
                "POST /api/v1/fornecedores/cadastrar",
                "GET  /api/v1/fornecedores/listar"
            ],
            "produtos": [
                "POST /api/v1/produtos/cadastrar",
                "GET  /api/v1/produtos/listar",
                "GET  /api/v1/produtos/{id}",
                "PUT  /api/v1/produtos/{id}/estoque"
            ],
            "vendas": [
                "POST /api/v1/vendas/realizar",
                "GET  /api/v1/vendas/listar",
                "GET  /api/v1/vendas/{id}",
                "GET  /api/v1/vendas/cliente/{email}"
            ],
            "relatorios": [
                "GET  /api/v1/relatorios/dashboard",
                "GET  /api/v1/relatorios/vendas"
            ],
            "sistema": [
                "GET  /health",
                "GET  /api/v1/logs/listar"
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando VendPerto ERP - Sistema Completo v2.0")
    print("📖 Documentação: http://localhost:8001/docs")
    print("🔗 Endpoints: http://localhost:8001/")
    print("👥 Usuários | 📦 Produtos | 🗂️ Categorias | 🏭 Fornecedores | 💰 Vendas | 📊 Relatórios")
    
    uvicorn.run(
        "testar_api_direto:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    ) 