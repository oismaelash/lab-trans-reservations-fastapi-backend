#!/bin/bash
# Script para configurar o banco de dados

echo "Parando containers..."
docker-compose down

echo "Removendo volume antigo do PostgreSQL..."
docker volume rm testepy_pgdata 2>/dev/null || echo "Volume não encontrado ou já removido"

echo "Recriando containers..."
docker-compose up --build 

echo "Aguardando PostgreSQL ficar pronto..."
sleep 5

echo "Banco de dados 'reservas' deve estar pronto!"

# Cenário comum de desenvolvimento
