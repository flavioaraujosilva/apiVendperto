#!/bin/bash

echo "🚀 Iniciando VendPerto ERP Backend..."

# Ir para diretório do projeto
cd "$(dirname "$0")/../.."

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker."
    exit 1
fi

echo "📦 Construindo e iniciando containers..."

# Ir para diretório do docker-compose
cd infra/docker

# Parar containers anteriores
docker-compose down

# Construir e iniciar
docker-compose up --build -d

echo "✅ Backend iniciado com sucesso!"
echo ""
echo "📍 URLs disponíveis:"
echo "   🔗 API: http://localhost:8000"
echo "   📚 Documentação: http://localhost:8000/docs"
echo "   📖 ReDoc: http://localhost:8000/redoc"
echo "   💾 PostgreSQL: localhost:5433"
echo ""
echo "📊 Para ver logs: docker-compose logs -f backend"
echo "🛑 Para parar: docker-compose down" 