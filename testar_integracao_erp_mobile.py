#!/usr/bin/env python3
"""
🧪 TESTE INTEGRAÇÃO ERP ↔ Mobile API
===================================

Este script demonstra como deve funcionar a integração:
1. ERP na porta 8001 - Sistema principal
2. Mobile na porta 8002 - Interface que CONSOME do ERP
3. Quando mobile vende, baixa estoque real do ERP

IMPORTANTE: Execute primeiro o ERP na porta 8001
"""

import requests
import json
from datetime import datetime

# URLs dos sistemas
ERP_URL = "http://localhost:8001"
MOBILE_URL = "http://localhost:8002"

def testar_integracao():
    print("🧪 Testando Integração ERP ↔ Mobile API")
    print("=" * 50)
    
    # 1. Verificar se ERP está rodando
    print("\n1️⃣ Verificando ERP...")
    try:
        response = requests.get(f"{ERP_URL}/health")
        if response.status_code == 200:
            print("✅ ERP online na porta 8001")
        else:
            print("❌ ERP não está respondendo")
            return
    except:
        print("❌ ERP não está rodando na porta 8001")
        print("⚠️  Execute primeiro: python testar_api_direto.py")
        return
    
    # 2. Verificar produtos no ERP
    print("\n2️⃣ Listando produtos do ERP...")
    try:
        produtos_erp = requests.get(f"{ERP_URL}/api/v1/produtos/listar")
        if produtos_erp.status_code == 200:
            produtos = produtos_erp.json()
            print(f"✅ ERP tem {produtos['total']} produtos cadastrados")
            
            if produtos['total'] > 0:
                produto_exemplo = produtos['produtos'][0]
                print(f"📦 Produto exemplo: {produto_exemplo['nome']} - Estoque: {produto_exemplo.get('estoque_atual', 0)}")
                produto_id_teste = produto_exemplo['id']
                estoque_inicial = produto_exemplo.get('estoque_atual', 0)
            else:
                print("⚠️  Nenhum produto no ERP. Execute os testes do ERP primeiro.")
                return
        else:
            print("❌ Erro ao acessar produtos do ERP")
            return
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # 3. Verificar se Mobile API está rodando
    print("\n3️⃣ Verificando Mobile API...")
    try:
        response = requests.get(f"{MOBILE_URL}/api/v1/mobile/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Mobile API online na porta 8002")
            print(f"🔗 Integração ERP: {status.get('erp_integrado', False)}")
        else:
            print("❌ Mobile API não está respondendo")
            return
    except:
        print("❌ Mobile API não está rodando na porta 8002")
        print("⚠️  Execute: python mobile_api_integrada.py")
        return
    
    # 4. Registrar morador no Mobile
    print("\n4️⃣ Registrando morador no Mobile...")
    morador_data = {
        "nome": "João Silva",
        "email": "joao@condominio.com",
        "senha": "123456",
        "telefone": "11999999999",
        "apartamento": "101",
        "bloco": "A"
    }
    
    registro = requests.post(f"{MOBILE_URL}/api/v1/mobile/auth/registrar", json=morador_data)
    if registro.status_code == 200:
        print("✅ Morador registrado no Mobile")
    else:
        print("⚠️  Morador já existe ou erro no registro")
    
    # 5. Login no Mobile
    print("\n5️⃣ Fazendo login no Mobile...")
    login_data = {
        "email": "joao@condominio.com",
        "senha": "123456"
    }
    
    login = requests.post(f"{MOBILE_URL}/api/v1/mobile/auth/login", json=login_data)
    if login.status_code == 200:
        token_mobile = login.json()['token']
        print("✅ Login realizado no Mobile")
        headers_mobile = {"Authorization": f"Bearer {token_mobile}"}
    else:
        print("❌ Erro no login do Mobile")
        return
    
    # 6. Verificar catálogo Mobile (deve vir do ERP)
    print("\n6️⃣ Verificando catálogo Mobile (fonte: ERP)...")
    catalogo = requests.get(f"{MOBILE_URL}/api/v1/mobile/produtos/catalogo", headers=headers_mobile)
    if catalogo.status_code == 200:
        produtos_mobile = catalogo.json()
        print(f"✅ Mobile exibe {produtos_mobile['total']} produtos do ERP")
        print(f"📍 Fonte: {produtos_mobile.get('fonte', 'ERP Integrado')}")
    else:
        print("❌ Erro ao obter catálogo do Mobile")
        return
    
    # 7. Adicionar produto ao carrinho Mobile
    print("\n7️⃣ Adicionando produto ao carrinho Mobile...")
    item_carrinho = {
        "produto_id": produto_id_teste,
        "quantidade": 2,
        "observacoes": "Teste de integração"
    }
    
    adicionar = requests.post(f"{MOBILE_URL}/api/v1/mobile/carrinho/adicionar", json=item_carrinho, headers=headers_mobile)
    if adicionar.status_code == 200:
        print("✅ Produto adicionado ao carrinho Mobile")
    else:
        print(f"❌ Erro ao adicionar ao carrinho: {adicionar.text}")
        return
    
    # 8. Ver carrinho (preços do ERP)
    print("\n8️⃣ Verificando carrinho (preços do ERP)...")
    carrinho = requests.get(f"{MOBILE_URL}/api/v1/mobile/carrinho", headers=headers_mobile)
    if carrinho.status_code == 200:
        carrinho_data = carrinho.json()
        print(f"✅ Carrinho: {carrinho_data['resumo']['total_items']} itens")
        print(f"💰 Total: R$ {carrinho_data['resumo']['valor_final']}")
        print(f"📍 Fonte preços: {carrinho_data['fonte_precos']}")
    else:
        print("❌ Erro ao verificar carrinho")
        return
    
    # 9. Criar pedido Mobile (venda no ERP)
    print("\n9️⃣ Criando pedido Mobile (será processado como venda no ERP)...")
    pedido_data = {
        "items": [item_carrinho],
        "endereco_entrega": "Apt 101, Bloco A",
        "forma_pagamento": "PIX",
        "observacoes": "Entrega rápida por favor"
    }
    
    pedido = requests.post(f"{MOBILE_URL}/api/v1/mobile/pedidos/criar", json=pedido_data, headers=headers_mobile)
    if pedido.status_code == 200:
        pedido_resultado = pedido.json()
        print("✅ Pedido criado e processado no ERP!")
        print(f"🆔 ID Venda ERP: {pedido_resultado.get('venda_erp_id')}")
        print(f"💰 Total: R$ {pedido_resultado.get('total')}")
    else:
        print(f"❌ Erro ao criar pedido: {pedido.text}")
        return
    
    # 10. Verificar estoque no ERP após a venda
    print("\n🔟 Verificando estoque no ERP após venda...")
    produto_atualizado = requests.get(f"{ERP_URL}/api/v1/produtos/{produto_id_teste}")
    if produto_atualizado.status_code == 200:
        produto_data = produto_atualizado.json()
        estoque_final = produto_data.get('estoque_atual', 0)
        print(f"📦 Estoque inicial: {estoque_inicial}")
        print(f"📦 Estoque final: {estoque_final}")
        print(f"📉 Redução: {estoque_inicial - estoque_final} unidades")
        
        if estoque_final < estoque_inicial:
            print("✅ INTEGRAÇÃO FUNCIONA! Estoque baixou no ERP após venda Mobile!")
        else:
            print("❌ Problema: Estoque não foi baixado")
    else:
        print("❌ Erro ao verificar estoque final")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMO DA INTEGRAÇÃO:")
    print("📱 Mobile: Interface otimizada para moradores")
    print("🏪 ERP: Sistema principal com estoque real")
    print("🔄 Fluxo: Mobile → consome → ERP → baixa estoque")
    print("✅ Integração: Mobile não tem dados próprios!")

if __name__ == "__main__":
    testar_integracao() 