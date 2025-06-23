#!/usr/bin/env python3
"""
🏪 VendPerto Mobile API INTEGRADA - Mini Mercado de Condomínios
============================================================

APIs Mobile que se INTEGRAM com o ERP real:
- Produtos vêm do ERP (porta 8001)
- Pedidos são processados como vendas no ERP
- Estoque é controlado pelo ERP
- Mobile API é apenas uma interface otimizada

DEPENDÊNCIA: ERP deve estar rodando na porta 8001
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid
import hashlib
import uvicorn
import requests
import asyncio

# Configuração do ERP
ERP_BASE_URL = "http://localhost:8001"

# ====================================
# 📱 MODELOS MOBILE
# ====================================

class MoradorRegistro(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    telefone: str
    apartamento: str
    bloco: Optional[str] = None

class MoradorLogin(BaseModel):
    email: EmailStr
    senha: str

class ItemCarrinho(BaseModel):
    produto_id: str
    quantidade: int
    observacoes: Optional[str] = None

class PedidoMobile(BaseModel):
    items: List[ItemCarrinho]
    endereco_entrega: str
    forma_pagamento: str
    observacoes: Optional[str] = None

# ====================================
# 🗄️ BANCO MOBILE (apenas moradores)
# ====================================

moradores_db = {}
carrinhos_db = {}
tokens_mobile = {}

# ====================================
# 🔐 AUTENTICAÇÃO MOBILE
# ====================================

def hash_senha_mobile(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def gerar_token_mobile() -> str:
    return str(uuid.uuid4())

def verificar_token_mobile(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token obrigatório")
    
    token = authorization.split(" ")[1]
    if token not in tokens_mobile:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return tokens_mobile[token]

# ====================================
# 🔗 INTEGRAÇÃO COM ERP
# ====================================

async def verificar_erp_online():
    """Verifica se o ERP está rodando"""
    try:
        response = requests.get(f"{ERP_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

async def obter_produtos_do_erp():
    """Obtém produtos diretamente do ERP"""
    try:
        response = requests.get(f"{ERP_BASE_URL}/api/v1/produtos/listar", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"produtos": [], "total": 0}
    except:
        raise HTTPException(status_code=503, detail="ERP indisponível")

async def obter_produto_do_erp(produto_id: str):
    """Obtém detalhes de um produto do ERP"""
    try:
        response = requests.get(f"{ERP_BASE_URL}/api/v1/produtos/{produto_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

async def processar_venda_no_erp(items: List[dict], cliente_email: str, observacoes: str = None):
    """Processa venda diretamente no ERP"""
    try:
        # Primeiro, fazer login no ERP para obter token
        login_data = {
            "email": "admin@vendperto.com",  # Usuário sistema para mobile
            "senha": "admin123"
        }
        
        login_response = requests.post(
            f"{ERP_BASE_URL}/api/v1/auth/login-json",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Erro na autenticação com ERP")
        
        token_erp = login_response.json().get("access_token")
        
        # Processar venda no ERP
        venda_data = {
            "cliente_email": cliente_email,
            "items": items,
            "observacoes": observacoes or "Pedido via Mobile App"
        }
        
        headers_erp = {"Authorization": f"Bearer {token_erp}"}
        
        venda_response = requests.post(
            f"{ERP_BASE_URL}/api/v1/vendas/realizar",
            json=venda_data,
            headers=headers_erp,
            timeout=15
        )
        
        if venda_response.status_code == 200:
            return venda_response.json()
        else:
            raise HTTPException(status_code=400, detail="Erro ao processar venda no ERP")
            
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="ERP indisponível para processar venda")

# ====================================
# 🚀 APLICAÇÃO MOBILE INTEGRADA
# ====================================

app = FastAPI(
    title="VendPerto Mobile API - INTEGRADA",
    description="APIs Mobile integradas com o ERP real",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================
# 📱 ENDPOINTS - VERIFICAÇÃO
# ====================================

@app.get("/api/v1/mobile/status")
async def status_mobile():
    """Status da API Mobile com verificação do ERP"""
    erp_online = await verificar_erp_online()
    
    return {
        "status": "online",
        "versao": "2.0.0 - INTEGRADA",
        "tipo": "VendPerto Mobile API",
        "erp_integrado": erp_online,
        "erp_url": ERP_BASE_URL,
        "timestamp": datetime.now().isoformat(),
        "integracao": "Produtos e vendas vêm do ERP real"
    }

# ====================================
# 📱 ENDPOINTS - AUTENTICAÇÃO
# ====================================

@app.post("/api/v1/mobile/auth/registrar")
async def registrar_morador(morador: MoradorRegistro):
    """Registra morador no app mobile"""
    if morador.email in moradores_db:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    morador_id = str(uuid.uuid4())
    moradores_db[morador.email] = {
        "id": morador_id,
        "nome": morador.nome,
        "email": morador.email,
        "senha_hash": hash_senha_mobile(morador.senha),
        "telefone": morador.telefone,
        "apartamento": morador.apartamento,
        "bloco": morador.bloco,
        "data_cadastro": datetime.now()
    }
    
    carrinhos_db[morador_id] = {"items": []}
    
    return {
        "sucesso": True,
        "mensagem": "Morador registrado com sucesso!",
        "morador_id": morador_id
    }

@app.post("/api/v1/mobile/auth/login")
async def login_morador(dados: MoradorLogin):
    """Login do morador"""
    if dados.email not in moradores_db:
        raise HTTPException(status_code=400, detail="Email não encontrado")
    
    morador = moradores_db[dados.email]
    if hash_senha_mobile(dados.senha) != morador["senha_hash"]:
        raise HTTPException(status_code=400, detail="Senha incorreta")
    
    token = gerar_token_mobile()
    tokens_mobile[token] = {
        "morador_id": morador["id"],
        "email": dados.email,
        "login_em": datetime.now()
    }
    
    return {
        "sucesso": True,
        "token": token,
        "morador": {
            "id": morador["id"],
            "nome": morador["nome"],
            "apartamento": morador["apartamento"],
            "bloco": morador["bloco"]
        }
    }

# ====================================
# 📱 ENDPOINTS - CATÁLOGO (VEM DO ERP)
# ====================================

@app.get("/api/v1/mobile/produtos/catalogo")
async def obter_catalogo_mobile(
    categoria: Optional[str] = None,
    busca: Optional[str] = None,
    morador=Depends(verificar_token_mobile)
):
    """🛍️ Catálogo que vem diretamente do ERP"""
    
    # Verificar se ERP está online
    if not await verificar_erp_online():
        raise HTTPException(status_code=503, detail="Sistema ERP temporariamente indisponível")
    
    # Obter produtos do ERP real
    produtos_erp = await obter_produtos_do_erp()
    produtos = produtos_erp.get("produtos", [])
    
    # Aplicar filtros mobile
    if categoria:
        produtos = [p for p in produtos if p.get("categoria", "").lower() == categoria.lower()]
    
    if busca:
        busca_lower = busca.lower()
        produtos = [p for p in produtos if busca_lower in p.get("nome", "").lower()]
    
    # Otimizar para mobile (campos essenciais)
    produtos_mobile = []
    for produto in produtos:
        # Só exibir produtos com estoque > 0
        if produto.get("estoque_atual", 0) > 0:
            produtos_mobile.append({
                "id": produto["id"],
                "nome": produto["nome"],
                "preco": produto["preco"],
                "categoria": produto.get("categoria", "Geral"),
                "disponivel": True,
                "estoque_atual": produto.get("estoque_atual", 0),
                "descricao": produto.get("descricao", ""),
                "unidade": produto.get("unidade", "un")
            })
    
    return {
        "produtos": produtos_mobile,
        "total": len(produtos_mobile),
        "fonte": "ERP Integrado",
        "erp_url": ERP_BASE_URL
    }

@app.get("/api/v1/mobile/produtos/{produto_id}")
async def obter_produto_detalhado(produto_id: str, morador=Depends(verificar_token_mobile)):
    """📋 Detalhes do produto vindo do ERP"""
    
    produto_erp = await obter_produto_do_erp(produto_id)
    if not produto_erp:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return {
        "id": produto_erp["id"],
        "nome": produto_erp["nome"],
        "preco": produto_erp["preco"],
        "categoria": produto_erp.get("categoria", "Geral"),
        "disponivel": produto_erp.get("estoque_atual", 0) > 0,
        "estoque_atual": produto_erp.get("estoque_atual", 0),
        "descricao": produto_erp.get("descricao", ""),
        "unidade": produto_erp.get("unidade", "un"),
        "fonte": "ERP Real"
    }

# ====================================
# 📱 ENDPOINTS - CARRINHO
# ====================================

@app.get("/api/v1/mobile/carrinho")
async def obter_carrinho(morador=Depends(verificar_token_mobile)):
    """🛒 Carrinho com preços atualizados do ERP"""
    
    morador_id = morador["morador_id"]
    carrinho = carrinhos_db.get(morador_id, {"items": []})
    
    # Atualizar preços do ERP
    total_valor = 0
    for item in carrinho["items"]:
        produto_erp = await obter_produto_do_erp(item["produto_id"])
        if produto_erp:
            item["preco_unitario"] = produto_erp["preco"]
            item["nome_produto"] = produto_erp["nome"]
            item["disponivel"] = produto_erp.get("estoque_atual", 0) >= item["quantidade"]
            total_valor += item["quantidade"] * produto_erp["preco"]
    
    return {
        "carrinho": carrinho,
        "resumo": {
            "total_items": sum(item["quantidade"] for item in carrinho["items"]),
            "total_valor": round(total_valor, 2),
            "taxa_entrega": 2.00,
            "valor_final": round(total_valor + 2.00, 2)
        },
        "fonte_precos": "ERP Real"
    }

@app.post("/api/v1/mobile/carrinho/adicionar")
async def adicionar_ao_carrinho(item: ItemCarrinho, morador=Depends(verificar_token_mobile)):
    """➕ Adiciona item com validação do ERP"""
    
    morador_id = morador["morador_id"]
    
    # Verificar se produto existe no ERP
    produto_erp = await obter_produto_do_erp(item.produto_id)
    if not produto_erp:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Verificar estoque
    if produto_erp.get("estoque_atual", 0) < item.quantidade:
        raise HTTPException(status_code=400, detail="Estoque insuficiente")
    
    if morador_id not in carrinhos_db:
        carrinhos_db[morador_id] = {"items": []}
    
    carrinho = carrinhos_db[morador_id]
    
    # Verificar se item já existe
    item_existente = None
    for i, cart_item in enumerate(carrinho["items"]):
        if cart_item["produto_id"] == item.produto_id:
            item_existente = i
            break
    
    if item_existente is not None:
        nova_quantidade = carrinho["items"][item_existente]["quantidade"] + item.quantidade
        if produto_erp.get("estoque_atual", 0) < nova_quantidade:
            raise HTTPException(status_code=400, detail="Estoque insuficiente para essa quantidade")
        carrinho["items"][item_existente]["quantidade"] = nova_quantidade
    else:
        carrinho["items"].append({
            "produto_id": item.produto_id,
            "quantidade": item.quantidade,
            "preco_unitario": produto_erp["preco"],
            "nome_produto": produto_erp["nome"],
            "observacoes": item.observacoes,
            "adicionado_em": datetime.now().isoformat()
        })
    
    return {
        "sucesso": True,
        "mensagem": "Item adicionado ao carrinho",
        "total_items": sum(i["quantidade"] for i in carrinho["items"])
    }

@app.delete("/api/v1/mobile/carrinho/limpar")
async def limpar_carrinho(morador=Depends(verificar_token_mobile)):
    """🗑️ Limpa carrinho"""
    morador_id = morador["morador_id"]
    carrinhos_db[morador_id] = {"items": []}
    return {"sucesso": True, "mensagem": "Carrinho limpo"}

# ====================================
# 📱 ENDPOINTS - PEDIDOS (INTEGRADOS)
# ====================================

@app.post("/api/v1/mobile/pedidos/criar")
async def criar_pedido_mobile(pedido: PedidoMobile, morador=Depends(verificar_token_mobile)):
    """🛍️ Cria pedido processando venda no ERP"""
    
    morador_id = morador["morador_id"]
    morador_email = morador["email"]
    
    # Converter itens para formato do ERP
    items_erp = []
    for item in pedido.items:
        produto_erp = await obter_produto_do_erp(item.produto_id)
        if not produto_erp:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")
        
        if produto_erp.get("estoque_atual", 0) < item.quantidade:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para {produto_erp['nome']}")
        
        items_erp.append({
            "produto_id": item.produto_id,
            "quantidade": item.quantidade,
            "preco_unitario": produto_erp["preco"]
        })
    
    # Processar venda no ERP
    observacoes_completas = f"PEDIDO MOBILE - {pedido.endereco_entrega}"
    if pedido.observacoes:
        observacoes_completas += f" | {pedido.observacoes}"
    
    resultado_venda = await processar_venda_no_erp(
        items_erp, 
        morador_email,
        observacoes_completas
    )
    
    # Limpar carrinho após pedido
    carrinhos_db[morador_id] = {"items": []}
    
    return {
        "sucesso": True,
        "pedido_id": resultado_venda.get("venda_id"),
        "total": resultado_venda.get("total"),
        "mensagem": "Pedido processado no ERP com sucesso!",
        "venda_erp_id": resultado_venda.get("venda_id"),
        "endereco_entrega": pedido.endereco_entrega,
        "forma_pagamento": pedido.forma_pagamento
    }

@app.get("/api/v1/mobile/pedidos/meus")
async def listar_meus_pedidos(morador=Depends(verificar_token_mobile)):
    """📋 Lista pedidos do morador (vendas do ERP)"""
    
    return {
        "mensagem": "Pedidos são processados como vendas no ERP",
        "total": 0,
        "pedidos": [],
        "info": "Para ver histórico completo, consulte o sistema ERP",
        "erp_url": f"{ERP_BASE_URL}/docs"
    }

# ====================================
# 📱 ENDPOINTS - PERFIL
# ====================================

@app.get("/api/v1/mobile/perfil")
async def obter_perfil_morador(morador=Depends(verificar_token_mobile)):
    """👤 Perfil do morador"""
    
    morador_data = moradores_db[morador["email"]]
    
    return {
        "perfil": {
            "nome": morador_data["nome"],
            "email": morador_data["email"],
            "telefone": morador_data["telefone"],
            "apartamento": morador_data["apartamento"],
            "bloco": morador_data["bloco"],
            "membro_desde": morador_data["data_cadastro"].strftime("%d/%m/%Y")
        },
        "integracao": {
            "erp_conectado": await verificar_erp_online(),
            "fonte_produtos": "ERP Real",
            "processamento_pedidos": "ERP Real"
        }
    }

# ====================================
# 🚀 EXECUÇÃO
# ====================================

if __name__ == "__main__":
    print("🏪 Iniciando VendPerto Mobile API - INTEGRADA COM ERP")
    print("📱 Documentação: http://localhost:8002/docs")
    print("🔗 Integração: Produtos e vendas vêm do ERP (porta 8001)")
    print("⚠️  IMPORTANTE: ERP deve estar rodando na porta 8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False) 