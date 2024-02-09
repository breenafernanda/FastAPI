import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import subprocess
import asyncio
import websockets
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

async def conectar_browserless(hostname_browserless, options):
    uri = f"wss://{hostname_browserless}/devtools/browser"

    async with websockets.connect(uri) as websocket:
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}

        payload = {
            "method": "Browser.createTarget",
            "params": {"url": "about:blank"},
        }
        await websocket.send(payload)

        # Espera um pouco para garantir que a nova sessão seja criada
        await asyncio.sleep(2)

        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
        return driver

async def abrir_navegador(browser='chrome', headless=True):
    try:
        print(f'Abrindo navegador {browser}') 
        # Substitua a URL abaixo pela URL do seu serviço Browserless
        browserless_url = "wss://browserless-production-6d17.up.railway.app/devtools/browser/96773cac-8991-4500-935b-ff5458a59376"

        # Configuração do WebDriver remoto
        capabilities = {
            "browserName": "chrome",
            "goog:chromeOptions": {"w3c": False},  # Desativar o modo W3C para compatibilidade
        }

        options = webdriver.ChromeOptions()
        options.add_experimental_option("w3c", False)  # Desativar o modo W3C para compatibilidade

        # Usar Remote mesmo localmente
        driver = webdriver.Remote(
            command_executor=browserless_url,
            desired_capabilities=capabilities,
            options=options
        )

        # Exemplo de uso
        driver.get("https://www.exemplo.com")
        print(driver.title)

        # Feche o navegador
        driver.quit()
    except Exception as e: 
        print(f'ERRO AO ABRIR NAVEGADOR -> {e}')

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

async def executar_no_terminal(comando):
    try:
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"Comando recebido:\x1b[36m {comando}\n\n\x1b[34mComando executado com sucesso!\x1b[0m")
        print(f'\x1b[33msaída do terminal -> {resultado.stdout}\x1b[0m')
        return resultado.stdout
    except subprocess.CalledProcessError as e:
        print(f"\x1b[35mErro ao executar o comando:\n {e}\x1b[0m")
        return f"Erro ao executar o comando:\n {e}"

async def run_command(command: str):
    if command == 'config':
        await executar_no_terminal('pip install pyppeteer')
        driver = await abrir_navegador(browser='chrome', headless=True)
        driver.get('https://www.example.com')
        print(f'Acessou link')
        driver.quit()
    else:
        retorno = await executar_no_terminal(command)
    print(f"Comando recebido: {command}")
    return f'{command}\n🤖 {retorno}\n\nComando Recebido pela API com sucesso ✅\n_________________________________'

@app.get("/terminal", response_class=HTMLResponse)
async def terminal():
    return HTMLResponse(content=open("templates/terminal.html", "r").read(), status_code=200)

@app.post("/run_command")
async def execute_command(command: dict):
    try:
        result = await run_command(command['command'])
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
