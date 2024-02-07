# Use a imagem oficial do Python
FROM python:3.8-slim

# Instale as dependências do sistema necessárias
RUN apt-get update \
    && apt-get install -y wget unzip curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instale o Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instale o ChromeDriver
RUN wget -q https://chromedriver.storage.googleapis.com/97.0.4692.71/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && rm chromedriver_linux64.zip

# Configurar o diretório de trabalho
WORKDIR /app

# Copiar os arquivos necessários
COPY requirements.txt .
COPY main.py .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt
