from fastapi import FastAPI
from threading import Semaphore
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

class Handler():
    buffer = []



def check_chromedriver_availability():
    try:
        # Especifique o caminho para o ChromeDriver
        chrome_driver_path = './drivers/chromedriver'  # Atualize o caminho conforme necessário
        webdriver.Chrome(executable_path=chrome_driver_path)
        print("ChromeDriver está disponível no ambiente.")
    except WebDriverException as e:
        print(f"Erro ao iniciar o ChromeDriver: {e}")
        print("Certifique-se de que o ChromeDriver está instalado e configurado corretamente.")

def abrir_navegador():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--headless') # navegador oculto
        options.use_chromium = True
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--window-size=1920x1080")
        try:
            driver_manager = ChromeDriverManager().install()
            driver = webdriver.Chrome(options=options)
            
        except Exception as e: 
            driver_manager = ChromeDriverManager()
            driver = webdriver.Chrome(executable_path=driver_manager.install(), options=options)

        print(f' \n💻 \x1b[32m Navegador Chrome iniciado! \x1b[0m✅\n')
        driver.maximize_window()
        # Abrir a segunda aba
        driver.execute_script("window.open('', '_blank');")
        
        # abrir a terceira aba
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

    # Semafaro para limitar processos simultaneos na API
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
        check_chromedriver_availability()
        driver = abrir_navegador()    

        return {"mensagem": "JSON recebido com sucesso", "dados": dados_json}

if __name__ == "__main__":
    # Executa o aplicativo usando o servidor Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
