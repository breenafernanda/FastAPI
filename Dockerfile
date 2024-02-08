# Dockerfile
FROM python:3.8-slim

# Instala o Google Chrome
RUN apt-get update && apt-get install -y wget gnupg2 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Instala o ChromeDriver
RUN apt-get update && apt-get install -y wget unzip && \
    CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+.[0-9]+.[0-9]+" | head -n 1) && \
    CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") && \
    wget -q --continue -P /chromedriver "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip /chromedriver/chromedriver* -d /usr/local/bin/ && \
    rm -rf /chromedriver && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o contêiner
COPY . .

# Instala as dependências do projeto
RUN pip install selenium

# Comando para executar o script de teste
CMD ["python", "main.py"]
