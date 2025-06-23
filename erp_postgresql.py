#!/usr/bin/env python3
"""
🚀 VendPerto ERP - Sistema Completo com PostgreSQL
==================================================

Sistema ERP completo usando PostgreSQL real:
- Usuários, Produtos, Categorias, Fornecedores, Vendas
- Dados persistentes no PostgreSQL
- Relacionamentos SQLAlchemy
- Logs de auditoria
- APIs RESTful completas

URL: postgresql://vendperto:nxq8n8m0qh7lnrqz@5.161.218.248:5432/vendperto
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib
import json
import base64
from decimal import Decimal
import uvicorn

# Imports do backend
from backend.app.core.database import SessionLocal, engine, obter_db
from backend.app.core.config import configuracoes
from backend.app.modelos import Usuario, Categoria, Fornecedor, Produto, Venda, ItemVenda, Log, Base
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func

# Criar todas as tabelas
print("🔧 Criando tabelas no PostgreSQL...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")

# Configurar segurança
security = HTTPBearer()

# ==================== SCHEMAS ====================
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cpf: Optional[str] = None
    perfil: str = "operador"

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class CategoriaCreate(BaseModel):
    nome: str
    descricao: str
    categoria_pai_id: Optional[int] = None

class FornecedorCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    cnpj: str
    endereco: str
    cidade: str
    estado: str
    cep: str

class ProdutoCreate(BaseModel):
    nome: str
    descricao: str
    preco: float
    categoria_id: int
    fornecedor_id: Optional[int] = None
    estoque: int = 0
    estoque_minimo: int = 5

class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int

class VendaCreate(BaseModel):
    cliente_email: str
    itens: List[ItemVendaCreate]
    observacoes: Optional[str] = ""

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
    """Cria hash seguro da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Verifica se a senha está correta"""
    return hash_senha(senha) == hash_armazenado

def criar_token(email: str) -> str:
    """Cria token JWT simples"""
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

def registrar_log(db: Session, acao: str, usuario_email: str, detalhes: dict, request: Request = None):
    """Registra log de auditoria"""
    ip_origem = None
    user_agent = None
    
    if request:
        ip_origem = request.client.host
        user_agent = request.headers.get("user-agent")
    
    log = Log(
        acao=acao,
        usuario_email=usuario_email,
        detalhes=detalhes,
        ip_origem=ip_origem,
        user_agent=user_agent
    )
    db.add(log)
    db.commit()

# ==================== APLICAÇÃO ====================
app = FastAPI(
    title="VendPerto ERP - PostgreSQL",
    description="Sistema ERP completo com PostgreSQL",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ENDPOINTS - SISTEMA ====================
@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    try:
        db = SessionLocal()
        # Teste simples de conexão
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "ok",
            "database": "postgresql_connected",
            "timestamp": datetime.now(),
            "version": "3.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "postgresql_error",
            "error": str(e),
            "timestamp": datetime.now()
        }

@app.get("/")
async def root():
    """Endpoint raiz com informações do sistema"""
    return {
        "sistema": "VendPerto ERP - PostgreSQL",
        "versao": "3.0.0",
        "banco": "PostgreSQL",
        "documentacao": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

# ==================== ENDPOINTS - AUTENTICAÇÃO ====================
@app.post("/api/v1/auth/registrar", response_model=RespostaPadrao)
async def registrar_usuario(dados_usuario: UsuarioCreate, request: Request, db: Session = Depends(obter_db)):
    """Registrar novo usuário"""
    
    # Verificar se já existe
    usuario_existente = db.query(Usuario).filter(Usuario.email == dados_usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Criar usuário
    usuario = Usuario(
        nome=dados_usuario.nome,
        email=dados_usuario.email,
        senha_hash=hash_senha(dados_usuario.senha),
        cpf=dados_usuario.cpf,
        perfil=dados_usuario.perfil
    )
    
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    # Log
    registrar_log(db, "usuario_registrado", dados_usuario.email, {
        "nome": dados_usuario.nome,
        "perfil": dados_usuario.perfil
    }, request)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem=f"Usuário {dados_usuario.nome} registrado com sucesso",
        dados={"id": usuario.id, "email": usuario.email},
        timestamp=datetime.now()
    )

@app.post("/api/v1/auth/login-json", response_model=Token)
async def fazer_login_json(dados_login: UsuarioLogin, request: Request, db: Session = Depends(obter_db)):
    """Login de usuário"""
    
    usuario = db.query(Usuario).filter(Usuario.email == dados_login.email).first()
    
    if not usuario or not verificar_senha(dados_login.senha, usuario.senha_hash):
        registrar_log(db, "login_falhou", dados_login.email, {"motivo": "credenciais_invalidas"}, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário desativado")
    
    token = criar_token(usuario.email)
    
    # Log
    registrar_log(db, "login_realizado", usuario.email, {"nome": usuario.nome}, request)
    
    return Token(access_token=token, token_type="bearer")

@app.get("/api/v1/auth/usuarios")
async def listar_usuarios(usuario_email: str = Depends(verificar_token), db: Session = Depends(obter_db)):
    """Listar todos os usuários"""
    
    usuarios = db.query(Usuario).filter(Usuario.ativo == True).all()
    
    return {
        "usuarios": [
            {
                "id": u.id,
                "nome": u.nome,
                "email": u.email,
                "perfil": u.perfil,
                "cpf": u.cpf,
                "data_criacao": u.data_criacao
            } for u in usuarios
        ],
        "total": len(usuarios)
    }

# ==================== ENDPOINTS - CATEGORIAS ====================
@app.post("/api/v1/categorias/cadastrar", response_model=RespostaPadrao)
async def cadastrar_categoria(dados_categoria: CategoriaCreate, request: Request, usuario_email: str = Depends(verificar_token), db: Session = Depends(obter_db)):
    """Cadastrar nova categoria"""
    
    # Verificar se categoria pai existe (se informada)
    if dados_categoria.categoria_pai_id:
        categoria_pai = db.query(Categoria).filter(Categoria.id == dados_categoria.categoria_pai_id).first()
        if not categoria_pai:
            raise HTTPException(status_code=404, detail="Categoria pai não encontrada")
    
    categoria = Categoria(
        nome=dados_categoria.nome,
        descricao=dados_categoria.descricao,
        categoria_pai_id=dados_categoria.categoria_pai_id
    )
    
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    
    # Log
    registrar_log(db, "categoria_cadastrada", usuario_email, {
        "nome": categoria.nome,
        "id": categoria.id
    }, request)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem=f"Categoria {categoria.nome} cadastrada com sucesso",
        dados={"id": categoria.id},
        timestamp=datetime.now()
    )

@app.get("/api/v1/categorias/listar")
async def listar_categorias(db: Session = Depends(obter_db)):
    """Listar todas as categorias"""
    
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()
    
    resultado = []
    for cat in categorias:
        # Contar produtos
        total_produtos = db.query(Produto).filter(
            Produto.categoria_id == cat.id,
            Produto.ativo == True
        ).count()
        
        # Buscar subcategorias
        subcategorias = db.query(Categoria).filter(
            Categoria.categoria_pai_id == cat.id,
            Categoria.ativo == True
        ).all()
        
        resultado.append({
            "id": cat.id,
            "nome": cat.nome,
            "descricao": cat.descricao,
            "categoria_pai_id": cat.categoria_pai_id,
            "categoria_pai_nome": cat.categoria_pai.nome if cat.categoria_pai else None,
            "total_produtos": total_produtos,
            "subcategorias": [{"id": sub.id, "nome": sub.nome} for sub in subcategorias],
            "data_criacao": cat.data_criacao
        })
    
    return {
        "categorias": resultado,
        "total": len(resultado)
    }

# ==================== ENDPOINTS - FORNECEDORES ====================
@app.post("/api/v1/fornecedores/cadastrar", response_model=RespostaPadrao)
async def cadastrar_fornecedor(dados_fornecedor: FornecedorCreate, request: Request, usuario_email: str = Depends(verificar_token), db: Session = Depends(obter_db)):
    """Cadastrar novo fornecedor"""
    
    # Verificar CNPJ único
    fornecedor_existente = db.query(Fornecedor).filter(Fornecedor.cnpj == dados_fornecedor.cnpj).first()
    if fornecedor_existente:
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    
    fornecedor = Fornecedor(
        nome=dados_fornecedor.nome,
        email=dados_fornecedor.email,
        telefone=dados_fornecedor.telefone,
        cnpj=dados_fornecedor.cnpj,
        endereco=dados_fornecedor.endereco,
        cidade=dados_fornecedor.cidade,
        estado=dados_fornecedor.estado,
        cep=dados_fornecedor.cep
    )
    
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    
    # Log
    registrar_log(db, "fornecedor_cadastrado", usuario_email, {
        "nome": fornecedor.nome,
        "cnpj": fornecedor.cnpj,
        "id": fornecedor.id
    }, request)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem=f"Fornecedor {fornecedor.nome} cadastrado com sucesso",
        dados={"id": fornecedor.id},
        timestamp=datetime.now()
    )

@app.get("/api/v1/fornecedores/listar")
async def listar_fornecedores(db: Session = Depends(obter_db)):
    """Listar todos os fornecedores"""
    
    fornecedores = db.query(Fornecedor).filter(Fornecedor.ativo == True).all()
    
    resultado = []
    for forn in fornecedores:
        total_produtos = db.query(Produto).filter(
            Produto.fornecedor_id == forn.id,
            Produto.ativo == True
        ).count()
        
        resultado.append({
            "id": forn.id,
            "nome": forn.nome,
            "email": forn.email,
            "telefone": forn.telefone,
            "cnpj": forn.cnpj,
            "endereco": forn.endereco,
            "cidade": forn.cidade,
            "estado": forn.estado,
            "cep": forn.cep,
            "total_produtos": total_produtos,
            "data_criacao": forn.data_criacao
        })
    
    return {
        "fornecedores": resultado,
        "total": len(resultado)
    }

# ==================== ENDPOINTS - PRODUTOS ====================
@app.post("/api/v1/produtos/cadastrar", response_model=RespostaPadrao)
async def cadastrar_produto(dados_produto: ProdutoCreate, request: Request, usuario_email: str = Depends(verificar_token), db: Session = Depends(obter_db)):
    """Cadastrar novo produto"""
    
    # Verificar se categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == dados_produto.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Verificar se fornecedor existe (se informado)
    if dados_produto.fornecedor_id:
        fornecedor = db.query(Fornecedor).filter(Fornecedor.id == dados_produto.fornecedor_id).first()
        if not fornecedor:
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    produto = Produto(
        nome=dados_produto.nome,
        descricao=dados_produto.descricao,
        preco=Decimal(str(dados_produto.preco)),
        categoria_id=dados_produto.categoria_id,
        fornecedor_id=dados_produto.fornecedor_id,
        estoque=dados_produto.estoque,
        estoque_minimo=dados_produto.estoque_minimo
    )
    
    db.add(produto)
    db.commit()
    db.refresh(produto)
    
    # Log
    registrar_log(db, "produto_cadastrado", usuario_email, {
        "nome": produto.nome,
        "preco": float(produto.preco),
        "estoque": produto.estoque,
        "id": produto.id
    }, request)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem=f"Produto {produto.nome} cadastrado com sucesso",
        dados={"id": produto.id},
        timestamp=datetime.now()
    )

@app.get("/api/v1/produtos/listar")
async def listar_produtos(categoria_id: Optional[int] = None, fornecedor_id: Optional[int] = None, db: Session = Depends(obter_db)):
    """Listar produtos com filtros opcionais"""
    
    query = db.query(Produto).filter(Produto.ativo == True)
    
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    
    if fornecedor_id:
        query = query.filter(Produto.fornecedor_id == fornecedor_id)
    
    produtos = query.all()
    
    resultado = []
    for prod in produtos:
        resultado.append({
            "id": prod.id,
            "nome": prod.nome,
            "descricao": prod.descricao,
            "preco": float(prod.preco),
            "categoria_id": prod.categoria_id,
            "categoria_nome": prod.categoria.nome,
            "fornecedor_id": prod.fornecedor_id,
            "fornecedor_nome": prod.fornecedor.nome if prod.fornecedor else None,
            "estoque": prod.estoque,
            "estoque_minimo": prod.estoque_minimo,
            "data_criacao": prod.data_criacao
        })
    
    return {
        "produtos": resultado,
        "total": len(resultado)
    }

@app.get("/api/v1/produtos/{produto_id}")
async def obter_produto(produto_id: int, db: Session = Depends(obter_db)):
    """Obter detalhes de um produto"""
    
    produto = db.query(Produto).filter(Produto.id == produto_id, Produto.ativo == True).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return {
        "id": produto.id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": float(produto.preco),
        "categoria_id": produto.categoria_id,
        "categoria_nome": produto.categoria.nome,
        "fornecedor_id": produto.fornecedor_id,
        "fornecedor_nome": produto.fornecedor.nome if produto.fornecedor else None,
        "estoque": produto.estoque,
        "estoque_minimo": produto.estoque_minimo,
        "data_criacao": produto.data_criacao
    }

# ==================== ENDPOINTS - VENDAS ====================
@app.post("/api/v1/vendas/realizar", response_model=RespostaPadrao)
async def realizar_venda(dados_venda: VendaCreate, request: Request, db: Session = Depends(obter_db)):
    """Realizar nova venda"""
    
    total_venda = Decimal('0')
    itens_processados = []
    
    # Processar cada item
    for item in dados_venda.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id, Produto.ativo == True).first()
        
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")
        
        if produto.estoque < item.quantidade:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para {produto.nome}")
        
        subtotal = produto.preco * item.quantidade
        total_venda += subtotal
        
        itens_processados.append({
            "produto": produto,
            "quantidade": item.quantidade,
            "preco_unitario": produto.preco,
            "subtotal": subtotal
        })
    
    # Criar venda
    venda = Venda(
        cliente_email=dados_venda.cliente_email,
        total=total_venda,
        observacoes=dados_venda.observacoes
    )
    
    db.add(venda)
    db.flush()  # Para obter o ID
    
    # Criar itens e baixar estoque
    for item_proc in itens_processados:
        item_venda = ItemVenda(
            venda_id=venda.id,
            produto_id=item_proc["produto"].id,
            quantidade=item_proc["quantidade"],
            preco_unitario=item_proc["preco_unitario"],
            subtotal=item_proc["subtotal"]
        )
        db.add(item_venda)
        
        # Baixar estoque
        item_proc["produto"].estoque -= item_proc["quantidade"]
    
    db.commit()
    db.refresh(venda)
    
    # Log
    registrar_log(db, "venda_realizada", dados_venda.cliente_email, {
        "venda_id": venda.id,
        "total": float(total_venda),
        "itens_quantidade": len(dados_venda.itens)
    }, request)
    
    return RespostaPadrao(
        sucesso=True,
        mensagem=f"Venda realizada com sucesso! Total: R$ {total_venda:.2f}",
        dados={"venda_id": venda.id, "total": float(total_venda)},
        timestamp=datetime.now()
    )

@app.get("/api/v1/vendas/listar")
async def listar_vendas(limite: int = 50, db: Session = Depends(obter_db)):
    """Listar vendas recentes"""
    
    vendas = db.query(Venda).order_by(desc(Venda.data_venda)).limit(limite).all()
    
    resultado = []
    for venda in vendas:
        itens = []
        for item in venda.itens:
            itens.append({
                "produto_id": item.produto_id,
                "produto_nome": item.produto.nome,
                "quantidade": item.quantidade,
                "preco_unitario": float(item.preco_unitario),
                "subtotal": float(item.subtotal)
            })
        
        resultado.append({
            "id": venda.id,
            "cliente_email": venda.cliente_email,
            "total": float(venda.total),
            "observacoes": venda.observacoes,
            "data_venda": venda.data_venda,
            "itens": itens
        })
    
    return {
        "vendas": resultado,
        "total": len(resultado)
    }

# ==================== ENDPOINTS - RELATÓRIOS ====================
@app.get("/api/v1/relatorios/dashboard")
async def obter_dashboard(db: Session = Depends(obter_db)):
    """Dashboard executivo"""
    
    # Estatísticas gerais
    total_produtos = db.query(Produto).filter(Produto.ativo == True).count()
    total_categorias = db.query(Categoria).filter(Categoria.ativo == True).count()
    total_fornecedores = db.query(Fornecedor).filter(Fornecedor.ativo == True).count()
    total_vendas = db.query(Venda).count()
    
    # Valor total em estoque
    valor_estoque = db.query(func.sum(Produto.preco * Produto.estoque)).filter(Produto.ativo == True).scalar()
    valor_estoque = float(valor_estoque) if valor_estoque else 0
    
    # Receita total
    receita_total = db.query(func.sum(Venda.total)).scalar()
    receita_total = float(receita_total) if receita_total else 0
    
    # Produtos com estoque baixo
    produtos_estoque_baixo = db.query(Produto).filter(
        Produto.ativo == True,
        Produto.estoque <= Produto.estoque_minimo
    ).count()
    
    return {
        "resumo": {
            "total_produtos": total_produtos,
            "total_categorias": total_categorias,
            "total_fornecedores": total_fornecedores,
            "total_vendas": total_vendas,
            "valor_estoque": valor_estoque,
            "receita_total": receita_total,
            "produtos_estoque_baixo": produtos_estoque_baixo
        },
        "timestamp": datetime.now()
    }

@app.get("/api/v1/logs/listar")
async def listar_logs(limite: int = 100, acao: Optional[str] = None, usuario: Optional[str] = None, db: Session = Depends(obter_db)):
    """Listar logs de auditoria"""
    
    query = db.query(Log).order_by(desc(Log.data_criacao))
    
    if acao:
        query = query.filter(Log.acao == acao)
    
    if usuario:
        query = query.filter(Log.usuario_email == usuario)
    
    logs = query.limit(limite).all()
    
    resultado = []
    for log in logs:
        resultado.append({
            "id": log.id,
            "acao": log.acao,
            "usuario_email": log.usuario_email,
            "detalhes": log.detalhes,
            "ip_origem": log.ip_origem,
            "data_criacao": log.data_criacao
        })
    
    return {
        "logs": resultado,
        "total": len(resultado)
    }

# ==================== INICIALIZAÇÃO ====================
async def inicializar_dados_basicos():
    """Criar dados básicos se não existirem"""
    db = SessionLocal()
    
    try:
        # Verificar se já tem usuário admin
        admin = db.query(Usuario).filter(Usuario.email == "admin@vendperto.com").first()
        if not admin:
            admin = Usuario(
                nome="Administrador",
                email="admin@vendperto.com",
                senha_hash=hash_senha("admin123"),
                perfil="administrador"
            )
            db.add(admin)
            print("✅ Usuário admin criado: admin@vendperto.com / admin123")
        
        # Criar categorias básicas
        if db.query(Categoria).count() == 0:
            categorias_basicas = [
                {"nome": "Bebidas", "descricao": "Refrigerantes, sucos, águas"},
                {"nome": "Alimentos", "descricao": "Produtos alimentícios"},
                {"nome": "Higiene", "descricao": "Produtos de higiene pessoal"},
                {"nome": "Limpeza", "descricao": "Produtos de limpeza doméstica"}
            ]
            
            for cat_data in categorias_basicas:
                categoria = Categoria(**cat_data)
                db.add(categoria)
            
            print("✅ Categorias básicas criadas")
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Erro ao inicializar dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando VendPerto ERP - PostgreSQL")
    print(f"📖 Documentação: http://localhost:8001/docs")
    print(f"🔗 Endpoints: http://localhost:8001/")
    print(f"🗄️ Banco: PostgreSQL")
    print("=" * 60)
    
    # Inicializar dados básicos
    import asyncio
    asyncio.run(inicializar_dados_basicos())
    
    uvicorn.run(app, host="0.0.0.0", port=8001) 