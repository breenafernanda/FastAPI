from fastapi import FastAPI
from threading import Semaphore
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import shutil, subprocess, uvicorn, requests

class Handler():
    buffer = []
import subprocess

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

# Rota para receber o JSON via método POST
@app.post("/api_financiamento")
async def receber_json(dados_json: dict):
    print(f'Dados recebidos: {dados_json}')
    data = dados_json
    # identificar a proposta que foi enviada para adicionar ao array de buffer
    numero_proposta = data.get('numero_proposta', 'Proposta não especificada')
    Handler.buffer.append(numero_proposta)

    # Semáforo para limitar processos simultâneos na API
    with semaphore:
        status_santander = None
        status_btg = None
        status_bv = None
        # Seção crítica: Apenas 2 threads podem entrar aqui simultaneamente
        instances_running = semaphore._value
        cpf = data.get('cpf', 'CPF não especificado')
        valor_proposta = data.get('valor_proposta', 'Valor não especificado')
        print(f'Buffer: {Handler.buffer}')

        print(
            f'\x1b[31m>>> NOVA CHAMADA DE API RECEBIDA <<<<\x1b[32m\n\n    vagas disponíveis no buffer: {instances_running} \n\n'
            f'Proposta recebida: \x1b[31m{numero_proposta}\x1b[32m\n'
            f'CPF: \x1b[31m{cpf}\x1b[32m\n'
            f'Valor da Proposta: \x1b[31m R$ {valor_proposta}\x1b[32m\n'
        )

        # Chama a função para verificar a disponibilidade do ChromeDriver
        # check_chromedriver_availability()

        # Chama a função para verificar a instalação do Chrome
        # check_chrome_installation()

        # Inicia o navegador
        # driver = abrir_navegador()
        # Exemplo de uso
        comando = "sudo apt update"
        executar_no_terminal(comando)
        executar_no_terminal("sudo apt install wget")
        executar_no_terminal("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        executar_no_terminal("sudo dpkg -i google-chrome-stable_current_amd64.deb")
        executar_no_terminal("sudo apt-get install -f")
        executar_no_terminal("google-chrome -V")
        
        return {"mensagem": "JSON recebido com sucesso", "dados": dados_json}

if __name__ == "__main__":
    # Executa o aplicativo usando o servidor Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
