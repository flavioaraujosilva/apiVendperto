# VendPerto ERP

Sistema ERP moderno, escalável e robusto construído com Python FastAPI e React, seguindo princípios de System Design para alta disponibilidade, performance e manutenibilidade.

## 🎯 Visão Geral

O VendPerto ERP é uma solução completa para gestão empresarial, desenvolvida especificamente para pequenas e médias empresas brasileiras. O sistema oferece módulos integrados de vendas, estoque, financeiro e relatórios, com interface moderna e intuitiva.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│                /login /dashboard /financeiro            │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                 API GATEWAY (FastAPI)                   │
│              /api/v1/* endpoints                        │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                CAMADA DE INFRAESTRUTURA                 │
│         PostgreSQL | Redis | Logs | Monitoramento      │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados principal
- **SQLAlchemy** - ORM
- **Alembic** - Migrações de banco
- **Pydantic** - Validação de dados
- **JWT** - Autenticação

### Frontend
- **React 18+** - Interface de usuário
- **React Router** - Roteamento
- **Axios** - Cliente HTTP
- **Material-UI/Tailwind** - Interface (a definir)

### Infraestrutura
- **Docker** - Containerização
- **Nginx** - Proxy reverso
- **Docker Compose** - Orquestração

## 📁 Estrutura do Projeto

```
apiVendperto/
│
├── frontend/                    # Aplicação React
│   ├── src/
│   │   ├── componentes/        # Componentes reutilizáveis
│   │   ├── paginas/            # Páginas da aplicação
│   │   │   ├── login/          # Página de login
│   │   │   ├── dashboard/      # Dashboard principal
│   │   │   └── financeiro/     # Módulo financeiro
│   │   ├── servicos/           # Chamadas para API
│   │   ├── contextos/          # Context API
│   │   └── utils/              # Utilitários
│   └── public/
│
├── backend/                     # API FastAPI
│   ├── app/
│   │   ├── api/v1/             # Endpoints versionados
│   │   │   ├── auth/           # Autenticação
│   │   │   ├── usuarios/       # Gestão de usuários
│   │   │   ├── estoque/        # Controle de estoque
│   │   │   └── vendas/         # Módulo de vendas
│   │   ├── core/               # Configurações centrais
│   │   ├── modelos/            # Modelos do banco
│   │   ├── esquemas/           # Pydantic schemas
│   │   ├── servicos/           # Lógica de negócio
│   │   └── repositorios/       # Acesso a dados
│   ├── tests/                  # Testes automatizados
│   └── alembic/                # Migrações
│
├── infra/                      # Infraestrutura
│   ├── docker/                 # Dockerfiles
│   ├── nginx/                  # Configuração Nginx
│   └── scripts/                # Scripts de deploy
│
├── docs/                       # Documentação
│   ├── api/                    # Documentação da API
│   ├── arquitetura/            # Diagramas de arquitetura
│   └── manuais/                # Manuais de usuário
│
└── memory-bank/                # Memory Bank do projeto
    ├── regras.md              # Regras fundamentais
    ├── projectbrief.md        # Escopo do projeto
    └── ... (outros arquivos)
```

## ⚙️ Configuração do Ambiente

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker 24+

### Banco de Dados (Configurado)
```env
Host: 5.161.218.248
Porta: 5432
Database: vendperto
```

### Ambiente de Teste
- **URL**: ambientedeteste.dev
- **SSL**: Configurado via Cloudflare

## 🎯 Objetivos Principais

### 1. **Modularidade**
- Arquitetura baseada em microsserviços modulares
- Componentes independentes e desacoplados

### 2. **Escalabilidade**
- Horizontal scaling com load balancing
- Suporte a crescimento de usuários e dados

### 3. **Observabilidade**
- Monitoramento completo do sistema
- Logs estruturados e centralizados

### 4. **Segurança**
- RBAC/ABAC (Role/Attribute Based Access Control)
- Autenticação robusta com JWT

### 5. **Performance**
- Resposta < 200ms para 95% das requisições
- Otimizações de banco de dados

## 📋 Fases de Desenvolvimento

### 🔄 FASE 1 - MVP Login (EM ANDAMENTO)
- [x] Estrutura completa do projeto
- [x] Documentação e planejamento
- [ ] API de autenticação
- [ ] Página de login funcional
- [ ] Conexão com PostgreSQL

### 📊 FASE 2 - Dashboard & Usuários
- [ ] Dashboard executivo
- [ ] Gestão completa de usuários
- [ ] Sistema de permissões

### 📦 FASE 3 - Controle de Estoque
- [ ] Cadastro de produtos
- [ ] Movimentações de estoque
- [ ] Relatórios de estoque

### 💰 FASE 4 - Módulo de Vendas
- [ ] Cadastro de clientes
- [ ] Processamento de pedidos
- [ ] Faturamento

### 📈 FASE 5 - Módulo Financeiro
- [ ] Contas a pagar/receber
- [ ] Fluxo de caixa
- [ ] Relatórios financeiros

## 🔧 Convenções de Desenvolvimento

### Nomenclatura (OBRIGATÓRIO: Português Brasileiro)
```python
# ✅ CORRETO
def validarCpf(cpf: str) -> bool:
def criarUsuario(dados: dict) -> Usuario:
def obterProdutoPorId(produto_id: int) -> Produto:

# ❌ INCORRETO
def validateCpf(cpf: str) -> bool:
def createUser(data: dict) -> User:
```

### Rotas da API
```
/api/v1/auth/login          # Login
/api/v1/auth/registrar      # Registro
/api/v1/usuarios/           # Gestão de usuários
/api/v1/estoque/            # Controle de estoque
/api/v1/vendas/             # Módulo de vendas
```

## 📚 Documentação

- **Memory Bank**: Documentação completa em `memory-bank/`
- **API Docs**: Documentação automática via ReDoc
- **Arquitetura**: Diagramas em `docs/arquitetura/`

## 🔒 Segurança

- HTTPS obrigatório em produção
- JWT com expiração de 24h
- Validação rigorosa de todas as entradas
- Logs de auditoria completos

## 🚀 Deploy

### Desenvolvimento
```bash
# Iniciar stack completa
docker-compose up -d

# Backend apenas
cd backend && uvicorn app.main:app --reload

# Frontend apenas  
cd frontend && npm run dev
```

### Produção
- Deploy automatizado via Docker
- Proxy reverso com Nginx
- SSL via Let's Encrypt

## 📊 Métricas de Qualidade

- **Backend**: 80%+ cobertura de testes
- **Frontend**: 70%+ cobertura de testes
- **Performance**: < 200ms resposta API
- **Uptime**: 99.9%+ disponibilidade

## 🤝 Contribuição

Este projeto segue princípios rigorosos de Clean Code e DRY (Don't Repeat Yourself). Consulte o Memory Bank para convenções detalhadas.

## 📝 Licença

[A definir]

## 📞 Suporte

- **Documentação**: `/docs`
- **Memory Bank**: `/memory-bank`
- **Issues**: GitHub Issues

---

**Status do Projeto**: 🔄 **Em Desenvolvimento Ativo**  
**Última Atualização**: Dezembro 2024  
**Versão Atual**: 0.1.0 (MVP em desenvolvimento) 