from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

class Handler():
    buffer = []

def adicionar_buffer(elemento):
   Handler.buffer.append(elemento)

def remover_buffer(elemento):
    Handler.buffer.remove(elemento)

class DadosParaProcessar(BaseModel):
    nome: str
    idade: int

app = FastAPI()

@app.get("/")
async def root():
    status_buffer = Handler.buffer
    return {"greeting": "Hello, World!", "message": f"Welcome to FastAPI!\n\nBuffer = {status_buffer}"}

@app.post("/processar-dados")
async def processar_dados(dados: dict):
    # Lógica de processamento dos dados aqui
    return {"message": "Dados processados com sucesso", "dados": dados}
@app.get("/ver_buffer")
async def ver_buffer():
    status_buffer = Handler.buffer
    return {"buffer": status_buffer}
