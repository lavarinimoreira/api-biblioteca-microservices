# Projeto FastAPI - Biblioteca

Este projeto implementa uma API para gerenciamento de uma biblioteca, composta por dois microsserviços:  
- **api_biblioteca:** API principal para gerenciar as operações do sistema.  
- **images_services:** Responsável pelo gerenciamento de imagens de usuários e capas de livros.

---

## 1. Instruções de Uso do Projeto

- Clone o repositório:
```bash
git clone https://github.com/lavarinimoreira/api-biblioteca-microservices.git
```
- Navegue até a o diretório do projeto:
```bash
cd api-biblioteca-microservices
```

### 1.1. Instalação de Dependências

O projeto utiliza **Docker Compose** para orquestrar os serviços e **Poetry** para gerenciar as dependências.  
Portanto, ao subir os containers com Docker Compose, as dependências serão instaladas automaticamente.

### 1.2. Configuração do Ambiente

Na raiz do projeto, você precisará criar os seguintes arquivos de ambiente podendo seguir o seguinte exemplo:

- **.env** (para ambiente de desenvolvimento):

```env
DATABASE_URL=postgresql+asyncpg://postgres:university@biblioteca_db:5432/biblioteca_db
POSTGRES_DB=biblioteca_db

POSTGRES_USER=postgres
POSTGRES_PASSWORD=university

DATABASE_URL_CELERY=postgresql+psycopg2://postgres:university@biblioteca_db:5432/biblioteca_db

TEST_DATABASE_URL=postgresql+asyncpg://postgres:university@biblioteca_db_test:5432/biblioteca_db_test
TEST_POSTGRES_DB=biblioteca_db_test

PGADMIN_DEFAULT_EMAIL=postgres@biblioteca.com
PGADMIN_DEFAULT_PASSWORD=university

API_KEY=t8v5W4ntL98tuv4Sn90vnAk

JWT_SECRET=zXHtAkMjfLqQZsa1R3Gzol_hakFta1D14SOruz7NwpQ
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

- **.env.test** (para ambiente de testes):
```env
DATABASE_URL=postgresql+asyncpg://postgres:university@biblioteca_db_test:5432/biblioteca_db_test

POSTGRES_USER=postgres
POSTGRES_PASSWORD=university

POSTGRES_DB=biblioteca_db_test
```
No diretório `/images_service` crie também um arquivo **.env** específico para esse serviço:
```env
API_KEY=t8v5W4ntL98tuv4Sn90vnAk
```
### 1.3. Rodando o Projeto Localmente

Após configurar os arquivos de ambiente, execute as seguintes etapas:

1. **Subir os serviços com Docker Compose:**  
 Utilize o comando para iniciar os containers.
 ```bash
 docker compose up --build -d
  ```
2. **Realizar a migração com o Alembic:**
Execute o comando abaixo para atualizar o banco de dados:
```bash
docker compose exec api_biblioteca alembic upgrade head
```
3. **Popular o banco de dados:**
Após a migração, entre no container da API:
```bash
docker compose exec api_biblioteca bash
```
E execute o script de popular o banco:
```bash
python -m app.services.scripts._populate_db
```
Após essa etapa o banco de dados estará setado com um usuário administrador.\
Você pode sair do container com o comando "Ctrl" + "D".
- A documentação agora pode ser acessada em: **http://localhost:8000/docs**
### 1.6. Rodando os Testes
Para executar os testes, utilize o seguinte comando:
```bash
docker compose exec api_biblioteca pytest
```
---

## 2. Decisões de Implementação
### 2.1. Tecnologias Utilizadas
O projeto foi desenvolvido utilizando as seguintes tecnologias e ferramentas:
- **FastAPI:** Framework web moderno, de alta performance.
- **PostgreSQL:** Banco de dados relacional robusto e escalável.
- **SQLAlchemy:** ORM para facilitar a interação com o banco de dados.
- **Pydantic:** Validação e definição de modelos de dados.
- **Alembic:** Gerenciamento de migrações do banco de dados.
- **JWT:** Implementação de autenticação segura.
- **Docker e Docker Compose:** Containerização e orquestração dos serviços.
- **Poetry:** Gerenciamento de dependências e empacotamento.
- **Celery:** Processamento de tarefas em segundo plano.

### 2.1. Arquitetura e Diagrama ER
O diagrama abaixo ilustra a estrutura do banco de dados do sistema de biblioteca:
![Diagrama ER](images/er_diagram.png)
A tabela grupo_politica possui a coluna "nome" como chave candidata que é utilizada como chave estrangeira na tabela associativa grupo_politica_permissao.

### 2.3 Estruturação do Código
O código foi organizado para manter uma separação clara das funcionalidades, dividindo o projeto em dois microsserviços:
- **api_biblioteca:** Contém a lógica principal da API, rotas, controladores e serviços.
- **images_services:**  Responsável pelo gerenciamento das imagens dos usuários e capas dos livros.

Esta organização visa facilitar a manutenção, escalabilidade e a evolução independente de cada serviço.

---

## 3. Dificuldades e Dúvidas
### 3.1 Principais Desafios Encontrados
- **Configuração do Alembic:**
Ao separar as tabelas em arquivos diferentes, ocorreram problemas de migração devido ao não reconhecimento das tabelas.\
**Solução:** Criar um arquivo \__all_models.py para que o Alembic detecte corretamente quaisquer atualizações no modelo.

- **Configuração do Celery:**
Utilizava um driver assíncrono para o banco de dados, porém o Celery é nativamente síncrono, o que causou conflitos na configuração.\
**Solução:** Desenvolver um driver síncrono para o Celery, visto que as operações não exigem assincronia nesse contexto. Duas tarefas são executadas em segundo plano, ambas, de 12 em 12 horas: a primeira é responsável por verificar as datas dos empréstimos e identificar atrasos, alterando o status do empréstimo e acionando a função para notificar o usuário. A segunda tarefa lida com arquivos órfão, removendo imagens que não estão mais relacionadas a nenhum usuário ou livro.

- **Dependências Circulares:**
Durante o desenvolvimento, percebi o problema de dependências circulares entre as tabelas que referenciavam umas às outra através de chaves estrangeiras, o que dificultava a criação dos registros de forma sequencial durante as migrações e a inicialização do sistema.\
**Solução:** Utilizar a função "relationship" do sqlalchemy para realizar corretamente o mapeamento das relações dependentes e implementar scripts específicos para popular o banco de dados diretamente. Esses scripts realizam a inserção dos dados fundamentais de forma ordenada, quebrando o ciclo de dependência.

- **Refatoração para Microsserviços:**
A divisão entre a API principal e a API de imagens exigiu um planejamento detalhado para garantir que as requisições fossem encaminhadas corretamente entre os serviços.\
**Solução:** Realizar *debugging* e inspeção cuidadosa das requisições, garantindo que cada serviço comunique corretamente as suas responsabilidades.

---
## Contato

Para dúvidas, sugestões ou contribuições, sinta-se à vontade para entrar em contato:
<a href = "mailto:lavarinimoreira@gmail.com">lavarinimoreira@gmail.com</a>
    
