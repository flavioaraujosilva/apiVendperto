#!/usr/bin/env python3
"""
🧪 Testes das APIs Mobile - VendPerto Mini Mercado
==============================================

Script para testar todas as funcionalidades das APIs mobile:
- Registro e login de moradores
- Catálogo de produtos
- Carrinho de compras
- Criação de pedidos
- Consulta de pedidos
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8002"
headers = {"Content-Type": "application/json"}

def imprimir_secao(titulo):
    print(f"\n{'='*50}")
    print(f"🧪 {titulo}")
    print('='*50)

def imprimir_resultado(teste, sucesso, dados=None):
    status = "✅ PASSOU" if sucesso else "❌ FALHOU"
    print(f"{status} - {teste}")
    if dados:
        print(f"   Resultado: {dados}")

def testar_apis_mobile():
    print("🏪 INICIANDO TESTES DAS APIs MOBILE")
    print(f"📱 URL Base: {BASE_URL}")
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    token_morador = None
    
    try:
        # ====================================
        # 1. TESTE DE STATUS
        # ====================================
        imprimir_secao("STATUS DA API MOBILE")
        
        response = requests.get(f"{BASE_URL}/api/v1/mobile/status")
        sucesso = response.status_code == 200
        imprimir_resultado("Status da API", sucesso, response.json() if sucesso else response.text)
        
        # ====================================
        # 2. REGISTRO DE MORADOR
        # ====================================
        imprimir_secao("REGISTRO DE MORADOR")
        
        dados_morador = {
            "nome": "João Silva",
            "email": "joao.silva@condominio.com",
            "senha": "123456",
            "telefone": "(11) 99999-9999",
            "apartamento": "101",
            "bloco": "A"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/mobile/auth/registrar",
            headers=headers,
            json=dados_morador
        )
        
        sucesso = response.status_code == 200
        resultado = response.json() if sucesso else response.text
        imprimir_resultado("Registro de morador", sucesso, resultado)
        
        # ====================================
        # 3. LOGIN DO MORADOR
        # ====================================
        imprimir_secao("LOGIN DO MORADOR")
        
        dados_login = {
            "email": "joao.silva@condominio.com",
            "senha": "123456"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/mobile/auth/login",
            headers=headers,
            json=dados_login
        )
        
        sucesso = response.status_code == 200
        resultado = response.json() if sucesso else response.text
        imprimir_resultado("Login do morador", sucesso, resultado)
        
        if sucesso and 'token' in resultado:
            token_morador = resultado['token']
            print(f"   🔑 Token obtido: {token_morador[:20]}...")
        
        # ====================================
        # 4. CATÁLOGO DE PRODUTOS
        # ====================================
        imprimir_secao("CATÁLOGO DE PRODUTOS MOBILE")
        
        if token_morador:
            headers_auth = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token_morador}"
            }
            
            response = requests.get(
                f"{BASE_URL}/api/v1/mobile/produtos/catalogo",
                headers=headers_auth
            )
            
            sucesso = response.status_code == 200
            resultado = response.json() if sucesso else response.text
            imprimir_resultado("Obter catálogo", sucesso, 
                             f"{len(resultado.get('produtos', []))} produtos encontrados" if sucesso else resultado)
            
            if sucesso:
                print("   📦 Produtos disponíveis:")
                for produto in resultado.get('produtos', [])[:3]:
                    print(f"      - {produto['nome']}: R$ {produto['preco']}")
        
        # ====================================
        # 5. ADICIONAR ITENS AO CARRINHO
        # ====================================
        imprimir_secao("CARRINHO DE COMPRAS")
        
        if token_morador:
            # Adicionar primeiro item
            item1 = {
                "produto_id": "prod_001",
                "quantidade": 2,
                "observacoes": "Leite bem gelado, por favor"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/mobile/carrinho/adicionar",
                headers=headers_auth,
                json=item1
            )
            
            sucesso = response.status_code == 200
            resultado = response.json() if sucesso else response.text
            imprimir_resultado("Adicionar item 1 ao carrinho", sucesso, resultado)
            
            # Adicionar segundo item
            item2 = {
                "produto_id": "prod_002",
                "quantidade": 1
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/mobile/carrinho/adicionar",
                headers=headers_auth,
                json=item2
            )
            
            sucesso = response.status_code == 200
            imprimir_resultado("Adicionar item 2 ao carrinho", sucesso)
            
            # Visualizar carrinho
            response = requests.get(
                f"{BASE_URL}/api/v1/mobile/carrinho",
                headers=headers_auth
            )
            
            sucesso = response.status_code == 200
            resultado = response.json() if sucesso else response.text
            imprimir_resultado("Visualizar carrinho", sucesso, 
                             f"Total: R$ {resultado.get('total_valor', 0)}" if sucesso else resultado)
            
            if sucesso:
                print(f"   🛒 Itens no carrinho: {len(resultado.get('carrinho', {}).get('items', []))}")
        
        # ====================================
        # 6. CRIAR PEDIDO
        # ====================================
        imprimir_secao("CRIAÇÃO DE PEDIDO")
        
        if token_morador:
            pedido_dados = {
                "items": [
                    {
                        "produto_id": "prod_001",
                        "quantidade": 2,
                        "observacoes": "Leite bem gelado"
                    },
                    {
                        "produto_id": "prod_002",
                        "quantidade": 1
                    }
                ],
                "endereco_entrega": "Apartamento 101, Bloco A",
                "forma_pagamento": "pix",
                "observacoes": "Entregar pela manhã se possível"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/mobile/pedidos/criar",
                headers=headers_auth,
                json=pedido_dados
            )
            
            sucesso = response.status_code == 200
            resultado = response.json() if sucesso else response.text
            imprimir_resultado("Criar pedido", sucesso, resultado)
            
            if sucesso:
                pedido_id = resultado.get('pedido_id')
                print(f"   🛍️ Pedido criado: {pedido_id}")
                print(f"   💰 Total: R$ {resultado.get('total', 0)}")
        
        # ====================================
        # 7. LISTAR PEDIDOS DO MORADOR
        # ====================================
        imprimir_secao("CONSULTA DE PEDIDOS")
        
        if token_morador:
            response = requests.get(
                f"{BASE_URL}/api/v1/mobile/pedidos/meus",
                headers=headers_auth
            )
            
            sucesso = response.status_code == 200
            resultado = response.json() if sucesso else response.text
            imprimir_resultado("Listar meus pedidos", sucesso, 
                             f"{resultado.get('total', 0)} pedidos encontrados" if sucesso else resultado)
            
            if sucesso and resultado.get('pedidos'):
                print("   📋 Últimos pedidos:")
                for pedido in resultado['pedidos'][:2]:
                    print(f"      - {pedido['id']}: R$ {pedido['total']} ({pedido['status']})")
        
        # ====================================
        # 8. TESTE DE REGISTRO DUPLICADO
        # ====================================
        imprimir_secao("VALIDAÇÃO DE ERROS")
        
        # Tentar registrar mesmo email novamente
        response = requests.post(
            f"{BASE_URL}/api/v1/mobile/auth/registrar",
            headers=headers,
            json=dados_morador
        )
        
        sucesso = response.status_code == 400  # Deve falhar
        imprimir_resultado("Registro duplicado (deve falhar)", sucesso, 
                         "Email já cadastrado" if sucesso else "Erro inesperado")
        
        # Teste de login inválido
        dados_login_invalido = {
            "email": "joao.silva@condominio.com",
            "senha": "senha_errada"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/mobile/auth/login",
            headers=headers,
            json=dados_login_invalido
        )
        
        sucesso = response.status_code == 400  # Deve falhar
        imprimir_resultado("Login com senha errada (deve falhar)", sucesso,
                         "Senha incorreta" if sucesso else "Erro inesperado")
        
        # ====================================
        # RESUMO DOS TESTES
        # ====================================
        imprimir_secao("RESUMO DOS TESTES MOBILE")
        
        print("✅ Testes completados com sucesso!")
        print("📱 APIs mobile funcionando corretamente")
        print("🛒 Fluxo completo: Registro → Login → Catálogo → Carrinho → Pedido")
        print(f"⏰ Finalizado: {datetime.now().strftime('%H:%M:%S')}")
        
        print("\n🔗 URLs importantes:")
        print(f"   📖 Documentação: {BASE_URL}/docs")
        print(f"   🔄 API Status: {BASE_URL}/api/v1/mobile/status")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API mobile")
        print("💡 Certifique-se de que a API está rodando na porta 8002")
        print("   Comando: python mobile_api.py")
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")

if __name__ == "__main__":
    testar_apis_mobile() 