#!/bin/bash
# Script para rebuild completo do Docker

echo "🧹 Limpando imagens Docker antigas..."
docker rmi avantis-bot 2>/dev/null || true

echo "🔨 Construindo nova imagem..."
docker build -t avantis-bot .

echo "✅ Pronto! Execute com:"
echo "docker run --rm -it -v \"\${PWD}:/app\" avantis-bot"
