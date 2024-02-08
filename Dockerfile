# Use a imagem oficial do Python
FROM python:3.9

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Criar e definir o diretório de trabalho
WORKDIR /app

# Copiar os requisitos do projeto para o contêiner
COPY requirements.txt /app/

# Instalar as dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Criação de um ambiente virtual
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Instalar o Alembic
RUN pip install alembic

# Copiar o código-fonte para o contêiner
COPY . /app/

# Adicionar o alembic.ini à imagem
COPY alembic.ini /app/alembic.ini

# Instalar o pydantic_settings
RUN pip install pydantic-settings

# Instalar o psycopg2 para PostgreSQL
RUN pip install psycopg2-binary

# Expor a porta que a aplicação FastAPI estará escutando
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["/venv/bin/alembic", "upgrade", "head", "&&", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
