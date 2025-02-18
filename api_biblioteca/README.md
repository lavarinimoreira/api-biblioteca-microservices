# api biblioteca

API RESTful para gerenciamento de livros, usuários e empréstimos, desenvolvida com FastAPI, SQLAlchemy assíncrono e PostgreSQL.

## Configuração do Ambiente Local

### 1. Clone o Repositório
```
git clone https://github.com/lavarinimoreira/api-biblioteca.git
cd api-biblioteca
```
### 2. Crie o Ambiente Virtual
 ```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
 ```
### 3. Instale as Dependências
O projeto utiliza o Poetry para gerenciamento de dependências.
 ```
pip install poetry
poetry install
```
### 4. Configure o Banco de Dados
Certifique-se de que o PostgreSQL está rodando e crie o banco de dados:
 ```
 psql -U postgres -c "CREATE DATABASE biblioteca;"
```
Configure os arquivos alembic.ini e app/database.py de acordo com suas credenciais.
(NOTA: atualizar para .env)
 ### 5. Rode as Migrações
```
alembic upgrade head
```
### 6. Execute o Servidor
```
uvicorn app.main:app --reload
```
Acesse a documentação interativa em: http://localhost:8000/docs

## Testes
Os testes utilizam pytest com suporte a operações assíncronas.
### 1. Configure o Banco de Testes
```
psql -U postgres -c "CREATE DATABASE biblioteca_test;"
```
### 2. Execute os testes
```
pytest
```