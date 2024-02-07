from fastapi import FastAPI
import random

class Handler():
    buffer = []

def adicionar_buffer(elemento):
   Handler.buffer.append(elemento)

def remover_buffer(elemento):
    Handler.buffer.remove(elemento)
    
app = FastAPI()

@app.get("/")
async def root():
    status_buffer = Handler.buffer
    return {"greeting": "Hello, World!", "message": f"Welcome to FastAPI!\n\nBuffer = {status_buffer}"}


@app.get("/add1")
async def root():
    numero_escolhido = random.randint(1, 10)
    adicionar_buffer('elemento1')
    return {"greeting": "Página de Financiamento", "message":"API FINANCIAMENTO\n ADICIONAR BUFFER 1"}
    
@app.get("/add2")
async def root():
    numero_escolhido = random.randint(1, 10)
    adicionar_buffer('elemento2')
    return {"greeting": "Página de Financiamento", "message":"API FINANCIAMENTO\n ADICIONAR BUFFER 2"}


@app.get("/del1")
async def root():
    numero_escolhido = random.randint(1, 10)
    remover_buffer('elemento1')
    return {"greeting": "Página de Financiamento", "message":"API FINANCIAMENTO\n REMOVER BUFFER"}
