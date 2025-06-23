# Contexto Técnico - API VendPerto

## Stack Tecnológico Definido

### Backend
```python
# Framework Principal
FastAPI 0.104+  # Framework web moderno e rápido
Uvicorn         # Servidor ASGI

# Banco de Dados
PostgreSQL 15+  # Banco principal
SQLAlchemy 2.0+ # ORM
Alembic         # Migrações

# Autenticação & Segurança
python-jose     # JWT tokens
passlib         # Hash de senhas
bcrypt          # Algoritmo de hash

# Validação & Serialização
Pydantic 2.0+   # Validação de dados
email-validator # Validação de emails

# Utilitários
python-multipart # Upload de arquivos
python-dotenv   # Variáveis de ambiente
```

### Frontend
```javascript
// Framework Principal
React 18+       // Interface de usuário
React Router    // Roteamento
Axios          // Cliente HTTP

// UI/UX
Material-UI     // Componentes (a confirmar)
// ou
Tailwind CSS   // Utilitários CSS (a confirmar)

// Estado
Context API    // Gerenciamento de estado
// ou
Zustand       // Estado global (a avaliar)

// Formulários
React Hook Form // Manipulação de formulários
Yup            // Validação de schemas
```

### Infraestrutura
```yaml
# Containerização
Docker 24+     # Containerização
Docker Compose # Orquestração local

# Proxy & Load Balancer
Nginx 1.24+    # Proxy reverso

# Monitoramento (Futuro)
Prometheus     # Métricas
Grafana        # Dashboards
Jaeger         # Tracing distribuído

# CI/CD (a definir)
GitHub Actions # Pipeline de deploy
```

## Configuração de Ambiente

### Ambiente de Desenvolvimento
```bash
# Python
Python 3.11+
pip 23+
virtualenv

# Node.js
Node.js 18+
npm 9+ ou yarn 1.22+

# Banco de Dados
PostgreSQL 15+ (local ou remoto)
```

### Ambiente de Produção
```bash
# Servidor
Ubuntu 22.04 LTS ou similar
Docker Engine 24+
Docker Compose 2.0+

# Banco de Dados
PostgreSQL 15+ (gerenciado)
Conexão SSL obrigatória

# Domínio
ambientedeteste.dev (configurado)
SSL/TLS com Let's Encrypt
```

## Configurações de Banco de Dados

### PostgreSQL (CONFIGURADO)
```env
# Conexão Principal
DB_HOST=5.161.218.248
DB_PORT=5432
DB_NAME=vendperto
DB_PASSWORD=nxq8n8m0qh7lnrqz
DB_USER=vendperto  # (assumido)

# Configurações de Pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

### Schema Inicial Planejado
```sql
-- Tabelas principais
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(11) UNIQUE,
    perfil VARCHAR(50) NOT NULL DEFAULT 'operador',
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT NOW(),
    data_atualizacao TIMESTAMP DEFAULT NOW()
);

CREATE TABLE produto (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    categoria_id INTEGER,
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT NOW(),
    data_atualizacao TIMESTAMP DEFAULT NOW()
);

CREATE TABLE estoque (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER REFERENCES produto(id),
    quantidade INTEGER NOT NULL DEFAULT 0,
    minimo INTEGER DEFAULT 0,
    data_atualizacao TIMESTAMP DEFAULT NOW()
);
```

## Constraints Técnicas Identificadas

### Performance
- **Resposta da API**: < 200ms para 95% das requisições
- **Concorrência**: Suporte a 100+ usuários simultâneos
- **Banco de Dados**: Queries otimizadas com índices apropriados

### Segurança
- **HTTPS**: Obrigatório em produção
- **JWT**: Expiração de 24h, refresh tokens
- **Validação**: Todas as entradas validadas
- **SQL Injection**: Prevenção via ORM

### Escalabilidade
- **Horizontal**: Múltiplas instâncias da API
- **Vertical**: Otimização de recursos
- **Cache**: Redis para sessões (futuro)

## Dependências Externas

### Obrigatórias
1. **PostgreSQL**: Banco de dados principal
2. **Cloudflare**: DNS e CDN (mencionado pelo usuário)
3. **ambientedeteste.dev**: Domínio de teste

### Opcionais (Futuro)
1. **Redis**: Cache e sessões
2. **S3**: Armazenamento de arquivos
3. **SendGrid**: Envio de emails
4. **Stripe**: Processamento de pagamentos

## Configurações de Desenvolvimento

### Estrutura de .env
```env
# Aplicação
APP_NAME=VendPerto ERP
APP_ENV=development
DEBUG=True
SECRET_KEY=sua_chave_super_secreta_aqui

# Banco de Dados
DATABASE_URL=postgresql://user:pass@host:port/db

# JWT
JWT_SECRET=jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "https://ambientedeteste.dev"]

# Logs
LOG_LEVEL=INFO
LOG_FILE=logs/vendperto.log
```

### Scripts de Desenvolvimento
```bash
# Backend
./scripts/dev-backend.sh    # Inicia API em modo dev
./scripts/test-backend.sh   # Roda testes
./scripts/migrate.sh        # Aplica migrações

# Frontend  
./scripts/dev-frontend.sh   # Inicia React em modo dev
./scripts/build-frontend.sh # Build de produção

# Completo
./scripts/dev-full.sh       # Inicia stack completa
```

## Configurações de Produção

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - APP_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db
      
  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=${API_URL}
      
  nginx:
    image: nginx:alpine
    volumes:
      - ./infra/nginx/nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
```

### Monitoramento Básico
```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

# Métricas básicas
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    return response
```

## Próximas Decisões Técnicas

### Urgentes (Esta Semana):
1. Framework CSS (Material-UI vs Tailwind)
2. Configuração de logs estruturados
3. Estratégia de cache (memória vs Redis)

### Médio Prazo (Próximo Mês):
1. Ferramenta de monitoramento
2. Pipeline de CI/CD
3. Estratégia de backup

### Longo Prazo (3+ Meses):
1. Microserviços vs Monolítico
2. Kubernetes vs Docker Swarm
3. Multi-tenancy 