# Use a imagem oficial do Python
FROM python:3.8-slim

# Instale o Hypercorn
RUN pip install hypercorn

# Crie um diretório de trabalho
WORKDIR /app

# Copie os arquivos do aplicativo para o diretório de trabalho (certifique-se de ter o seu aplicativo aqui)
COPY . /app

# Comando de execução do Hypercorn
CMD ["hypercorn", "main:app", "--bind", "fastapi-production-00ec.up.railway.app:5000"]
