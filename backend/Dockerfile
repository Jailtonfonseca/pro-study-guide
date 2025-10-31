# Usar uma imagem base oficial do Python
FROM python:3.11-slim

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Expor a porta que o Uvicorn usará
EXPOSE 8000

# Criar um usuário não-root para rodar a aplicação
RUN useradd --create-home appuser

# Criar o arquivo de chaves de API e dar a permissão correta antes de trocar de usuário
RUN touch api_keys.json && chown appuser:appuser api_keys.json

USER appuser

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
