from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from threading import Semaphore
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import shutil, subprocess, uvicorn, requests

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


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
        return f"Erro ao executar o comando:\n {e}"


# Função para simular a execução do comando
def run_command(command: str):
    # Aqui você pode implementar a lógica real para executar o comando
    # Neste exemplo, apenas retornamos uma mensagem simulada
    retorno = executar_no_terminal(command)
    print(f"Comando recebido: {command}")



    return f'{command}\n🤖 {retorno}\n\nComando Recebido pela API com sucesso ✅\n_________________________________'

# Rota para a interface do terminal
@app.get("/terminal", response_class=HTMLResponse)
def terminal():
    return HTMLResponse(content=open("templates/terminal.html", "r").read(), status_code=200)

# Rota para executar comandos
@app.post("/run_command")
async def execute_command(command: dict):
    try:
        result = run_command(command['command'])
        return {"result": result }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Iniciar o servidor usando Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
