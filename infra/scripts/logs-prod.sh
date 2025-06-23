#!/bin/bash

# Script para visualizar logs de produção
echo "📊 Logs de produção - VendPerto ERP"
echo "======================================"

# Função para mostrar menu
mostrar_menu() {
    echo ""
    echo "Escolha uma opção:"
    echo "1) Todos os serviços"
    echo "2) Apenas API (backend)"
    echo "3) Apenas Traefik"
    echo "4) Apenas Frontend"
    echo "5) Logs de acesso Traefik"
    echo "6) Últimas 50 linhas de todos"
    echo "0) Sair"
    echo ""
    read -p "Digite sua opção: " opcao
}

# Loop principal
while true; do
    mostrar_menu
    
    case $opcao in
        1)
            echo "📊 Mostrando logs de todos os serviços..."
            docker-compose -f infra/docker/docker-compose.prod.yml logs -f
            ;;
        2)
            echo "🔌 Mostrando logs da API..."
            docker-compose -f infra/docker/docker-compose.prod.yml logs -f backend
            ;;
        3)
            echo "🌐 Mostrando logs do Traefik..."
            docker-compose -f infra/docker/docker-compose.prod.yml logs -f traefik
            ;;
        4)
            echo "💻 Mostrando logs do Frontend..."
            docker-compose -f infra/docker/docker-compose.prod.yml logs -f frontend
            ;;
        5)
            echo "📈 Mostrando logs de acesso do Traefik..."
            docker exec vendperto-traefik-prod tail -f /var/log/traefik/access.log
            ;;
        6)
            echo "📋 Últimas 50 linhas de todos os serviços..."
            docker-compose -f infra/docker/docker-compose.prod.yml logs --tail=50
            ;;
        0)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida!"
            ;;
    esac
    
    echo ""
    read -p "Pressione Enter para continuar..."
done 