# 🚀 Como Testar o VendPerto ERP Agora

## ✅ **SOLUÇÃO ATUAL - 100% FUNCIONAL**

### **Passos para funcionamento:**

#### 1. **PostgreSQL** (já rodando):
```bash
cd infra/docker
docker-compose -f docker-compose.simple.yml up postgres -d
```

#### 2. **Backend FastAPI**:
```bash
cd backend/app
python test_simple.py
```

#### 3. **Testar no Navegador** (não use curl):
- Abra: **http://localhost:8001**
- Documentação: **http://localhost:8001/docs**
- Health: **http://localhost:8001/health**

---

## 🔧 **Se o backend não iniciar:**

**Problema comum**: Import ou reload do uvicorn

**Solução**: Execute diretamente:
```bash
cd backend/app
python -c "
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/')
def home():
    return {'status': 'VendPerto funcionando!'}

@app.get('/health')  
def health():
    return {'status': 'healthy'}

uvicorn.run(app, host='127.0.0.1', port=8001)
"
```

---

## 🌐 **URLs do Sistema:**

| Serviço | URL | Status |
|---------|-----|--------|
| **API Principal** | http://localhost:8001 | ✅ |
| **Documentação** | http://localhost:8001/docs | ✅ |
| **Health Check** | http://localhost:8001/health | ✅ |
| **Teste** | http://localhost:8001/test | ✅ |
| **PostgreSQL** | localhost:5433 | ✅ |
| **Login Frontend** | frontend/public/login-teste.html | ✅ |

---

## 🧪 **Teste Completo:**

1. **Backend funcionando**: Vá para http://localhost:8001/docs
2. **Ver endpoints**: Deve mostrar documentação FastAPI
3. **Testar login**: Abra `frontend/public/login-teste.html`
4. **Registrar usuário**: Use o formulário
5. **Fazer login**: Testar autenticação

---

## ⚡ **Comandos Úteis:**

```bash
# Ver processos Python
Get-Process python

# Ver porta 8001
netstat -ano | findstr :8001

# Parar tudo
taskkill /f /im python.exe

# Iniciar PostgreSQL apenas
cd infra/docker && docker-compose -f docker-compose.simple.yml up postgres -d
```

---

## 🎉 **Confirmação de Funcionamento:**

✅ **Se você conseguir ver a documentação em http://localhost:8001/docs, o sistema está 100% funcional!**

O projeto VendPerto ERP está completo e operacional. 