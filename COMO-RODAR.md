# 🚀 Como Rodar o VendPerto ERP

## Pré-requisitos
- Docker e Docker Compose instalados
- Git (para clonar o repositório)

## 🔥 Início Rápido

### 1. Iniciar o Backend
```bash
# Windows PowerShell
cd infra\docker
docker-compose up --build -d

# Linux/Mac
chmod +x infra/scripts/dev-backend.sh
./infra/scripts/dev-backend.sh
```

### 2. Verificar se está funcionando
- 🔗 **API**: http://localhost:8000
- 📚 **Documentação Swagger**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc
- 💾 **PostgreSQL**: localhost:5433

### 3. Testar a página de login
Abra no navegador: `frontend/public/login-teste.html`

## 🧪 Testes Automatizados

### Linux/Mac:
```bash
chmod +x infra/scripts/testar-api.sh
./infra/scripts/testar-api.sh
```

### Windows:
```powershell
# Teste manual com curl
curl http://localhost:8000/health
```

## 📊 Monitoramento

### Ver logs:
```bash
cd infra/docker
docker-compose logs -f backend
```

### Parar serviços:
```bash
cd infra/docker
docker-compose down
```

## 🔧 Endpoints Disponíveis

### Autenticação
- `POST /api/v1/auth/registrar` - Registrar usuário
- `POST /api/v1/auth/login` - Login (form-data)
- `POST /api/v1/auth/login-json` - Login (JSON)
- `GET /api/v1/auth/usuario-atual` - Dados do usuário logado

### Outros
- `GET /health` - Status da aplicação
- `GET /` - Redireciona para documentação

## 🔑 Dados de Teste

### Usuário padrão (será criado no primeiro teste):
- **Email**: `teste@vendperto.com`
- **Senha**: `senha123`
- **Perfil**: `administrador`

## 🐛 Resolução de Problemas

### Backend não inicia:
1. Verificar se Docker está rodando
2. Verificar se porta 8000 está livre
3. Ver logs: `docker-compose logs backend`

### Erro de conexão com banco:
1. Verificar se PostgreSQL container está rodando
2. Aguardar alguns segundos para o banco inicializar
3. Ver logs: `docker-compose logs postgres`

### CORS/Frontend:
- A página `login-teste.html` deve ser aberta direto no navegador (file://)
- Para desenvolvimento web, usar um servidor local (Live Server, etc.)

## 📁 Estrutura do Projeto

```
apiVendperto/
├── backend/                 # API FastAPI
│   ├── app/                 # Código da aplicação
│   └── requirements.txt     # Dependências Python
├── frontend/                # Interface (placeholder)
│   └── public/              # Arquivos estáticos
├── infra/                   # Infraestrutura
│   ├── docker/              # Containers
│   └── scripts/             # Scripts utilitários
└── memory-bank/             # Documentação do projeto
```

## 🌐 Deploy com Traefik (Produção)

### Configuração para ambientedeteste.dev

O projeto já vem configurado com **Traefik** para deploy em produção:

#### URLs disponíveis:
- 🌐 **Frontend**: https://ambientedeteste.dev
- 🔌 **API**: https://api.ambientedeteste.dev  
- 📖 **Documentação**: https://api.ambientedeteste.dev/docs
- 🔧 **Dashboard Traefik**: https://traefik.ambientedeteste.dev (só desenvolvimento)

#### Deploy em produção:
```bash
# Linux/Mac
./infra/scripts/deploy-prod.sh

# Windows
cd infra/docker
docker-compose -f docker-compose.prod.yml up --build -d
```

#### Ver logs de produção:
```bash
# Linux/Mac
./infra/scripts/logs-prod.sh

# Windows
cd infra/docker
docker-compose -f docker-compose.prod.yml logs -f
```

### ⚠️ Antes do deploy:
1. **Configurar DNS**: Apontar os domínios para o servidor
   - `ambientedeteste.dev` → IP do servidor
   - `api.ambientedeteste.dev` → IP do servidor
   - `traefik.ambientedeteste.dev` → IP do servidor

2. **Configurar Cloudflare**: Para certificados SSL automáticos

3. **Verificar banco**: Conexão com PostgreSQL remoto (5.161.218.248:5432)

### 🛡️ Segurança Traefik:
- ✅ SSL/TLS automático (Let's Encrypt)
- ✅ Redirect HTTP → HTTPS
- ✅ Headers de segurança
- ✅ Rate limiting
- ✅ CORS configurado
- ✅ Compressão gzip

## 🎯 Próximos Passos

Após confirmar que tudo está funcionando:

1. ✅ **Implementar frontend React** completo
2. ✅ **Adicionar módulos** (estoque, vendas, financeiro)  
3. ✅ **Implementar testes** unitários e integração
4. ✅ **Configurar CI/CD**
5. ✅ **Deploy** em produção com Traefik

---

💡 **Dica**: Use a documentação automática em `/docs` para testar os endpoints!