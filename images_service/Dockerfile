# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Instala dependências do sistema e o Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=2.0.1

RUN pip install "poetry==$POETRY_VERSION"

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock* ./

# Instala as dependências do projeto sem criar um virtualenv
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta padrão da aplicação
EXPOSE 8000

# Comando para iniciar a aplicação com Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
