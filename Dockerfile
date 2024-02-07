# Use a imagem oficial do Python
FROM python:3.8-slim

# Instale o ChromeDriver
RUN apt-get update \
    && apt-get install -y wget unzip \
    && wget https://chromedriver.storage.googleapis.com/97.0.4692.71/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && rm chromedriver_linux64.zip \
    && apt-get purge -y wget unzip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Configurar o diretório de trabalho
WORKDIR /app

# Copiar os arquivos necessários
COPY requirements.txt .
COPY main.py .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta
EXPOSE 8000

# Comando para executar o aplicativo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
