#!/bin/bash

# Função para verificar se a porta está em uso
is_port_in_use() {
  netstat -an | grep "LISTEN" | grep -q ":$1\b"
}

# Porta inicial
PORT=8080

# Encontra a primeira porta disponível a partir da porta inicial
while is_port_in_use $PORT; do
  echo "Porta $PORT está em uso. Tentando a próxima..."
  PORT=$((PORT + 1))
done

echo "Iniciando a aplicação na porta $PORT..."

# Exporta a variável de ambiente para o docker-compose
export APP_PORT=$PORT

# Constrói e sobe os contêineres
# O -d (detached) é opcional, mas bom para rodar em segundo plano
docker compose up --build -d

# Aguarda um pouco para os serviços estabilizarem (opcional, mas recomendado)
sleep 5

echo ""
echo "----------------------------------------------------"
echo " Aplicação Guia de Estudo Pro iniciada com sucesso!"
echo ""
echo " Acesse em: http://localhost:$PORT"
echo "----------------------------------------------------"
echo ""
echo "Para parar a aplicação, execute: docker compose down"
echo ""
