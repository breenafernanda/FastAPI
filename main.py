from fastapi import FastAPI
from flask import Flask, request, jsonify
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

# @app.get("/")
# async def root():
#     return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}


# @app.get("/financiamento")
# async def root():
#     return {"greeting": "Página de Financiamento", "message":"API FINANCIAMENTO"}



semaphore = Semaphore(2) 

def aguardar_elemento(driver, tempo, tipo, code):
    try:
        if tipo == 'CSS':   
            element = WebDriverWait(driver, tempo).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, code))
            )
        elif tipo == 'ID':
            element = WebDriverWait(driver, tempo).until(
                EC.element_to_be_clickable((By.ID, code))
            )  
        return element
    except Exception as e:  
        # print(f'\x1b[36m erro ao aguardar elemento {e}\x1b[0m')
        return 'Elemento não encontrado'

def abrir_navegador(number):
            try:
                dir_path = os.getcwd()

                options = webdriver.ChromeOptions()
                if number != 0 :
                    profile = f'FinanciamentoAPI_{number}'
                    profile = os.path.join(dir_path, profile)
                    options.add_argument(r"user-data-dir={}".format(profile))
                else: profile = 'Genérico'
                options.add_argument('--disable-gpu')
                # options.add_argument('--headless') # navegador oculto
                options.use_chromium = True
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                options.add_experimental_option('prefs', {'download.default_directory': os.path.join(os.getcwd(), 'download')})
                options.add_argument("--window-size=1920x1080")
                try:
                    driver_manager = ChromeDriverManager().install()
                    driver = webdriver.Chrome(options=options)
                    
                except Exception as e: 
                    driver_manager = ChromeDriverManager()
                    driver = webdriver.Chrome(executable_path=driver_manager.install(), options=options)


                print(f' \n💻 \x1b[32m Navegador Chrome iniciado! {profile} \x1b[0m✅\n')
                driver.maximize_window()
                # Abrir a segunda aba
                driver.execute_script("window.open('', '_blank');")
                
                # abrir a terceira aba
                driver.execute_script("window.open('', '_blank');")

                return driver
            except Exception as erro: print(f'VERIFICAR NAVEGADOR ABERTO \n {erro}')

def receive_mail(numero_proposta):
    import imaplib
    import email
    from email.header import decode_header
    from bs4 import BeautifulSoup

    print(f'\x1b[32m[ {numero_proposta} ]\x1b[0m   \x1b[36m>>> 📩 <<< Aguardando código por email...\x1b[0m')
    sleep(10)
    codigo_confirmacao = None
    # Configurações da conta de email
    email_user = "tech@kinsolenergia.com.br"
    email_pass = "kinsol*24"

    # Configurações do servidor IMAP
    imap_server = "mail.kinsolenergia.com.br"
    imap_port = 993

    # Conectar ao servidor IMAP
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)

    # Efetuar login na conta de email
    mail.login(email_user, email_pass)

    # Selecionar a caixa de entrada
    mail.select("inbox")

    # Procurar por todos os emails na caixa de entrada
    status, messages = mail.search(None, "ALL")
    message_ids = messages[0].split()

    # Iterar sobre os IDs dos emails e recuperar cada email
    for message_id in message_ids:
        # Buscar o email pelo ID
        _, msg_data = mail.fetch(message_id, "(RFC822)")
        raw_email = msg_data[0][1]
        subject = None

        # Decodificar o email
        msg = email.message_from_bytes(raw_email)

        # Obter o assunto e o remetente do email
        subject, encoding = decode_header(msg["Subject"])[0]
        subject = subject.decode(encoding) if encoding else subject
        from_, encoding = decode_header(msg.get("From"))[0]
        from_ = from_.decode(encoding) if encoding else from_


        if subject == "Codigo de confirmacao":

            # Obter o corpo da mensagem
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        # Extrair o código do corpo HTML
                        html_content = part.get_payload(decode=True).decode("utf-8")
                        soup = BeautifulSoup(html_content, 'html.parser')
                        codigo_confirmacao = soup.find('span', class_='title').find_next('span', class_='title').text.strip()

    print('\n\n-------------------------------------------------')
    print(f"Assunto: {subject}")
    print(f"Remetente: {from_}")
    print(f"Código de Confirmação localizado no e-mail: {codigo_confirmacao}")
    print('-------------------------------------------------\n\n')

                        # return codigo_confirmacao
    mail.logout()
    
    return codigo_confirmacao

def acessar_banco(banco, cliente, driver):
                numero_proposta = cliente['numero_proposta']
                if banco == 'santander':
                    try:
                        driver.switch_to.window(driver.window_handles[2])

                        url = 'https://brpioneer.accenture.com/originacao-loj/identification'
                        driver.get(url)
                        ## deslogar e logar novamente para resolver bug dos termos e condições
                        try:
                            # expandir menu {  v  }
                            setinha_baixo = aguardar_elemento(driver, 10, 'CSS', 'body > app-root > app-header > app-header-shopkeeper > div.desktop.d-none.d-md-block > mat-toolbar > span.user-menu.step9 > i')
                            driver.execute_script("arguments[0].click();", setinha_baixo)

                            # clicar em sair
                            botao_sair = driver.find_element(By.CSS_SELECTOR,'body > app-root > app-header > app-header-shopkeeper > div.desktop.d-none.d-md-block > mat-toolbar > app-menu-profile > mat-card > mat-card-content > mat-list > mat-list-item.mat-list-item.mat-focus-indicator.list-item-image > span > span.mat-ripple.mat-list-item-ripple')
                            driver.execute_script("arguments[0].click();", botao_sair)

                            botao_sim_sair_da_conta = aguardar_elemento(driver, 5, 'CSS', '#mat-dialog-0 > app-exit-page > div:nth-child(4) > div:nth-child(2) > button')
                            driver.execute_script("arguments[0].click();", botao_sim_sair_da_conta)
                            

                            try:
                                botao_gd_sair = aguardar_elemento(driver,5,'CSS','#modal-cancel-button')
                                botao_gd_sair.click()
                            except: pass
                                
                                
                            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[34m🔒>>>> Logout realizado!\x1b[0m')

                            inserir_cpf = aguardar_elemento(driver,5,'ID', 'mat-input-0')
                            inserir_cpf.send_keys('39291935824')
                            inserir_senha = driver.find_element(By.ID, 'mat-input-1').send_keys('@Kinsol*23')
                            botao_login = aguardar_elemento(driver,5,'CSS', 'body > app-root > div > app-login-container > div > app-sign-in-container > div > div.content-container.mt-md-5.align-items-center.justify-content-center.d-flex > div > div > form > div:nth-child(8) > button')
                            driver.execute_script("arguments[0].click();", botao_login)

                            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[34m🔓>>>> Login realizado novamente!\x1b[0m')
                        except Exception as e: 
                            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[36m>>>>   ERRO EM DESLOGAR E LOGAR:\n\x1b[32m{e}\x1b[0m')
                            return False

                        try:
                            
                            select = aguardar_elemento(driver,5,'ID', 'mat-select-value-3')
                            select.click()
                        except Exception as e: print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   Erro ao clicar no select por id: {e}')
                        try: 
                            cdc_option =aguardar_elemento(driver,5,'CSS', '#mat-option-4 > span')
                            driver.execute_script("arguments[0].click();", cdc_option)

                        except Exception as e: 
                            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[33m⚠️>>>> Falha ao selecionar opção de financiamento no Banco Santander!\x1b[0m<<<<')
                            return None
                        try:
                            cpf_input = aguardar_elemento(driver,10,'ID','mat-input-2')
                            cpf_input.send_keys(cliente['cpf'])
                        except Exception as e: pass
                        try:
                            nasc_input = driver.find_element(By.ID, 'mat-input-3')
                            nasc_input.send_keys(cliente['nasc'])
                        except Exception as e: pass
                        try:
                            tel_input = driver.find_element(By.ID, 'mat-input-4')
                            tel_input.send_keys('34997741385')
                        except Exception as e: pass
                        try:
                            proposta_input = driver.find_element(By.ID, 'mat-input-5')
                            valor_proposta = cliente['valor_proposta']
                            if ',' in valor_proposta or '.' in valor_proposta:
                                # Se houver vírgula ou ponto, remover a vírgula (a página entende os decimais)
                                valor_proposta = valor_proposta.replace(',', '').replace('.', '')
                            else:
                                # Se for um número inteiro, adicionar dois zeros no final
                                valor_proposta += '00'

                            proposta_input.send_keys(int(valor_proposta))
                        except Exception as e: pass

                        try:
                            # definir elemento 
                            box_termos_e_condicoes = aguardar_elemento(driver,10,'CSS', 'body > app-root > div > app-identification > div > div.ng-star-inserted > div:nth-child(2) > app-terms-and-conditions > div.col-12.terms > p')
                            # clicar no elemento para selecionar (é necessário?)
                            driver.execute_script("arguments[0].click();", box_termos_e_condicoes)
                            
                            # Dar scroll até o final da caixa
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", box_termos_e_condicoes)
                            checkbox_confirm = aguardar_elemento(driver,5,'CSS','#mat-checkbox-2 > label > span.mat-checkbox-inner-container')
                            sleep(2)
                            driver.execute_script("arguments[0].click();", checkbox_confirm)
                            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0   ✅  Clicou em Confirmo que li e aceito os termos e condições!')
                        except Exception as e: print(e)

                        try:
                            circle1 = driver.execute_script("arguments[0].click();", driver.find_element(By.ID, 'mat-radio-3-input'))
                            circle2 = driver.execute_script("arguments[0].click();", driver.find_element(By.ID, 'mat-radio-6-input'))
                            circle3 = driver.execute_script("arguments[0].click();", driver.find_element(By.ID, 'mat-radio-9-input'))
                        except Exception as e:
                            print(f'\x1b[32m[ {numero_proposta} ]\x1b[0m   Erro ao clicar nos circles')

                        # clicar em Buscar Ofertas
                        try:
                            
                            buscar_ofertas = aguardar_elemento(driver,10,'CSS', 'body > app-root > div > app-identification > div > div.row.identification-submit > div > button')
                            sleep(2)
                            buscar_ofertas.click()
                        
                        except Exception as e: 
                             print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   erro ao clicar no botão buscar ofertas')
                             try:
                                  elemento = aguardar_elemento(driver, 10, 'CSS', 'body > app-root > div > app-identification > div > div.row.identification-submit > div > button')
                                  clicar =  driver.execute_script("arguments[0].click();", elemento)
                                  print('clicou')
                             except Exception as e: print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   erro ao clicar no botão buscar ofertas {e}')
                        try:
                            valor_parcela = WebDriverWait(driver, 60).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'body > app-root > div > app-step-offers-container > app-step-offers-npp > div > div > div.col.offset-md-4.col-md-8.content > div > div.ng-star-inserted > app-step-offer-npp > div:nth-child(2) > div.card-body > div.financied-value > p.financied-total.ng-star-inserted'))
                            )
                            qtde_parcelas = driver.find_element(By.CSS_SELECTOR, 'body > app-root > div > app-step-offers-container > app-step-offers-npp > div > div > div.col.offset-md-4.col-md-8.content > div > div.ng-star-inserted > app-step-offer-npp > div:nth-child(2) > div.card-body > div.financied-value > p.card-text.ng-star-inserted').text
                            qtde_parcelas = qtde_parcelas.split(' ')
                            qtde_parcelas = qtde_parcelas[0]

                            valor_seguro_parcela = driver.find_element(By.CSS_SELECTOR, 'body > app-root > div > app-step-offers-container > app-step-offers-npp > div > div > div.col.offset-md-4.col-md-8.content > div > div.ng-star-inserted > app-step-offer-npp > div:nth-child(2) > div.card-body > div.insurance-value.ng-star-inserted > p.card-text').text
                            valor_seguro_parcela = valor_seguro_parcela.split(' ')
                            valor_seguro_parcela = valor_seguro_parcela[2]
                                                       
                            valor_com_seguro_total = driver.find_element(By.CSS_SELECTOR, 'body > app-root > div > app-step-offers-container > app-step-offers-npp > div > div > div.col.offset-md-4.col-md-8.content > div > div.ng-star-inserted > app-step-offer-npp > div:nth-child(2) > div.card-body > div.insurance-value.ng-star-inserted > p:nth-child(3) > span').text
                            valor_com_seguro_total = valor_com_seguro_total.split(' ')
                            valor_com_seguro_total = valor_com_seguro_total[1]
                             
                        except Exception as e: print(f'\x1b[32m[ {numero_proposta} ]\x1b[0m   Elemento não encontrado: {e}')
                        dados = {
                             'valor_parcela': valor_parcela.text,
                             'qtde_parcelas': qtde_parcelas,
                             'valor_seguro_parcela':valor_seguro_parcela,
                             'valor_com_seguro_total':valor_com_seguro_total
                        }
                        url = 'https://brpioneer.accenture.com/originacao-loj/identification'
                        driver.get(url)

                        ## deslogar e logar novamente para resolver bug dos termos e condições
                        try:
                            # expandir menu {  v  }
                            setinha_baixo = aguardar_elemento(driver, 5, 'CSS', 'body > app-root > app-header > app-header-shopkeeper > div.desktop.d-none.d-md-block > mat-toolbar > span.user-menu.step9 > i')
                            driver.execute_script("arguments[0].click();", setinha_baixo)

                            # clicar em sair
                            botao_sair = aguardar_elemento(driver,5,'CSS','body > app-root > app-header > app-header-shopkeeper > div.desktop.d-none.d-md-block > mat-toolbar > app-menu-profile > mat-card > mat-card-content > mat-list > mat-list-item.mat-list-item.mat-focus-indicator.list-item-image > span > span.mat-ripple.mat-list-item-ripple')
                            driver.execute_script("arguments[0].click();", botao_sair)

                            botao_sim_sair_da_conta = aguardar_elemento(driver, 5, 'CSS', '#mat-dialog-0 > app-exit-page > div:nth-child(4) > div:nth-child(2) > button')
                            driver.execute_script("arguments[0].click();", botao_sim_sair_da_conta)
                            

                            try:
                                botao_gd_sair = aguardar_elemento(driver,5,'CSS','#modal-cancel-button')
                                botao_gd_sair.click()
                            except: pass
                                
                            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[34m>>>> Logout realizado!\x1b[0m')


                            sleep(2)
                        except Exception as e: 
                            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[36m>>>>   ERRO EM DESLOGAR E LOGAR:\n\x1b[32m{e}\x1b[0m')
                            return False

                        return dados
                    except Exception as e: print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   \x1b[33m⚠️>>>> Erro ao acessar página do Santader\n{e}\x1b[0m ')
                
                elif banco == 'btg':
                    driver.switch_to.window(driver.window_handles[1])
                    try:
                        url = 'https://parceiros.empresas.btgpactual.com/b2b/common/clientes/iniciar-cadastro'
                        driver.get(url)
                        sleep(5)
                        try:
                            driver.find_element(By.ID, 'username').send_keys('39291935824')
                            driver.find_element(By.ID, 'password').send_keys('014697')

                            # elemento = driver.find_element(By.CSS_SELECTOR, '#__next > div > div:nth-child(2) > div > div.sc-f30eff5c-0.eHjPAs > div.sc-d6d407fb-0.UoXxj > form > div.ant-row.ant-row-end.gap-4 > div.ant-col.col-xs-12.col-sm-12 > button')
                            elemento = aguardar_elemento(driver, 15, 'CSS','#__next > div > div:nth-child(2) > div > div.sc-f30eff5c-0.eHjPAs > div.sc-d6d407fb-0.UoXxj > form > div.ant-row.ant-row-end.gap-4 > div.ant-col.col-xs-12.col-sm-12 > button')
                            elemento.click()
                        except Exception as e: pass
                    except Exception as e: pass

                    
                    ## verificar se está na tela de token
                    try:
                        try:
                            def verificar_campo_token():
                                    try:
                                        sleep(10)
                                        # verificar se token input está disponível ainda
                                        token0 = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable((By.ID, 'o-session-token-1'))
                                        )
                                        token0.click()
                                        # print('Input de token localizado')
                                        return True
                                    except: return False
                            def inserir_token(numero_proposta):
                                token = receive_mail(numero_proposta)
                                print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m  \x1b[36m   TOKEN RECEBIDO: {token}\x1b[0m')
                                if token == None: token = '000000'
                                token0.send_keys(token)
                            ## encontrou input do token, validar
                           
                           
                            token = receive_mail(numero_proposta)

                            print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m   TOKEN RECEBIDO: {token}')
                            if token == None: token = '000000'
                            try:
                                    token0 = driver.find_element(By.CSS_SELECTOR, '#o-session-token-1')

                                    token0.send_keys(token)
                                    print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m   \x1b[33mTOKEN INSERIDO COM SUCESSO!\x1b[0m')
                                    while True:
                                        status_token = verificar_campo_token()
                                        if status_token == True:
                                            inserir_token(numero_proposta)
                                        else: break                                            
                                        
                                   
                                    
                            except Exception as e: pass

                        except Exception as e:
                             print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m  Erro ao obter token: \x1b[36m\n{e}\x1b[0m')
                    except Exception as e: print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m   >>> Erro ao validar token\n')

                        
                    try:


                        try:
                            driver.get('https://parceiros.empresas.btgpactual.com/b2b/solar/credito-solar/formulario/solicitar')
                            sleep(3)
                            proximo = driver.find_element(By.CSS_SELECTOR, '#single-spa-application\:\@b2b\/solar > o-steps-timeline > o-step-body > o-step-content.p-0.o-step-content.o-step-content--active.hydrated > div.d-flex.mt-4.w-100.justify-content-between.gap-2 > o-button:nth-child(2) > button').click()
                            # Localizar e clicar no botão de seleção
                            select_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CLASS_NAME, "o-select__header"))
                            )
                            select_button.click()

                            option_to_select = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[text()='Ambos']"))
                            )
                            option_to_select.click()

                        except Exception as e: print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m   Erro ao selecionar Operador {e}')

                        try:
                            operador = driver.find_element(By.ID, 'operatorIdentification')
                            operador.send_keys('Camila')
                            operador.send_keys(Keys.ENTER)
                        except Exception as e: print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m   Erro ao selecionar Operador')
                        try:
                            # await message.channel.send(cliente)
                            nome = cliente['nome']
                            nome = nome.replace(' ', '')
                            nome = nome.lower()
                            email = nome +'@kinsolenergia.com.br'
                            cpf = cliente['cpf']
                            driver.find_element(By.ID, 'o-identification').send_keys(cpf)
                            driver.find_element(By.ID, 'o-email').send_keys(email)
                            driver.find_element(By.ID, 'o-electricBillAverage').send_keys('40000')
                            driver.find_element(By.ID, 'o-monthlyBilling').send_keys('400000')
                            valor_solicitado = cliente['valor_proposta']
                            if ',' in valor_solicitado or '.' in valor_solicitado:
                                # Se houver vírgula ou ponto, remover a vírgula (a página entende os decimais)
                                valor_solicitado = valor_solicitado.replace(',', '').replace('.', '')
                            else:
                                # Se for um número inteiro, adicionar dois zeros no final
                                valor_solicitado += '00'
 
                            driver.find_element(By.ID, 'o-projectValue').send_keys(valor_solicitado)
                            driver.find_element(By.ID, 'o-cep').send_keys(cliente['cep'])
                            sleep(5)
                            driver.find_element(By.ID, 'o-number').send_keys('999')
                            driver.execute_script("window.scrollBy(0, 650);")

                            # botão salvar
                            salvar = driver.find_element(By.CSS_SELECTOR, '#single-spa-application\:\@b2b\/solar > o-steps-timeline > o-step-body > o-step-content.p-0.o-step-content.hydrated.o-step-content--active > div.d-flex.w-100.justify-content-between.mt-4 > div:nth-child(1) > o-button > button')
                            driver.execute_script("arguments[0].click();", salvar)
                            
                            sleep(5)
                            # botão proximo
                            driver.find_element(By.CSS_SELECTOR, '#single-spa-application\:\@b2b\/solar > o-steps-timeline > o-step-body > o-step-content.p-0.o-step-content.hydrated.o-step-content--active > div.d-flex.w-100.justify-content-between.mt-4 > div:nth-child(2) > o-button:nth-child(2) > button').click()
                            sleep(5)
                            driver.execute_script("window.scrollBy(0, 650);")

                            aceite = driver.find_element(By.CSS_SELECTOR, '#single-spa-application\:\@b2b\/solar > o-steps-timeline > o-step-body > o-step-content.p-0.o-step-content.hydrated.o-step-content--active > div.d-flex.pt-5.flex-column.gap-2 > div:nth-child(1) > div.d-flex.align-items-center.gap-2 > button')
                            driver.execute_script("arguments[0].click();", aceite)
                            sleep(2)
                            # botão salvar
                            indicar = driver.find_element(By.CSS_SELECTOR, '#single-spa-application\:\@b2b\/solar > o-steps-timeline > o-step-body > o-step-content.p-0.o-step-content.hydrated.o-step-content--active > div.d-flex.pt-5.flex-column.gap-2 > div.d-flex.w-100.justify-content-between.mt-4 > div:nth-child(2) > o-button:nth-child(2) > button')
                            driver.execute_script("arguments[0].click();", indicar)
                            # botao enviar indicação
                            driver.get('https://parceiros.empresas.btgpactual.com/b2b/solar/credito-solar/analise-credito')
                            sleep(5)
                            driver.execute_script("window.scrollBy(0, 650);")

                        except Exception as e:print(f'\x1b[32m[ {numero_proposta} - BTG  ]\x1b[0m   ERROR {e}')
                        try:
                            status_solicitacao = driver.find_element(By.XPATH, '//*[@id="single-spa-application:@b2b/solar"]/div/div[3]/section/div/div/div/div/div[6]/div[1]/div/div[1]/div/table/tbody/tr[1]/td[3]/o-badge/span')
                            print(f'\x1b[32m[ {numero_proposta} - BTG  ]\x1b[0m   {status_solicitacao.text} ')
                            return status_solicitacao.text
                        except Exception as e: print(e)
                    except Exception as e:
                        print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m   >>> Erro ao editar simulação BTG\n{e}')
                    
                elif banco == 'bv':
                    # muda para a primeira aba
                    driver.switch_to.window(driver.window_handles[0])
                    url = 'https://instalador.meufinanciamentosolar.com.br/dashboard/home'
                    driver.get(url)
                    sleep(3)
                    
                
                    try: 
                        driver.find_element(By.ID, 'email').send_keys('sac@kinsolenergia.com.br')
                        driver.find_element(By.ID, 'password').send_keys('BA8jkFeY*')
                        driver.find_element(By.ID, 'login-form_button').click()
                        sleep(3)
                    except Exception as e: print(f'\x1b[32m[ {numero_proposta} - BANCO BV ]\x1b[0m   \x1b[33m>>><<<<')
                    try:
                        driver.get('https://instalador.meufinanciamentosolar.com.br/dashboard/proposals-create')
                        sleep(2)

                        driver.find_element(By.ID, 'installer_info_cnpj').send_keys('18.902.786/0001-06')
                        driver.find_element(By.ID, 'installer_info_email').send_keys('camilacaetano.kinsol@gmail.com')
                        driver.find_element(By.ID, 'value').clear()
                        valor_proposta = cliente['valor_proposta']
                        if ',' in valor_proposta:
                                valor_proposta = valor_proposta.split(',')[0]

                        elif  '.' in valor_proposta:
                                # Se houver vírgula ou ponto, remover a vírgula (a página entende os decimais)
                                valor_proposta = valor_proposta.split('.')[0]
                                # valor_proposta = valor_proposta.replace(',', '').replace('.', '')

                        driver.find_element(By.ID, 'value').send_keys(valor_proposta)

                        driver.find_element(By.ID, 'name').send_keys(cliente['nome'])
                        driver.find_element(By.ID, 'cnpj_cpf').send_keys(cliente['cpf'])
                        driver.find_element(By.ID, 'postalcode').send_keys(cliente['cep'])
                        driver.find_element(By.ID, 'birthdate').send_keys(cliente['nasc'])

                        driver.find_element(By.CSS_SELECTOR, '#app-container > main > div > div > div > div > form > div:nth-child(8) > button').click()
                        sleep(10)
                        try:
                            parcela1 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(1) > button').text
                            parcela2 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(2) > button').text
                            parcela3 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(3) > button').text
                            parcela4 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(4) > button').text
                            parcela5 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(5) > button').text
                            parcela6 = driver.find_element(By.CSS_SELECTOR, '#installmentsButtons > div:nth-child(6) > button').text
                            total_financiado_bv = driver.find_element(By.CSS_SELECTOR, '#app-container > main > div > div > div > div > form > p.resultsFinancedValue > strong').text
                            # driver.find_element(By.CSS_SELECTOR, '#app-container > main > div > div > div > div > header > div:nth-child(1) > h1').send_keys(Keys.PAGE_DOWN)

                            driver.execute_script("window.scrollBy(0, 400);")
                            print(f'\x1b[32m[ {numero_proposta} - BANCO BV ]\x1b[33m Valor da parcela  {parcela1}\x1b[0m')
                            parcelamento = {
                                'parcelamento1': parcela1,
                                'parcelamento2': parcela2,
                                'parcelamento3': parcela3,
                                'parcelamento4': parcela4,
                                'parcelamento5': parcela5,
                                'parcelamento6': parcela6,
                                'total_financiado': total_financiado_bv
                            }
                        except Exception as e:
                            try:
                                
                                modal = driver.find_element(By.CSS_SELECTOR, '#myModal > div > div.modal-body-initial').text
                            except:    pass
                    except Exception as e: 
                        print(f'\x1b[32m[ {numero_proposta} - BANCO BV ]\x1b[0m   \x1b[33m>>>Erro ao editar banco bv\x1b[0m<<<<{e}')
                        parcelamento = None

                    # Salvar a captura de tela
                    
                    return parcelamento

class APIHandler:
    buffer = []
    @app.get('/financiamento', methods=['POST'])
    async def financiamento():
        try:
            data = request.json

            print(f'CHAMOU API {data}')
            # identificar a proposta que foi enviada para adicionar ao array de buffer
            numero_proposta = data.get('numero_proposta', 'Proposta não especificada')
            APIHandler.buffer.append(numero_proposta)

            # Semafaro para limitar processos simultaneos na API
            with semaphore:
                    status_santander = None
                    status_btg = None
                    status_bv = None
                # Seção crítica: Apenas 5 threads podem entrar aqui simultaneamente
                    instances_running = semaphore._value
                    data = request.json
                    print(f'Buffer: {APIHandler.buffer}')
                    driver = abrir_navegador(0)
                    cpf = data.get('cpf', 'CPF não especificado')
                    valor_proposta = data.get('valor_proposta', 'Valor não especificado')
                    print(
                        f'\x1b[31m>>> NOVA CHAMADA DE API RECEBIDA <<<<\x1b[32m\n\n    vagas disponíveis no buffer: {instances_running} \n\n'
                        f'Proposta recebida: \x1b[31m{numero_proposta}\x1b[32m\n'
                        f'CPF: \x1b[31m{cpf}\x1b[32m\n'
                        f'Valor da Proposta: \x1b[31m R$ {valor_proposta}\x1b[32m\n'
                    )
                    
                    contador = 0
                    while True:
                        contador += 1
                        if contador >= 5:
                             santander_status = 'Sistema do Banco Santander Indisponível, tente novamente mais tarde!'
                             break
                        santander_status = acessar_banco('santander',data,driver)

                        
                        if santander_status == None:
                            tempo = random.randint(0,5)
                            print(f'\x1b[32m[ {numero_proposta} - SANTANDER ]\x1b[0m   Banco Santander com erro, tentando novamente em {tempo} segundos')
                            sleep(tempo)
                        
                        else: break
                    contador = 0
                    while True:
                        contador += 1
                        if contador >= 3:
                             btg_status = 'Sistema do Banco BTG Indisponível, tente novamente mais tarde!'
                             break
                        btg_status = acessar_banco('btg',data,driver)
                        if btg_status == None:
                            print(f'\x1b[32m[ {numero_proposta} - BTG ]\x1b[0m   Banco BTG com erro, tentando novamente!')
                            tempo = random.randint(5,10)
                            sleep(tempo)
                        else: break
                    contador = 0
                    while True:
                        contador += 1
                        if contador >= 5:
                             bv_status = 'Sistema BV Financeira Indisponível, tente novamente mais tarde'
                             break
                        bv_status = acessar_banco('bv',data,driver)
                        if bv_status == None:
                            print(f'\x1b[32m[ {numero_proposta} ]\x1b[0m   Banco BV com erro, tentando novamente!')
                        else: break
                        
                    response = {
                            'data_recebido': data,
                            'status_santander':santander_status,
                            'status_btg':btg_status,
                            'status_bv':bv_status,
                    }
                    # sleep(300)
                    driver.quit()
                    APIHandler.buffer.remove(numero_proposta)  # Remover a proposta do buffer (processo finalizado!)
                    print(f'\x1b[32m[ {numero_proposta} ]\x1b[0m   FINAL DA EXECUÇÃO!')

                    return jsonify(response)


        except Exception as e:
            try:
                driver.close()
                driver.quit()
            except:
                pass
            return jsonify(e)

    @app.get('/verificar_buffer_financiamento', methods=['POST'])
    async def verificar_buffer_financiamento():
        try:
            buffer = APIHandler.buffer
            return buffer
        except Exception as e: print(f'Erro ao verificar buffer: {e}')    
       
