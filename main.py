from fastapi import FastAPI, HTTPException
from threading import Semaphore
import uvicorn

class Handler():
    buffer = []


# lib para limitar buffer em 2 processos por vez (lib cria fila de execução)
semaphore = Semaphore(2) 


app = FastAPI()

# Rota para receber o JSON via método POST
@app.post("/processar-dados")
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
            print(f'Buffer: {Handler.buffer}')
            return {"mensagem": "JSON recebido com sucesso", "dados": dados_json}






if __name__ == "__main__":
    # Executa o aplicativo usando o servidor Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
