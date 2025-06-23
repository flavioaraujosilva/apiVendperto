# Padrões do Sistema - API VendPerto

## Arquitetura Geral

### Padrão: Clean Architecture + DDD
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
│                   CAMADA DE SERVIÇOS                    │
│    AutenticacaoService | UsuarioService | EstoqueService│
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   CAMADA DE DOMÍNIO                     │
│      Usuario | Produto | Venda | Categoria              │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                CAMADA DE INFRAESTRUTURA                 │
│         PostgreSQL | Redis | Logs | Monitoramento      │
└─────────────────────────────────────────────────────────┘
```

## Estrutura de Pastas Detalhada

```
apiVendperto/
│
├── frontend/                    # Aplicação React
│   ├── src/
│   │   ├── componentes/        # Componentes reutilizáveis
│   │   ├── paginas/            # Páginas da aplicação
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   └── financeiro/
│   │   ├── servicos/           # Chamadas para API
│   │   ├── contextos/          # Context API
│   │   └── utils/              # Utilitários
│   ├── public/
│   └── package.json
│
├── backend/                     # API FastAPI
│   ├── app/
│   │   ├── main.py             # Ponto de entrada
│   │   ├── api/                # Endpoints da API
│   │   │   ├── v1/
│   │   │   │   ├── auth/       # Autenticação
│   │   │   │   ├── usuarios/   # Gestão de usuários
│   │   │   │   ├── estoque/    # Controle de estoque
│   │   │   │   └── vendas/     # Módulo de vendas
│   │   │   └── dependencias.py
│   │   ├── core/               # Configurações centrais
│   │   │   ├── config.py       # Configurações
│   │   │   ├── seguranca.py    # JWT, hashing
│   │   │   └── database.py     # Conexão DB
│   │   ├── modelos/            # Modelos do banco
│   │   │   ├── usuario.py
│   │   │   ├── produto.py
│   │   │   └── venda.py
│   │   ├── esquemas/           # Pydantic schemas
│   │   ├── servicos/           # Lógica de negócio
│   │   ├── repositorios/       # Acesso a dados
│   │   └── utils/              # Utilitários
│   ├── tests/                  # Testes automatizados
│   │   ├── test_auth.py
│   │   ├── test_usuarios.py
│   │   └── test_integracao.py
│   ├── alembic/                # Migrações do banco
│   ├── requirements.txt
│   └── .env.exemplo
│
├── infra/                      # Infraestrutura
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.frontend
│   │   └── docker-compose.yml
│   ├── nginx/
│   │   └── nginx.conf
│   ├── scripts/
│   │   ├── deploy.sh
│   │   └── backup.sh
│   └── k8s/                    # Kubernetes (futuro)
│
├── docs/                       # Documentação
│   ├── api/                    # Docs da API
│   ├── arquitetura/            # Diagramas
│   └── manuais/                # Manuais de uso
│
├── memory-bank/                # Memory Bank
│   ├── regras.md
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── activeContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   └── progress.md
│
└── README.md
```

## Padrões de Código

### 1. Nomenclatura (Português Brasileiro)
```python
# ✅ CORRETO
class UsuarioService:
    def criarUsuario(self, dados: dict) -> Usuario:
        pass
    
    def validarCpf(self, cpf: str) -> bool:
        pass

# ❌ INCORRETO  
class UserService:
    def createUser(self, data: dict) -> User:
        pass
```

### 2. Estrutura de Endpoints
```python
# Padrão para todos os endpoints
@router.post("/registrar", response_model=UsuarioResponse)
async def registrar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(obter_db)
):
    """Registra um novo usuário no sistema."""
    pass
```

### 3. Tratamento de Erros
```python
# Padrão unificado de exceções
class VendPertoException(Exception):
    def __init__(self, mensagem: str, codigo: int = 400):
        self.mensagem = mensagem
        self.codigo = codigo

class UsuarioNaoEncontrado(VendPertoException):
    def __init__(self):
        super().__init__("Usuário não encontrado", 404)
```

## Padrões de Segurança

### 1. Autenticação JWT
```python
# Estrutura do token
{
    "sub": "id_usuario",
    "email": "usuario@exemplo.com",
    "perfil": "administrador",
    "exp": timestamp_expiracao
}
```

### 2. Controle de Acesso (RBAC)
```python
# Níveis de permissão
PERFIS = {
    "administrador": ["*"],  # Acesso total
    "gerente": ["usuarios.ler", "vendas.*", "estoque.*"],
    "vendedor": ["vendas.criar", "vendas.ler", "estoque.ler"],
    "operador": ["estoque.*"]
}
```

## Padrões de Banco de Dados

### 1. Convenções de Nomenclatura
```sql
-- Tabelas: singular, minúsculo
usuario
produto  
venda

-- Campos: snake_case
data_criacao
total_vendas
cpf_usuario

-- Índices: idx_tabela_campo
idx_usuario_email
idx_produto_categoria
```

### 2. Padrões de Auditoria
```sql
-- Campos obrigatórios em todas as tabelas
id SERIAL PRIMARY KEY
data_criacao TIMESTAMP DEFAULT NOW()
data_atualizacao TIMESTAMP DEFAULT NOW()
ativo BOOLEAN DEFAULT TRUE
```

## Padrões de API

### 1. Estrutura de Response
```json
{
    "sucesso": true,
    "dados": {...},
    "mensagem": "Operação realizada com sucesso",
    "timestamp": "2024-01-01T10:00:00Z"
}
```

### 2. Paginação Padrão
```json
{
    "itens": [...],
    "total": 100,
    "pagina": 1,
    "por_pagina": 20,
    "total_paginas": 5
}
```

## Padrões de Logging

### 1. Estrutura de Log
```python
logger.info(
    "Ação executada",
    extra={
        "usuario_id": 123,
        "acao": "criar_produto",
        "ip": "192.168.1.1",
        "dados": {...}
    }
)
```

### 2. Níveis de Log
- **DEBUG**: Informações de desenvolvimento
- **INFO**: Operações normais
- **WARNING**: Situações suspeitas
- **ERROR**: Erros recuperáveis
- **CRITICAL**: Falhas do sistema

## Padrões de Testes

### 1. Estrutura de Teste
```python
class TestUsuarioService:
    def setup_method(self):
        # Configuração antes de cada teste
        pass
    
    def test_criar_usuario_sucesso(self):
        # Arrange
        dados = {...}
        
        # Act
        resultado = servico.criarUsuario(dados)
        
        # Assert
        assert resultado.id is not None
```

### 2. Categorias de Teste
- **Unitários**: Testam funções isoladas
- **Integração**: Testam componentes conectados
- **E2E**: Testam fluxos completos
- **Performance**: Testam carga e velocidade 