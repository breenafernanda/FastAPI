# Usa uma imagem base oficial do Python como ponto de partida
FROM python:3.8-slim
 
# Define o diretório de trabalho no contêiner
WORKDIR /app
 
# Instala o Google Chrome
RUN apt-get update && apt-get install -y wget gnupg2 && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable
 
# Instala o ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+") && \
    CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") && \
    wget -q --continue -P /chromedriver "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip /chromedriver/chromedriver* -d /usr/local/bin/
 
# Limpa o cache do apt
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
 
# Copia os arquivos locais para o contêiner
COPY . .
 
# Instala as dependências do projeto Python
RUN pip install --no-cache-dir -r requirements.txt
 
# Comando padrão para executar a aplicação
