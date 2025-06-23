#!/usr/bin/env python3
"""
🏪 VendPerto Mobile API - Mini Mercado de Condomínios
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid
import hashlib
import uvicorn

# Modelos Mobile
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

# Banco em memória
moradores_db = {}
carrinhos_db = {}
pedidos_mobile_db = {}
tokens_mobile = {}

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

# App Mobile
app = FastAPI(
    title="VendPerto Mobile API",
    description="APIs para app mobile do mini mercado",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/mobile/auth/registrar")
async def registrar_morador(morador: MoradorRegistro):
    """Registra morador no app"""
    if morador.email in moradores_db:
        raise HTTPException(status_code=400, detail="Email já existe")
    
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
    
    return {"sucesso": True, "morador_id": morador_id}

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
            "apartamento": morador["apartamento"]
        }
    }

@app.get("/api/v1/mobile/produtos/catalogo")
async def obter_catalogo_mobile(morador=Depends(verificar_token_mobile)):
    """Catálogo para mobile"""
    produtos = [
        {
            "id": "prod_001",
            "nome": "Leite Integral 1L",
            "preco": 4.50,
            "categoria": "Laticínios",
            "disponivel": True,
            "estoque_atual": 15
        },
        {
            "id": "prod_002",
            "nome": "Pão de Forma",
            "preco": 6.80,
            "categoria": "Padaria",
            "disponivel": True,
            "estoque_atual": 8
        }
    ]
    
    return {"produtos": produtos, "total": len(produtos)}

@app.post("/api/v1/mobile/carrinho/adicionar")
async def adicionar_ao_carrinho(item: ItemCarrinho, morador=Depends(verificar_token_mobile)):
    """Adiciona item ao carrinho"""
    morador_id = morador["morador_id"]
    
    if morador_id not in carrinhos_db:
        carrinhos_db[morador_id] = {"items": []}
    
    carrinho = carrinhos_db[morador_id]
    
    precos = {"prod_001": 4.50, "prod_002": 6.80}
    preco_unitario = precos.get(item.produto_id, 0.0)
    
    carrinho["items"].append({
        "produto_id": item.produto_id,
        "quantidade": item.quantidade,
        "preco_unitario": preco_unitario,
        "observacoes": item.observacoes
    })
    
    return {"sucesso": True, "mensagem": "Item adicionado"}

@app.get("/api/v1/mobile/carrinho")
async def obter_carrinho(morador=Depends(verificar_token_mobile)):
    """Obtém carrinho"""
    morador_id = morador["morador_id"]
    carrinho = carrinhos_db.get(morador_id, {"items": []})
    
    total_valor = sum(item["quantidade"] * item.get("preco_unitario", 0) for item in carrinho["items"])
    
    return {
        "carrinho": carrinho,
        "total_valor": round(total_valor, 2)
    }

@app.post("/api/v1/mobile/pedidos/criar")
async def criar_pedido_mobile(pedido: PedidoMobile, morador=Depends(verificar_token_mobile)):
    """Cria pedido via mobile"""
    morador_id = morador["morador_id"]
    pedido_id = f"MOB{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
    
    precos = {"prod_001": 4.50, "prod_002": 6.80}
    total = sum(item.quantidade * precos.get(item.produto_id, 0) for item in pedido.items)
    
    novo_pedido = {
        "id": pedido_id,
        "morador_id": morador_id,
        "status": "pendente",
        "data_pedido": datetime.now(),
        "items": [
            {
                "produto_id": item.produto_id,
                "quantidade": item.quantidade,
                "preco_unitario": precos.get(item.produto_id, 0)
            } for item in pedido.items
        ],
        "endereco_entrega": pedido.endereco_entrega,
        "forma_pagamento": pedido.forma_pagamento,
        "total": total
    }
    
    pedidos_mobile_db[pedido_id] = novo_pedido
    carrinhos_db[morador_id] = {"items": []}
    
    return {
        "sucesso": True,
        "pedido_id": pedido_id,
        "total": total
    }

@app.get("/api/v1/mobile/pedidos/meus")
async def listar_meus_pedidos(morador=Depends(verificar_token_mobile)):
    """Lista pedidos do morador"""
    morador_id = morador["morador_id"]
    
    pedidos_morador = [
        pedido for pedido in pedidos_mobile_db.values()
        if pedido["morador_id"] == morador_id
    ]
    
    return {"pedidos": pedidos_morador, "total": len(pedidos_morador)}

@app.get("/api/v1/mobile/status")
async def status_mobile():
    """Status da API Mobile"""
    return {
        "status": "online",
        "versao": "1.0.0",
        "tipo": "VendPerto Mobile API",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🏪 Iniciando VendPerto Mobile API")
    print("📱 Documentação: http://localhost:8002/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False) 