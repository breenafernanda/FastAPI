from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

# Rota para receber o JSON via método POST
@app.post("/processar-dados")
async def receber_json(dados_json: dict):
    print(f'Dados recebidos: {dados_json}')
    return {"mensagem": "JSON recebido com sucesso", "dados": dados_json}






if __name__ == "__main__":
    # Executa o aplicativo usando o servidor Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
