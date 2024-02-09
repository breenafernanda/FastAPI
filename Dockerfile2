# Define a imagem base
FROM python:3.8-slim
# Exemplo de mensagem de depuração
RUN echo "Definindo imagem base como python 3.8\n________________________________________________________"

RUN echo "Atualizar a lista de pacotes e instalar as dependencias necessárias \n________________________________________________________"
# Atualiza a lista de pacotes e instala dependências necessárias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Adiciona o repositório do Google Chrome ao sources.list e instala o Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Instala uma versão específica do ChromeDriver
RUN wget -q --continue -P /chromedriver "https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip" \
    && unzip /chromedriver/chromedriver* -d /usr/local/bin/ \
    && rm -rf /chromedriver

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos do projeto para o diretório de trabalho no contêiner
COPY . .

# Instala as dependências do projeto Python, incluindo Selenium
RUN pip install  hypercorn
RUN pip install --no-cache-dir -r requirements.txt


# Comando para executar o script de teste
CMD ["python", "main.py"]
