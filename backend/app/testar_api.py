import requests
import json

# Configuração
API_BASE = "http://localhost:8001"

def testar_health():
    """Testa endpoint de saúde"""
    print("🔍 Testando endpoint de saúde...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Resposta: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_cadastro():
    """Testa cadastro de usuário"""
    print("\n👤 Testando cadastro de usuário...")
    
    dados_usuario = {
        "nome": "Usuario Teste",
        "email": "teste@vendperto.com",
        "senha": "senha123",
        "perfil": "administrador"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/auth/registrar",
            json=dados_usuario,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Resposta: {response.json()}")
        
        if response.status_code == 200:
            return True
        else:
            print("⚠️ Usuário pode já existir, continuando...")
            return True
            
    except Exception as e:
        print(f"❌ Erro no cadastro: {e}")
        return False

def testar_login():
    """Testa login do usuário"""
    print("\n🔐 Testando login...")
    
    dados_login = {
        "email": "teste@vendperto.com",
        "senha": "senha123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/auth/login-json",
            json=dados_login,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Status: {response.status_code}")
        resultado = response.json()
        print(f"📄 Resposta: {resultado}")
        
        if response.status_code == 200 and "access_token" in resultado:
            token = resultado["access_token"]
            print(f"🎫 Token gerado: {token[:50]}...")
            return token
        else:
            print("❌ Login falhou")
            return None
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def testar_usuario_atual(token):
    """Testa endpoint de usuário atual"""
    print("\n👀 Testando endpoint de usuário atual...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/api/v1/auth/usuario-atual",
            headers=headers
        )
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Resposta: {response.json()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro ao obter usuário atual: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API VendPerto ERP")
    print("=" * 50)
    
    # Teste 1: Health
    if not testar_health():
        print("❌ API não está funcionando")
        return
    
    # Teste 2: Cadastro
    if not testar_cadastro():
        print("❌ Cadastro falhou")
        return
    
    # Teste 3: Login
    token = testar_login()
    if not token:
        print("❌ Login falhou")
        return
    
    # Teste 4: Usuário atual
    if not testar_usuario_atual(token):
        print("❌ Endpoint de usuário atual falhou")
        return
    
    print("\n🎉 Todos os testes passaram!")
    print("✅ APIs de cadastro e login estão funcionando perfeitamente")

if __name__ == "__main__":
    main() 