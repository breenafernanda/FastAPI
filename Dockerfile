# Dockerfile
FROM python:3.8-slim

# Atualiza a lista de pacotes e instala dependências
RUN apt-get update && apt-get install -y wget gnupg2 unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Adiciona o repositório do Google Chrome ao sources.list
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Instala o ChromeDriver
RUN wget -q --continue -P /chromedriver "https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip" \
    && unzip /chromedriver/chromedriver* -d /usr/local/bin/ \
    && rm -rf /chromedriver

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o contêiner
COPY . .

# Instala as dependências do projeto
RUN pip install selenium

# Comando para executar o script de teste
CMD ["python", "main.py"]
