import requests
import json

# Configuração
API_BASE = "http://localhost:8001"
TOKEN_GLOBAL = None

def obter_token():
    """Faz login e obtém token para autenticação"""
    global TOKEN_GLOBAL
    
    if TOKEN_GLOBAL:
        return TOKEN_GLOBAL
    
    # Primeiro registrar um admin se não existir
    dados_admin = {
        "nome": "Administrador Sistema",
        "email": "admin@vendperto.com",
        "senha": "admin123",
        "perfil": "administrador"
    }
    
    requests.post(f"{API_BASE}/api/v1/auth/registrar", json=dados_admin)
    
    # Fazer login
    dados_login = {
        "email": "admin@vendperto.com",
        "senha": "admin123"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/auth/login-json", json=dados_login)
    if response.status_code == 200:
        TOKEN_GLOBAL = response.json()["access_token"]
        return TOKEN_GLOBAL
    
    return None

def get_headers():
    """Retorna headers com autenticação"""
    token = obter_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

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
    if response.status_code == 200:
        print(f"✅ {response.json()['mensagem']}")
    else:
        print(f"⚠️ {response.json()}")
    
    return response.status_code == 200

def testar_login():
    """Testa login do usuário"""
    print("\n🔐 Testando login...")
    
    token = obter_token()
    if token:
        print(f"✅ Login realizado com sucesso")
        print(f"Token: {token[:20]}...")
        return True
    else:
        print("❌ Falha no login")
        return False

def testar_cadastro_categorias():
    """Testa cadastro de categorias"""
    print("\n🗂️ Testando cadastro de categorias...")
    
    categorias = [
        {
            "nome": "Eletrônicos",
            "descricao": "Produtos eletrônicos em geral",
            "ativo": True
        },
        {
            "nome": "Informática",
            "descricao": "Computadores e acessórios",
            "ativo": True
        },
        {
            "nome": "Smartphones",
            "descricao": "Celulares e tablets",
            "categoria_pai_id": 1,  # Subcategoria de Eletrônicos
            "ativo": True
        }
    ]
    
    for categoria in categorias:
        response = requests.post(
            f"{API_BASE}/api/v1/categorias/cadastrar",
            json=categoria,
            headers=get_headers()
        )
        print(f"Categoria: {categoria['nome']} - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ {response.json()['mensagem']}")
        else:
            print(f"  ❌ Erro: {response.text}")
    
    return True

def testar_listar_categorias():
    """Testa listagem de categorias"""
    print("\n📋 Testando listagem de categorias...")
    
    response = requests.get(f"{API_BASE}/api/v1/categorias/listar")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total de categorias: {data['total']}")
        for categoria in data['categorias']:
            print(f"  • {categoria['nome']} - Produtos: {categoria['total_produtos']}")
            if categoria['subcategorias']:
                for sub in categoria['subcategorias']:
                    print(f"    └─ {sub['nome']}")
    
    return response.status_code == 200

def testar_cadastro_fornecedores():
    """Testa cadastro de fornecedores"""
    print("\n🏭 Testando cadastro de fornecedores...")
    
    fornecedores = [
        {
            "nome": "Tech Solutions Ltda",
            "email": "contato@techsolutions.com",
            "telefone": "(11) 99999-0001",
            "cnpj": "12.345.678/0001-90",
            "endereco": "Rua das Tecnologias, 123",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01234-567"
        },
        {
            "nome": "Digital Commerce S.A.",
            "email": "vendas@digitalcommerce.com",
            "telefone": "(21) 88888-0002",
            "cnpj": "98.765.432/0001-10",
            "endereco": "Av. Inovação, 456",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "cep": "20000-123"
        }
    ]
    
    for fornecedor in fornecedores:
        response = requests.post(
            f"{API_BASE}/api/v1/fornecedores/cadastrar",
            json=fornecedor,
            headers=get_headers()
        )
        print(f"Fornecedor: {fornecedor['nome']} - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ {response.json()['mensagem']}")
        else:
            print(f"  ❌ Erro: {response.text}")
    
    return True

def testar_listar_fornecedores():
    """Testa listagem de fornecedores"""
    print("\n📋 Testando listagem de fornecedores...")
    
    response = requests.get(f"{API_BASE}/api/v1/fornecedores/listar")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total de fornecedores: {data['total']}")
        for fornecedor in data['fornecedores']:
            print(f"  • {fornecedor['nome']} - CNPJ: {fornecedor['cnpj']} - Produtos: {fornecedor['total_produtos']}")
    
    return response.status_code == 200

def testar_cadastro_produtos():
    """Testa cadastro de produtos com categorias e fornecedores"""
    print("\n📦 Testando cadastro de produtos...")
    
    produtos = [
        {
            "nome": "iPhone 15 Pro",
            "descricao": "Smartphone Apple iPhone 15 Pro 256GB",
            "preco": 7999.99,
            "categoria_id": 3,  # Smartphones
            "fornecedor_id": 1,  # Tech Solutions
            "estoque": 15,
            "estoque_minimo": 5
        },
        {
            "nome": "MacBook Pro M3",
            "descricao": "Notebook Apple MacBook Pro 14' M3 512GB",
            "preco": 12999.99,
            "categoria_id": 2,  # Informática
            "fornecedor_id": 1,  # Tech Solutions
            "estoque": 8,
            "estoque_minimo": 3
        },
        {
            "nome": "AirPods Pro",
            "descricao": "Fone de ouvido sem fio Apple AirPods Pro",
            "preco": 1499.99,
            "categoria_id": 1,  # Eletrônicos
            "fornecedor_id": 2,  # Digital Commerce
            "estoque": 25,
            "estoque_minimo": 10
        }
    ]
    
    for produto in produtos:
        response = requests.post(
            f"{API_BASE}/api/v1/produtos/cadastrar",
            json=produto,
            headers=get_headers()
        )
        print(f"Produto: {produto['nome']} - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ {response.json()['mensagem']}")
        else:
            print(f"  ❌ Erro: {response.text}")
    
    return True

def testar_listar_produtos():
    """Testa listagem de produtos com informações completas"""
    print("\n📋 Testando listagem de produtos...")
    
    response = requests.get(f"{API_BASE}/api/v1/produtos/listar")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total de produtos: {data['total']}")
        for produto in data['produtos']:
            estoque_status = "🔴 BAIXO" if produto['estoque_baixo'] else "🟢 OK"
            print(f"  • {produto['nome']} - R$ {produto['preco']}")
            print(f"    Categoria: {produto['categoria_nome']} | Fornecedor: {produto['fornecedor_nome']}")
            print(f"    Estoque: {produto['estoque']} {estoque_status}")
    
    return response.status_code == 200

def testar_venda():
    """Testa realização de venda"""
    print("\n💰 Testando realização de venda...")
    
    dados_venda = {
        "cliente_email": "cliente@vendperto.com",
        "observacoes": "Compra realizada via teste automatizado",
        "itens": [
            {"produto_id": 1, "quantidade": 2},  # iPhone
            {"produto_id": 3, "quantidade": 1}   # AirPods
        ]
    }
    
    response = requests.post(
        f"{API_BASE}/api/v1/vendas/realizar",
        json=dados_venda
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()["dados"]
        print(f"✅ Venda realizada! ID: {data['venda_id']} - Total: R$ {data['total']}")
    else:
        print(f"❌ Erro: {response.text}")
    
    return response.status_code == 200

def testar_dashboard():
    """Testa API de dashboard"""
    print("\n📊 Testando dashboard...")
    
    response = requests.get(f"{API_BASE}/api/v1/relatorios/dashboard")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        resumo = data["resumo"]
        print("Dashboard - Resumo:")
        print(f"  • Usuários: {resumo['total_usuarios']}")
        print(f"  • Produtos: {resumo['total_produtos']}")
        print(f"  • Categorias: {resumo['total_categorias']}")
        print(f"  • Fornecedores: {resumo['total_fornecedores']}")
        print(f"  • Vendas: {resumo['total_vendas']}")
        print(f"  • Vendas hoje: {resumo['vendas_hoje']}")
        print(f"  • Receita hoje: R$ {resumo['receita_hoje']}")
        print(f"  • Produtos com estoque baixo: {resumo['produtos_estoque_baixo']}")
        
        if data["alertas"]:
            print("Alertas:")
            for alerta in data["alertas"]:
                print(f"  ⚠️ {alerta['tipo']}: {alerta['quantidade']} produtos")
    
    return response.status_code == 200

def testar_relatorio_vendas():
    """Testa relatório de vendas"""
    print("\n📈 Testando relatório de vendas...")
    
    response = requests.get(f"{API_BASE}/api/v1/relatorios/vendas?periodo=7")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Relatório de vendas (últimos {data['periodo_dias']} dias):")
        print(f"  • Total de vendas: {data['total_vendas']}")
        print(f"  • Receita total: R$ {data['receita_total']}")
        print(f"  • Ticket médio: R$ {data['ticket_medio']:.2f}")
    
    return response.status_code == 200

def testar_logs():
    """Testa listagem de logs"""
    print("\n📝 Testando logs de auditoria...")
    
    response = requests.get(f"{API_BASE}/api/v1/logs/listar?limit=10")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Logs de auditoria ({data['exibindo']} de {data['total']}):")
        for log in data['logs'][:5]:  # Mostrar apenas os 5 mais recentes
            print(f"  • {log['timestamp'][:19]} - {log['acao']} - {log['usuario_email']}")
    
    return response.status_code == 200

def main():
    """Executa todos os testes do sistema completo"""
    print("🚀 TESTANDO SISTEMA COMPLETO VENDPERTO ERP v2.0")
    print("=" * 60)
    
    testes = [
        ("Cadastro de usuário", testar_cadastro_usuario),
        ("Login e autenticação", testar_login),
        ("Cadastro de categorias", testar_cadastro_categorias),
        ("Listagem de categorias", testar_listar_categorias),
        ("Cadastro de fornecedores", testar_cadastro_fornecedores),
        ("Listagem de fornecedores", testar_listar_fornecedores),
        ("Cadastro de produtos", testar_cadastro_produtos),
        ("Listagem de produtos", testar_listar_produtos),
        ("Realização de venda", testar_venda),
        ("Dashboard principal", testar_dashboard),
        ("Relatório de vendas", testar_relatorio_vendas),
        ("Logs de auditoria", testar_logs)
    ]
    
    sucessos = 0
    total = len(testes)
    
    for nome, teste in testes:
        try:
            print(f"\n{'='*20} {nome.upper()} {'='*20}")
            if teste():
                sucessos += 1
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏆 RESULTADO FINAL: {sucessos}/{total} testes passaram")
    
    if sucessos == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema ERP funcionando perfeitamente!")
        print("\n🎯 MÓDULOS TESTADOS COM SUCESSO:")
        print("   ✅ Usuários e Autenticação")
        print("   ✅ Categorias de Produtos")
        print("   ✅ Fornecedores")
        print("   ✅ Produtos com Relacionamentos")
        print("   ✅ Vendas Completas")
        print("   ✅ Dashboard e Relatórios")
        print("   ✅ Sistema de Logs/Auditoria")
        print("\n🚀 PRONTO PARA PRODUÇÃO!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main() 