#!/usr/bin/env python3
"""
🏪 VendPerto Mobile API - Mini Mercado de Condomínios
==================================================

APIs específicas para o APP MOBILE dos moradores:
- Catálogo de produtos
- Carrinho de compras
- Sistema de pedidos
- Perfil do morador
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
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
# 🔐 FUNÇÕES DE AUTENTICAÇÃO
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

app_mobile = FastAPI(
    title="VendPerto Mobile API",
    description="APIs específicas para app mobile do mini mercado",
    version="1.0.0",
    docs_url="/mobile/docs",
    redoc_url="/mobile/redoc"
)

app_mobile.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================
# 📱 ENDPOINTS - AUTENTICAÇÃO
# ====================================

@app_mobile.post("/mobile/v1/auth/registrar")
async def registrar_morador(morador: MoradorRegistro):
    """📝 Registra um novo morador no app"""
    
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

@app_mobile.post("/mobile/v1/auth/login")
async def login_morador(dados: MoradorLogin):
    """🔑 Login do morador no app"""
    
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
# 📱 ENDPOINTS - CATÁLOGO
# ====================================

@app_mobile.get("/mobile/v1/produtos/catalogo")
async def obter_catalogo_mobile(
    categoria: Optional[str] = None,
    busca: Optional[str] = None,
    morador=Depends(verificar_token_mobile)
):
    """🛍️ Catálogo de produtos para mobile"""
    
    # Mock de produtos do mini mercado
    produtos = [
        {
            "id": "prod_001",
            "nome": "Leite Integral 1L",
            "descricao": "Leite integral pasteurizado",
            "preco": 4.50,
            "categoria": "Laticínios",
            "imagem_url": "https://example.com/leite.jpg",
            "disponivel": True,
            "estoque_atual": 15,
            "unidade": "un"
        },
        {
            "id": "prod_002",
            "nome": "Pão de Forma",
            "descricao": "Pão de forma integral 500g",
            "preco": 6.80,
            "categoria": "Padaria",
            "imagem_url": "https://example.com/pao.jpg",
            "disponivel": True,
            "estoque_atual": 8,
            "unidade": "un"
        },
        {
            "id": "prod_003",
            "nome": "Água Mineral 500ml",
            "descricao": "Água mineral natural",
            "preco": 2.00,
            "categoria": "Bebidas",
            "imagem_url": "https://example.com/agua.jpg",
            "disponivel": True,
            "estoque_atual": 25,
            "unidade": "un"
        },
        {
            "id": "prod_004",
            "nome": "Refrigerante Cola 2L",
            "descricao": "Refrigerante sabor cola",
            "preco": 8.90,
            "categoria": "Bebidas",
            "imagem_url": "https://example.com/refri.jpg",
            "disponivel": True,
            "estoque_atual": 12,
            "unidade": "un"
        },
        {
            "id": "prod_005",
            "nome": "Biscoito Recheado",
            "descricao": "Biscoito recheado chocolate",
            "preco": 3.25,
            "categoria": "Doces",
            "imagem_url": "https://example.com/biscoito.jpg",
            "disponivel": False,
            "estoque_atual": 0,
            "unidade": "un"
        }
    ]
    
    # Filtros
    if categoria:
        produtos = [p for p in produtos if p["categoria"].lower() == categoria.lower()]
    
    if busca:
        busca_lower = busca.lower()
        produtos = [p for p in produtos if busca_lower in p["nome"].lower()]
    
    return {
        "produtos": produtos,
        "total": len(produtos),
        "categorias_disponiveis": ["Laticínios", "Padaria", "Bebidas", "Doces", "Higiene", "Limpeza"]
    }

@app_mobile.get("/mobile/v1/produtos/{produto_id}")
async def obter_produto_detalhado(produto_id: str, morador=Depends(verificar_token_mobile)):
    """📋 Detalhes de um produto"""
    
    if produto_id == "prod_001":
        return {
            "id": "prod_001",
            "nome": "Leite Integral 1L",
            "descricao": "Leite integral pasteurizado de alta qualidade",
            "preco": 4.50,
            "categoria": "Laticínios",
            "imagem_url": "https://example.com/leite.jpg",
            "disponivel": True,
            "estoque_atual": 15,
            "unidade": "un",
            "marca": "Fazenda Verde",
            "validade": "2024-02-15"
        }
    
    raise HTTPException(status_code=404, detail="Produto não encontrado")

# ====================================
# 📱 ENDPOINTS - CARRINHO
# ====================================

@app_mobile.get("/mobile/v1/carrinho")
async def obter_carrinho(morador=Depends(verificar_token_mobile)):
    """🛒 Obtém carrinho atual"""
    
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

@app_mobile.post("/mobile/v1/carrinho/adicionar")
async def adicionar_ao_carrinho(item: ItemCarrinho, morador=Depends(verificar_token_mobile)):
    """➕ Adiciona item ao carrinho"""
    
    morador_id = morador["morador_id"]
    
    if morador_id not in carrinhos_db:
        carrinhos_db[morador_id] = {"items": []}
    
    carrinho = carrinhos_db[morador_id]
    
    # Mock de preços
    precos = {
        "prod_001": 4.50,
        "prod_002": 6.80,
        "prod_003": 2.00,
        "prod_004": 8.90,
        "prod_005": 3.25
    }
    
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
            "observacoes": item.observacoes,
            "adicionado_em": datetime.now().isoformat()
        })
    
    return {
        "sucesso": True,
        "mensagem": "Item adicionado ao carrinho",
        "total_items": sum(i["quantidade"] for i in carrinho["items"])
    }

@app_mobile.delete("/mobile/v1/carrinho/limpar")
async def limpar_carrinho(morador=Depends(verificar_token_mobile)):
    """🗑️ Limpa carrinho"""
    
    morador_id = morador["morador_id"]
    carrinhos_db[morador_id] = {"items": []}
    
    return {"sucesso": True, "mensagem": "Carrinho limpo"}

# ====================================
# 📱 ENDPOINTS - PEDIDOS
# ====================================

@app_mobile.post("/mobile/v1/pedidos/criar")
async def criar_pedido_mobile(pedido: PedidoMobile, morador=Depends(verificar_token_mobile)):
    """🛍️ Cria pedido via mobile"""
    
    morador_id = morador["morador_id"]
    pedido_id = f"PED{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Calcular total
    precos = {"prod_001": 4.50, "prod_002": 6.80, "prod_003": 2.00, "prod_004": 8.90, "prod_005": 3.25}
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
        "mensagem": "Pedido criado! Você receberá atualizações em tempo real."
    }

@app_mobile.get("/mobile/v1/pedidos/meus")
async def listar_meus_pedidos(morador=Depends(verificar_token_mobile)):
    """📋 Lista pedidos do morador"""
    
    morador_id = morador["morador_id"]
    
    pedidos_morador = [
        pedido for pedido in pedidos_mobile_db.values()
        if pedido["morador_id"] == morador_id
    ]
    
    # Ordenar por data
    pedidos_morador.sort(key=lambda x: x["data_pedido"], reverse=True)
    
    return {"pedidos": pedidos_morador, "total": len(pedidos_morador)}

@app_mobile.get("/mobile/v1/pedidos/{pedido_id}")
async def obter_detalhes_pedido(pedido_id: str, morador=Depends(verificar_token_mobile)):
    """📄 Detalhes de um pedido"""
    
    if pedido_id not in pedidos_mobile_db:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    pedido = pedidos_mobile_db[pedido_id]
    
    if pedido["morador_id"] != morador["morador_id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return pedido

@app_mobile.post("/mobile/v1/pedidos/{pedido_id}/cancelar")
async def cancelar_pedido(pedido_id: str, morador=Depends(verificar_token_mobile)):
    """❌ Cancela pedido"""
    
    if pedido_id not in pedidos_mobile_db:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    pedido = pedidos_mobile_db[pedido_id]
    
    if pedido["morador_id"] != morador["morador_id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if pedido["status"] in ["saiu_entrega", "entregue"]:
        raise HTTPException(status_code=400, detail="Não é possível cancelar")
    
    pedido["status"] = "cancelado"
    pedido["data_atualizacao"] = datetime.now()
    
    return {"sucesso": True, "mensagem": "Pedido cancelado"}

# ====================================
# 📱 ENDPOINTS - PERFIL
# ====================================

@app_mobile.get("/mobile/v1/perfil")
async def obter_perfil_morador(morador=Depends(verificar_token_mobile)):
    """👤 Perfil do morador"""
    
    morador_data = moradores_db[morador["email"]]
    
    pedidos_morador = [p for p in pedidos_mobile_db.values() if p["morador_id"] == morador["morador_id"]]
    valor_total = sum(p["total"] for p in pedidos_morador)
    
    return {
        "perfil": {
            "nome": morador_data["nome"],
            "email": morador_data["email"],
            "telefone": morador_data["telefone"],
            "apartamento": morador_data["apartamento"],
            "bloco": morador_data["bloco"],
            "membro_desde": morador_data["data_cadastro"].strftime("%d/%m/%Y")
        },
        "estatisticas": {
            "total_pedidos": morador_data["pedidos_realizados"],
            "valor_total_compras": round(valor_total, 2),
            "economia_estimada": round(valor_total * 0.1, 2)
        }
    }

# ====================================
# 📱 STATUS DA API
# ====================================

@app_mobile.get("/mobile/v1/status")
async def status_mobile():
    """📊 Status da API mobile"""
    return {
        "status": "online",
        "versao": "1.0.0",
        "tipo": "VendPerto Mobile API",
        "descricao": "APIs para app mobile do mini mercado",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "Autenticação (/mobile/v1/auth/*)",
            "Catálogo (/mobile/v1/produtos/*)",
            "Carrinho (/mobile/v1/carrinho/*)",
            "Pedidos (/mobile/v1/pedidos/*)",
            "Perfil (/mobile/v1/perfil)"
        ]
    }

# ====================================
# 🚀 EXECUÇÃO
# ====================================

if __name__ == "__main__":
    print("🏪 Iniciando VendPerto Mobile API - Mini Mercado")
    print("📱 App dos Moradores: http://localhost:8002/mobile/docs")
    print("🛒 Carrinho | 🛍️ Pedidos | 👤 Perfil")
    
    uvicorn.run(app_mobile, host="0.0.0.0", port=8002, reload=False) 