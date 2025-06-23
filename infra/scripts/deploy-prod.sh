#!/bin/bash

# Script de Deploy para Produção - VendPerto ERP
echo "🚀 Iniciando deploy em produção..."

# Verificar se estamos no diretório correto
if [ ! -f "infra/docker/docker-compose.prod.yml" ]; then
    echo "❌ Erro: Execute este script a partir da raiz do projeto"
    exit 1
fi

# Parar serviços existentes
echo "⏹️ Parando serviços existentes..."
docker-compose -f infra/docker/docker-compose.prod.yml down

# Fazer backup do banco (opcional)
echo "💾 Criando backup do banco..."
mkdir -p backups
docker exec postgres pg_dump -U vendperto vendperto > "backups/backup_$(date +%Y%m%d_%H%M%S).sql" 2>/dev/null || true

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p infra/docker/traefik/letsencrypt
chmod 600 infra/docker/traefik/letsencrypt

# Construir imagens
echo "🔨 Construindo imagens..."
docker-compose -f infra/docker/docker-compose.prod.yml build --no-cache

# Subir serviços
echo "⬆️ Subindo serviços..."
docker-compose -f infra/docker/docker-compose.prod.yml up -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 30

# Verificar status
echo "🔍 Verificando status dos serviços..."
docker-compose -f infra/docker/docker-compose.prod.yml ps

# Executar migrações
echo "🔄 Executando migrações do banco..."
docker-compose -f infra/docker/docker-compose.prod.yml exec -T backend alembic upgrade head

# Verificar saúde da API
echo "🏥 Verificando saúde da API..."
if curl -f -s https://api.ambientedeteste.dev/health > /dev/null; then
    echo "✅ API funcionando corretamente!"
else
    echo "⚠️ API ainda não está respondendo (isso é normal nos primeiros minutos)"
fi

echo "✅ Deploy concluído!"
echo ""
echo "📋 URLs importantes:"
echo "🌐 Frontend: https://ambientedeteste.dev"
echo "🔌 API: https://api.ambientedeteste.dev"
echo "📖 Documentação: https://api.ambientedeteste.dev/docs"
echo "📊 Logs: docker-compose -f infra/docker/docker-compose.prod.yml logs -f"
echo ""
echo "🔧 Comandos úteis:"
echo "   Ver logs: ./infra/scripts/logs-prod.sh"
echo "   Parar: docker-compose -f infra/docker/docker-compose.prod.yml down"
echo "   Reiniciar: docker-compose -f infra/docker/docker-compose.prod.yml restart" 