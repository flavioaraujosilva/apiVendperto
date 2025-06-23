#!/bin/bash

echo "🧪 Testando API VendPerto ERP..."

API_URL="http://localhost:8000"

echo ""
echo "1️⃣ Testando endpoint de saúde..."
curl -s "${API_URL}/health" | python -m json.tool

echo ""
echo ""
echo "2️⃣ Testando registro de usuário..."
curl -s -X POST "${API_URL}/api/v1/auth/registrar" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@vendperto.com",
    "nome": "Usuario Teste",
    "senha": "senha123",
    "perfil": "administrador"
  }' | python -m json.tool

echo ""
echo ""
echo "3️⃣ Testando login..."
TOKEN=$(curl -s -X POST "${API_URL}/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@vendperto.com",
    "senha": "senha123"
  }' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    echo "✅ Login realizado com sucesso!"
    echo "Token: ${TOKEN:0:50}..."
    
    echo ""
    echo "4️⃣ Testando endpoint protegido..."
    curl -s -X GET "${API_URL}/api/v1/auth/usuario-atual" \
      -H "Authorization: Bearer $TOKEN" | python -m json.tool
else
    echo "❌ Falha no login"
fi

echo ""
echo ""
echo "🏁 Teste concluído!" 