from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}


@app.get("/financiamento")
async def root():
    return {"greeting": "Página de Financiamento"}


