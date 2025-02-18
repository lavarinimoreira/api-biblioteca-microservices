# Usando uma imagem base com Python 3.12 slim
FROM python:3.12-slim

# Definindo a versão do Poetry a ser instalada
ENV POETRY_VERSION=2.0.1
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/"

# Instale o Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos de dependências para a imagem
# Se o arquivo poetry.lock não existir, o Docker ainda continuará
COPY pyproject.toml poetry.lock* README.md /app/

# Configure o Poetry para não criar um virtualenv e instale as dependências
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copie o restante do código da aplicação
COPY . /app

