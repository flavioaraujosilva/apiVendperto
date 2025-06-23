# Regras do Projeto API VendPerto

## Convenções de Nomenclatura

### Idioma: PORTUGUÊS BRASILEIRO
- **Todas** as variáveis, funções, classes, métodos devem estar em português
- **Todas** as tabelas do banco de dados em português  
- **Todas** as rotas e páginas em português
- **Todas** as mensagens de erro e retorno em português

### Exemplos de Nomenclatura Correta:

#### Funções:
```python
def validarCpf(cpf: str) -> bool:
def criarUsuario(dados: dict) -> Usuario:
def obterProdutoPorId(produto_id: int) -> Produto:
def calcularTotalVenda(itens: list) -> float:
```

#### Tabelas do Banco:
```sql
usuario
estoque  
perfil
produto
venda
categoria
fornecedor
cliente
```

#### Rotas/Endpoints:
```
/registrar
/login
/dashboard
/financeiro
/estoque
/vendas
/relatorios
```

#### Variáveis:
```python
nome_usuario = "João"
total_vendas = 1500.00
data_cadastro = datetime.now()
lista_produtos = []
```

## Estrutura do Projeto

```
apiVendperto/
│
├── frontend/         # Aplicação React
├── backend/          # API FastAPI  
├── infra/            # Docker, docker-compose, nginx, CI/CD
├── docs/             # Documentação do projeto
├── memory-bank/      # Documentação do Memory Bank
└── README.md
```

## Princípios de Desenvolvimento

1. **DRY (Don't Repeat Yourself)** - Evitar duplicação de código
2. **SOLID** - Seguir princípios SOLID 
3. **Clean Code** - Código limpo e legível
4. **TDD** - Testes antes da implementação
5. **Modularidade** - Componentes desacoplados

## Fluxo de Desenvolvimento

1. **Planejamento** - Documentar antes de implementar
2. **Estrutura** - Criar apenas estrutura de pastas inicialmente
3. **Implementação Gradual** - Só criar código quando autorizado
4. **Primeira Entrega** - Página de login + conexão backend
5. **Iterações** - Desenvolvimento incremental

## Configurações de Ambiente

### Banco de Dados PostgreSQL:
- Host: 5.161.218.248
- Porta: 5432
- Database: vendperto
- Senha: nxq8n8m0qh7lnrqz

### Ambientes:
- Teste: ambientedeteste.dev
- Produção: (a definir)

## Tecnologias Obrigatórias

- Backend: Python FastAPI
- Banco: PostgreSQL
- Documentação: ReDoc
- Logs: Sistema robusto de logging
- Testes: Pytest
- Infraestrutura: Docker 