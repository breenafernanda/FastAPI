from fastapi import FastAPI
# from flask import Flask, request, jsonify
import time, requests, os, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
from time import sleep
from threading import Semaphore

app = FastAPI()

@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}


# @app.get("/financiamento")
# async def root():
#     return {"greeting": "Página de Financiamento", "message":"API FINANCIAMENTO"}



semaphore = Semaphore(2) 
