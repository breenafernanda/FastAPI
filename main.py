from fastapi import FastAPI
from threading import Semaphore
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import subprocess
import shutil, subprocess, uvicorn, requests
from fastapi.responses import HTMLResponse

class Handler():
    buffer = []

    
def install_dependencies():
    dependencies = [
        "fonts-liberation",
        "libasound2",
        "libatk-bridge2.0-0",
        "libatk1.0-0",
        "libatspi2.0-0",
        "libcairo2",
        "libcups2",
        "libdbus-1-3",
        "libdrm2",
        "libgbm1",
        "libgtk-3-0",
        "libgtk-4-1",
        "libnspr4",
        "libnss3",
        "libpango-1.0-0",
        "libu2f-udev",
        "libvulkan1",
        "libx11-6",
        "libxcb1",
        "libxcomposite1",
        "libxdamage1"
    ]

    for dependency in dependencies:
        try:
            subprocess.run(f"sudo apt-get install -y {dependency}", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao instalar a dependência {dependency}: {e}")

def check_chrome_installation():
    try:
        install_dependencies()
        # Verifica se o executável do Chrome está no PATH
        if shutil.which("google-chrome") or shutil.which("google-chrome-stable"):
            print("Chrome está instalado no ambiente.")
        else:
            print("Chrome não está instalado no ambiente. Instalando...")

            # URL para download do Google Chrome
            download_url = "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"

            # Comando para instalar o Chrome
            install_command = "sudo dpkg -i google-chrome-stable_current_amd64.deb"

            # Baixa o arquivo do Chrome
            response = requests.get(download_url)
            with open("google-chrome-stable_current_amd64.deb", "wb") as f:
                f.write(response.content)

            # Executa o comando de instalação
            subprocess.run(install_command, shell=True, check=True)

            # Comando para corrigir dependências (caso necessário)
            fix_dependencies_command = "sudo apt-get install -f"

            # Executa o comando de correção de dependências
            subprocess.run(fix_dependencies_command, shell=True, check=True)

            # Limpando o arquivo .deb após a instalação
            subprocess.run("rm google-chrome-stable_current_amd64.deb", shell=True, check=True)

            print("Chrome instalado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar o Chrome: {e}")

def check_chromedriver_availability():
    try:
        # Especifique o caminho para o ChromeDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')  # navegador oculto
        options.use_chromium = True
        driver_manager = ChromeDriverManager()
        driver = webdriver.Chrome(executable_path=driver_manager.install(), options=options)
        print("ChromeDriver está disponível no ambiente.")
    except WebDriverException as e:
        print(f"Erro ao iniciar o ChromeDriver: {e}")
        print("Certifique-se de que o ChromeDriver está instalado e configurado corretamente.")

def abrir_navegador():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')  # navegador oculto
        options.use_chromium = True
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--window-size=1920x1080")
        
        # Utilize o ChromeDriverManager para instalar e obter o caminho do ChromeDriver
        driver_manager = ChromeDriverManager()
        driver = webdriver.Chrome(executable_path=driver_manager.install(), options=options)

        print(f' \n💻 \x1b[32m Navegador Chrome iniciado! \x1b[0m✅\n')
        driver.maximize_window()
        # Abrir a segunda aba
        driver.execute_script("window.open('', '_blank');")
        
        # Abrir a terceira aba
        driver.execute_script("window.open('', '_blank');")

        return driver
    except Exception as erro:
        print(f'VERIFICAR NAVEGADOR ABERTO \n {erro}')

# lib para limitar buffer em 2 processos por vez (lib cria fila de execução)
semaphore = Semaphore(2) 

app = FastAPI()

def executar_no_terminal(comando):
    """
    Executa um comando no terminal.

    Parâmetros:
    - comando (str): O comando a ser executado.

    Retorna:
    - Saída padrão do comando se a execução for bem-sucedida, None caso contrário.
    """
    try:
        # Executa o comando no terminal
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"Comando recebido:\x1b[36m {comando}\n\n\x1b[34mComando executado com sucesso!\x1b[0m")
        print(f'\x1b[33msaída do terminal -> {resultado.stdout}\x1b[0m')
        return resultado.stdout
    except subprocess.CalledProcessError as e:
        print(f"\x1b[35mErro ao executar o comando:\n {e}\x1b[0m")
        return None


# Rota para exibir a página terminal.html
@app.get("/terminal")
async def exibir_terminal():
    # Leia o conteúdo do arquivo terminal.html
    with open("terminal.html", "r") as arquivo_html:
        conteudo_html = arquivo_html.read()
    return HTMLResponse(content=conteudo_html)

# Rota para receber o comando via método POST
@app.post("/executar-comando")
async def executar_comando(comando: str):
    print(f"Comando recebido: {comando}")
    # Aqui você pode chamar a função executar_no_terminal(comando) para processar o comando
    # e retornar a saída adequada (como um JSON ou texto).
    # Por enquanto, vou apenas retornar uma mensagem de sucesso.
    return "Comando recebido com sucesso!"

if __name__ == "__main__":
    # Executa o aplicativo usando o servidor Uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e: print(f'Erro ao iniciar API {e}')