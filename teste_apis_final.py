import requests
import json

# Configuração
API_BASE = "http://localhost:8001"

def testar_cadastro_usuario():
    """Testa cadastro de usuário"""
    print("👤 Testando cadastro de usuário...")
    
    dados_usuario = {
        "nome": "Cliente Teste",
        "email": "cliente@vendperto.com",
        "senha": "senha123",
        "perfil": "cliente"
    }
    
    response = requests.post(
        f"{API_BASE}/api/v1/auth/registrar",
        json=dados_usuario
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    return response.status_code == 200

def testar_login():
    """Testa login do usuário"""
    print("\n🔐 Testando login...")
    
    dados_login = {
        "email": "cliente@vendperto.com",
        "senha": "senha123"
    }
    
    response = requests.post(
        f"{API_BASE}/api/v1/auth/login-json",
        json=dados_login
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    return response.status_code == 200

def testar_cadastro_produtos():
    """Testa cadastro de produtos"""
    print("\n📦 Testando cadastro de produtos...")
    
    produtos = [
        {
            "nome": "Smartphone Galaxy",
            "descricao": "Celular Samsung Galaxy com 128GB",
            "preco": 1299.99,
            "categoria": "eletrônicos",
            "estoque": 10
        },
        {
            "nome": "Notebook Dell",
            "descricao": "Notebook Dell Inspiron 15 polegadas",
            "preco": 2499.99,
            "categoria": "informática",
            "estoque": 5
        },
        {
            "nome": "Fone Bluetooth",
            "descricao": "Fone de ouvido sem fio Bluetooth",
            "preco": 199.99,
            "categoria": "eletrônicos",
            "estoque": 20
        }
    ]
    
    for produto in produtos:
        response = requests.post(
            f"{API_BASE}/api/v1/produtos/cadastrar",
            json=produto
        )
        print(f"Produto: {produto['nome']} - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ {response.json()['mensagem']}")
        else:
            print(f"  ❌ Erro: {response.text}")
    
    return True

def testar_listar_produtos():
    """Testa listagem de produtos"""
    print("\n📋 Testando listagem de produtos...")
    
    response = requests.get(f"{API_BASE}/api/v1/produtos/listar")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total de produtos: {data['total']}")
        for produto in data['produtos']:
            print(f"  • {produto['nome']} - R$ {produto['preco']} (Estoque: {produto['estoque']})")
    
    return response.status_code == 200

def testar_venda():
    """Testa realização de venda"""
    print("\n💰 Testando realização de venda...")
    
    dados_venda = {
        "cliente_email": "cliente@vendperto.com",
        "itens": [
            {
                "produto_id": 1,
                "quantidade": 2
            },
            {
                "produto_id": 3,
                "quantidade": 1
            }
        ]
    }
    
    response = requests.post(
        f"{API_BASE}/api/v1/vendas/realizar",
        json=dados_venda
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        resultado = response.json()
        print(f"✅ {resultado['mensagem']}")
        print(f"Total da venda: R$ {resultado['dados']['total']}")
        print(f"Número de itens: {resultado['dados']['itens']}")
    else:
        print(f"❌ Erro: {response.text}")
    
    return response.status_code == 200

def testar_estoque_apos_venda():
    """Verifica estoque após venda"""
    print("\n📊 Verificando estoque após venda...")
    
    response = requests.get(f"{API_BASE}/api/v1/produtos/listar")
    
    if response.status_code == 200:
        data = response.json()
        print("Estoque atualizado:")
        for produto in data['produtos']:
            print(f"  • {produto['nome']} - Estoque: {produto['estoque']}")
    
    return response.status_code == 200

def testar_historico_vendas():
    """Testa histórico de vendas"""
    print("\n📈 Testando histórico de vendas...")
    
    response = requests.get(f"{API_BASE}/api/v1/vendas/listar")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total de vendas: {data['total']}")
        for venda in data['vendas']:
            print(f"  • Venda #{venda['id']} - Cliente: {venda['cliente_nome']} - Total: R$ {venda['total']}")
    
    return response.status_code == 200

def testar_vendas_por_cliente():
    """Testa vendas por cliente"""
    print("\n👤 Testando vendas por cliente...")
    
    response = requests.get(f"{API_BASE}/api/v1/vendas/cliente/cliente@vendperto.com")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Vendas do cliente: {data['total']}")
        for venda in data['vendas']:
            print(f"  • Data: {venda['data_venda']} - Total: R$ {venda['total']}")
    
    return response.status_code == 200

def main():
    """Executa todos os testes"""
    print("🚀 TESTANDO SISTEMA COMPLETO VENDPERTO ERP")
    print("=" * 50)
    
    testes = [
        ("Cadastro de usuário", testar_cadastro_usuario),
        ("Login", testar_login),
        ("Cadastro de produtos", testar_cadastro_produtos),
        ("Listagem de produtos", testar_listar_produtos),
        ("Realização de venda", testar_venda),
        ("Estoque após venda", testar_estoque_apos_venda),
        ("Histórico de vendas", testar_historico_vendas),
        ("Vendas por cliente", testar_vendas_por_cliente)
    ]
    
    sucessos = 0
    total = len(testes)
    
    for nome, teste in testes:
        try:
            if teste():
                sucessos += 1
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏆 RESULTADO FINAL: {sucessos}/{total} testes passaram")
    
    if sucessos == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main() 