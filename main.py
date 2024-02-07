from fastapi import FastAPI

class API():
    buffer = 0
    
app = FastAPI()

@app.get("/")
async def root():
    status_buffer = API.buffer
    return {"greeting": "Hello, World!", "message": f"Welcome to FastAPI!\n\nBuffer = {status_buffer}"}


@app.get("/financiamento")
async def root():
    return {"greeting": "Página de Financiamento", "message":"API FINANCIAMENTO"}

