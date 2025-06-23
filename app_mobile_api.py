#!/usr/bin/env python3
"""
🏪 VendPerto Mobile API - Mini Mercado de Condomínios
================================================

APIs específicas para o APP MOBILE dos moradores:
- Catálogo de produtos otimizado para mobile
- Carrinho de compras persistente
- Sistema de pedidos com rastreamento
- Perfil do morador

ERP Backend (porta 8001): Gestão interna do mini mercado
Mobile API (porta 8002): Interface para moradores
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid
import hashlib
import uvicorn

# ====================================
# 📱 MODELOS PARA MOBILE
# ====================================

class MoradorRegistro(BaseModel):
    nome: str = Field(..., min_length=2)
    email: EmailStr
    senha: str = Field(..., min_length=6)
    telefone: str
    apartamento: str
    bloco: Optional[str] = None
    
class MoradorLogin(BaseModel):
    email: EmailStr
    senha: str

class ItemCarrinho(BaseModel):
    produto_id: str
    quantidade: int = Field(..., gt=0)
    observacoes: Optional[str] = None

class PedidoMobile(BaseModel):
    items: List[ItemCarrinho]
    endereco_entrega: str
    forma_pagamento: str
    observacoes: Optional[str] = None

# ====================================
# 🗄️ BANCO EM MEMÓRIA MOBILE
# ====================================

moradores_db = {}
carrinhos_db = {}
pedidos_mobile_db = {}
tokens_mobile = {}

# ====================================
# 🔐 FUNÇÕES DE SEGURANÇA
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
# 🚀 APLICAÇÃO MOBILE
# ====================================

app = FastAPI(
    title="VendPerto Mobile API",
    description="APIs específicas para app mobile do mini mercado",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================
# 📱 AUTENTICAÇÃO MOBILE
# ====================================

@app.post("/api/v1/mobile/auth/registrar")
async def registrar_morador(morador: MoradorRegistro):
    """📝 Registra novo morador no app"""
    
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
        "data_cadastro": datetime.now(),
        "pedidos_realizados": 0
    }
    
    carrinhos_db[morador_id] = {"items": []}
    
    return {
        "sucesso": True,
        "mensagem": "Morador registrado com sucesso!",
        "morador_id": morador_id
    }

@app.post("/api/v1/mobile/auth/login")
async def login_morador(dados: MoradorLogin):
    """🔑 Login do morador"""
    
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
# 📱 CATÁLOGO MOBILE
# ====================================

@app.get("/api/v1/mobile/produtos/catalogo")
async def obter_catalogo_mobile(
    categoria: Optional[str] = None,
    busca: Optional[str] = None,
    morador=Depends(verificar_token_mobile)
):
    """🛍️ Catálogo otimizado para mobile"""
    
    produtos = [
        {
            "id": "prod_001",
            "nome": "Leite Integral 1L",
            "preco": 4.50,
            "categoria": "Laticínios",
            "disponivel": True,
            "estoque_atual": 15,
            "imagem_url": "/static/leite.jpg"
        },
        {
            "id": "prod_002",
            "nome": "Pão de Forma Integral",
            "preco": 6.80,
            "categoria": "Padaria",
            "disponivel": True,
            "estoque_atual": 8,
            "imagem_url": "/static/pao.jpg"
        },
        {
            "id": "prod_003",
            "nome": "Água Mineral 500ml",
            "preco": 2.00,
            "categoria": "Bebidas",
            "disponivel": True,
            "estoque_atual": 25,
            "imagem_url": "/static/agua.jpg"
        },
        {
            "id": "prod_004",
            "nome": "Refrigerante Cola 2L",
            "preco": 8.90,
            "categoria": "Bebidas",
            "disponivel": True,
            "estoque_atual": 12,
            "imagem_url": "/static/refri.jpg"
        }
    ]
    
    # Aplicar filtros
    if categoria:
        produtos = [p for p in produtos if p["categoria"].lower() == categoria.lower()]
    
    if busca:
        busca_lower = busca.lower()
        produtos = [p for p in produtos if busca_lower in p["nome"].lower()]
    
    return {
        "produtos": produtos,
        "total": len(produtos),
        "categorias": ["Laticínios", "Padaria", "Bebidas", "Doces", "Higiene"]
    }

# ====================================
# 📱 CARRINHO MOBILE
# ====================================

@app.get("/api/v1/mobile/carrinho")
async def obter_carrinho(morador=Depends(verificar_token_mobile)):
    """🛒 Carrinho atual do morador"""
    
    morador_id = morador["morador_id"]
    carrinho = carrinhos_db.get(morador_id, {"items": []})
    
    total_items = sum(item["quantidade"] for item in carrinho["items"])
    total_valor = sum(item["quantidade"] * item.get("preco_unitario", 0) for item in carrinho["items"])
    
    return {
        "carrinho": carrinho,
        "resumo": {
            "total_items": total_items,
            "total_valor": round(total_valor, 2),
            "taxa_entrega": 2.00,
            "valor_final": round(total_valor + 2.00, 2)
        }
    }

@app.post("/api/v1/mobile/carrinho/adicionar")
async def adicionar_ao_carrinho(item: ItemCarrinho, morador=Depends(verificar_token_mobile)):
    """➕ Adicionar item ao carrinho"""
    
    morador_id = morador["morador_id"]
    
    if morador_id not in carrinhos_db:
        carrinhos_db[morador_id] = {"items": []}
    
    carrinho = carrinhos_db[morador_id]
    
    # Preços dos produtos
    precos = {"prod_001": 4.50, "prod_002": 6.80, "prod_003": 2.00, "prod_004": 8.90}
    preco_unitario = precos.get(item.produto_id, 0.0)
    
    # Verificar se item já existe
    item_existente = None
    for i, cart_item in enumerate(carrinho["items"]):
        if cart_item["produto_id"] == item.produto_id:
            item_existente = i
            break
    
    if item_existente is not None:
        carrinho["items"][item_existente]["quantidade"] += item.quantidade
    else:
        carrinho["items"].append({
            "produto_id": item.produto_id,
            "quantidade": item.quantidade,
            "preco_unitario": preco_unitario,
            "observacoes": item.observacoes
        })
    
    return {
        "sucesso": True,
        "mensagem": "Item adicionado ao carrinho",
        "total_items": sum(i["quantidade"] for i in carrinho["items"])
    }

@app.delete("/api/v1/mobile/carrinho/limpar")
async def limpar_carrinho(morador=Depends(verificar_token_mobile)):
    """🗑️ Limpar carrinho"""
    
    morador_id = morador["morador_id"]
    carrinhos_db[morador_id] = {"items": []}
    
    return {"sucesso": True, "mensagem": "Carrinho limpo"}

# ====================================
# 📱 PEDIDOS MOBILE
# ====================================

@app.post("/api/v1/mobile/pedidos/criar")
async def criar_pedido_mobile(pedido: PedidoMobile, morador=Depends(verificar_token_mobile)):
    """🛍️ Criar pedido via mobile"""
    
    morador_id = morador["morador_id"]
    pedido_id = f"MOB{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
    
    # Calcular total
    precos = {"prod_001": 4.50, "prod_002": 6.80, "prod_003": 2.00, "prod_004": 8.90}
    total = sum(item.quantidade * precos.get(item.produto_id, 0) for item in pedido.items)
    taxa_entrega = 2.00
    total_final = total + taxa_entrega
    
    novo_pedido = {
        "id": pedido_id,
        "morador_id": morador_id,
        "status": "pendente",
        "data_pedido": datetime.now(),
        "items": [
            {
                "produto_id": item.produto_id,
                "quantidade": item.quantidade,
                "preco_unitario": precos.get(item.produto_id, 0),
                "observacoes": item.observacoes
            } for item in pedido.items
        ],
        "endereco_entrega": pedido.endereco_entrega,
        "forma_pagamento": pedido.forma_pagamento,
        "observacoes": pedido.observacoes,
        "subtotal": total,
        "taxa_entrega": taxa_entrega,
        "total": total_final,
        "tempo_estimado": "15-20 minutos"
    }
    
    pedidos_mobile_db[pedido_id] = novo_pedido
    
    # Atualizar contador do morador
    morador_data = moradores_db[morador["email"]]
    morador_data["pedidos_realizados"] += 1
    
    # Limpar carrinho
    carrinhos_db[morador_id] = {"items": []}
    
    return {
        "sucesso": True,
        "pedido_id": pedido_id,
        "total": total_final,
        "tempo_estimado": "15-20 minutos",
        "mensagem": "Pedido criado com sucesso!"
    }

@app.get("/api/v1/mobile/pedidos/meus")
async def listar_meus_pedidos(morador=Depends(verificar_token_mobile)):
    """📋 Pedidos do morador"""
    
    morador_id = morador["morador_id"]
    
    pedidos_morador = [
        pedido for pedido in pedidos_mobile_db.values()
        if pedido["morador_id"] == morador_id
    ]
    
    return {"pedidos": pedidos_morador, "total": len(pedidos_morador)}

@app.post("/api/v1/mobile/pedidos/{pedido_id}/cancelar")
async def cancelar_pedido(pedido_id: str, morador=Depends(verificar_token_mobile)):
    """❌ Cancelar pedido"""
    
    if pedido_id not in pedidos_mobile_db:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    pedido = pedidos_mobile_db[pedido_id]
    
    if pedido["morador_id"] != morador["morador_id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if pedido["status"] in ["saiu_entrega", "entregue"]:
        raise HTTPException(status_code=400, detail="Não é possível cancelar")
    
    pedido["status"] = "cancelado"
    
    return {"sucesso": True, "mensagem": "Pedido cancelado"}

# ====================================
# 📱 PERFIL MOBILE
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
            "bloco": morador_data["bloco"]
        },
        "estatisticas": {
            "total_pedidos": morador_data["pedidos_realizados"],
            "membro_desde": morador_data["data_cadastro"].strftime("%d/%m/%Y")
        }
    }

# ====================================
# 📱 STATUS
# ====================================

@app.get("/api/v1/mobile/status")
async def status_mobile():
    """📊 Status da API Mobile"""
    return {
        "status": "online",
        "versao": "1.0.0",
        "tipo": "VendPerto Mobile API",
        "descricao": "APIs para app mobile do mini mercado",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """✅ Health Check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ====================================
# 🚀 EXECUÇÃO
# ====================================

if __name__ == "__main__":
    print("🏪 Iniciando VendPerto Mobile API")
    print("📱 Documentação: http://localhost:8002/docs")
    print("🛒 Carrinho | 🛍️ Pedidos | 👤 Perfil")
    
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False) 