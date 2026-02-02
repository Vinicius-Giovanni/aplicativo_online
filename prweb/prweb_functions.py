from playwright.sync_api import sync_playwright
from settings.chromium_settings import launch_chromium_custom
from settings.config import sp_rotas
import re
from tabulate import tabulate
from logging import getLogger


logger = getLogger("RPA")

def start_browser():
    """
    Configura e inicia a instancia
    """

    playwright = sync_playwright().start()
    browser, page = launch_chromium_custom(playwright)
    return playwright, browser, page

def emissao_de_carga(page,
                empresa,
                matricula,
                password,
                data: str):
    
    """
    Realiza a emissao das cargas
    """
    
    logger.info("Iniciando emissão de carga")

    carga_de_entrega = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr/td[1]/table/tbody/tr[11]/td[1]/input")
    carga_de_entrega.click()

    consulta = page.locator('xpath=//*[@id="NM_BOT_CON"]')
    consulta.click()

    cargas_fracionada = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr[5]/td[1]/input")
    cargas_fracionada.click()

    processa = page.locator('xpath=//*[@id="NM_BOT_PRC"]')
    processa.click()

    matricula_1 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[5]/input[1]")
    matricula_1.clear()
    matricula_1.type(empresa)

    matricula_2 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[6]/input[1]")
    matricula_2.type(matricula)

    for rota in sp_rotas:

        page.wait_for_timeout(500)

        senha = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[7]/b/input")
        senha.type(password)
        page.wait_for_timeout(500)

        rota_1 = page.locator("xpath=/html/body/form/table[5]/tbody/tr[1]/td[6]/input[1]")
        rota_1.type("sp")
        page.wait_for_timeout(500)

        rota_2 = page.locator("xpath=/html/body/form/table[5]/tbody/tr[1]/td[6]/input[3]")
        rota_2.type(rota)
        page.wait_for_timeout(500)

        dt_entrega = page.locator("xpath=/html/body/form/table[5]/tbody/tr[1]/td[8]/input[1]")
        dt_entrega.type(data)
        page.wait_for_timeout(500)

        sem_emissao_nf = page.locator("xpath=/html/body/form/table[6]/tbody/tr/td/input[1]")
        sem_emissao_nf.click()
        page.wait_for_timeout(500)

        processa = page.locator('xpath=//*[@id="NM_BOT_PRC"]')
        processa.click()
        page.wait_for_timeout(500)

        # Verificação de caixa de dialog
        def handle_dialog(dialog):
            dialog.accept()
            logger.info("Caixa de confirmação ACEITA")
        
        page.once("dialog", handle_dialog)
        page.wait_for_timeout(500)

        if page.locator("xpath=/html/body/form/table[8]/tbody/tr[1]/td").count() > 0:
            qtd_carga_string = page.locator("xpath=/html/body/form/table[8]/tbody/tr[1]/td").inner_text()
            page.wait_for_timeout(500)
            qtd_carga_int = int(re.search(r"\d+",qtd_carga_string).group())
        
            tabela = []
            
            while True:
                
                qtd_carga_string = page.locator("xpath=/html/body/form/table[8]/tbody/tr[1]/td").inner_text()
                qtd_carga_int = int(re.search(r"\d+",qtd_carga_string).group())
                logger.info(f"Quantidade de cargas exibidas: {qtd_carga_int} da rota {rota}")
                    
                for i in range(1, qtd_carga_int * 3 + 1, 3):

                    id = i

                    # ============== Extração de Carga ==============

                    def resolve_xpath_carga(page, i):
                        base = f"/html/body/form/table[8]/tbody/tr[2]/td/table[{i}]/tbody/tr/td[2]"
                        xpath_com_a = base + "/a"

                        if page.locator(f"xpath={xpath_com_a}").count() > 0:
                            return xpath_com_a
                        else:
                            return base

                    xpath_carga = resolve_xpath_carga(page, i)

                    # logger.info(f"Path:\n",xpath,"\n")

                    carga_ = page.locator(f"xpath={xpath_carga}").inner_text()
                    carga = re.search(r"\d+", carga_).group()

                    # ============== Extração de Status da Carga ==============

                    xpath_status_carga = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i}]/tbody/tr/td[2]").inner_text()

                    if "Aberta" in xpath_status_carga:
                        status_carga = "Aberta"
                    elif "Fechada" in xpath_status_carga:
                        status_carga = "Fechada"

                    # ============== Extração de Valor no Box ==============

                    xpath_valor_box = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i+1}]/tbody/tr[1]/td[2]/input[1]").input_value()

                    if xpath_valor_box == "":
                        v_valor = 'vazio'
                    else:
                        v_valor = 'preenchido'

                    # ============== Extração de Status CHECKBOX Emite ==============

                    xpath_checkbox_emite = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i+2}]/tbody/tr/td/table/tbody/tr/td[3]/input")

                    # ============== Extração de transportadora ==============

                    xpath_transportadora = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i+1}]/tbody/tr[9]/td[2]").inner_text()

                    # ============== Condição: Se o status_carga for "Fechado" a checkbox EMITE deve ser "checked" ==============

                    def get_checkbox_state(locator):
                        return (
                            "disabled" if locator.get_attribute("disabled") is not None
                            else "checked" if locator.is_checked()
                            else "unchecked"
                        )
                    
                    estado_checkbox_antes = get_checkbox_state(xpath_checkbox_emite)

                    if status_carga == "Fechada" and v_valor == 'preenchido': # <<< Status da carga = 'Fechada' e valor do box estiver preenchido

                        if estado_checkbox_antes == "unchecked": # <<< Checkbox estiver desmarcado
                            xpath_checkbox_emite.click() # <<< Marca checkbox
                    
                    elif status_carga == "Fechada" and v_valor == 'vazio': # <<< Status da carga = 'Fechada' e valor do box estiver vazio

                        if estado_checkbox_antes == "checked": # <<< Checkbox estiver marcada
                            xpath_checkbox_emite.click() # <<< Desmarca checkbox

                    elif status_carga == "Fechada" and "ANJUN" in xpath_transportadora: # status da carga = 'Fechada' e 'ANJUN' escrito no campo de transportadora

                        if estado_checkbox_antes == "checked":
                            xpath_checkbox_emite.click()
                        
                    elif status_carga == "Aberta": # <<< Status da carga = 'Aberta'

                        if estado_checkbox_antes == "checked": # <<< Checkbox estiver marcada
                            xpath_checkbox_emite.click() # <<< Desmarca checkbox

                    estado_checkbox_depois = get_checkbox_state(xpath_checkbox_emite)

                    # ============== Tabela ==============

                    linha = {
                        "Rota": rota,
                        "Nº Carga": carga,
                        "Transportadora": xpath_transportadora,
                        "Status da Carga": status_carga,
                        "Botão Emite Antes": estado_checkbox_antes,
                        "Botão Emite Depois":estado_checkbox_depois
                        }

                    tabela.append(linha)

                if qtd_carga_int < 55: # <<< Processa, limpa e finalizada
                    page.locator('xpath=//*[@id="NM_BOT_PRC"]').click()
                    page.wait_for_timeout(500)

                    page.once("dialog", handle_dialog)
                    
                    page.wait_for_timeout(500)

                    page.locator('xpath=//*[@id="NM_BOT_LIM"]').click()
                    page.wait_for_timeout(500)
                    break

                elif qtd_carga_int == 55: # <<< Avança
                    btn_avancar = page.locator('xpath=//*[@id="NM_BOT_AVA"]')
                    if btn_avancar.is_visible() and btn_avancar.is_enabled():
                        btn_avancar.click()
                    else:
                        page.locator('xpath=//*[@id="NM_BOT_PRC"]').click()
                        page.wait_for_timeout(500)

                        page.once("dialog", handle_dialog)
                        
                        page.wait_for_timeout(500)

                        page.locator('xpath=//*[@id="NM_BOT_LIM"]').click()
                        page.wait_for_timeout(500)
                        break

        else:  
            logger.info(f"Zero cargas encontradas para a rota {rota}")
            logger.info(f"Ignorando rota {rota} e indo para a próxima rota...")

            page.locator('xpath=//*[@id="NM_BOT_RET"]').click() # <<< Retorna
            page.wait_for_timeout(500)
            page.locator('xpath=/html/body/form[1]/table[3]/tbody/tr[5]/td[1]/input').click() # <<< Seleciona Cargas de entrega geral - Fracionada
            page.wait_for_timeout(500)
            page.locator('xpath=//*[@id="NM_BOT_PRC"]').click() # <<< Processa
            page.wait_for_timeout(500)
            matricula_1 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[5]/input[1]")
            matricula_1.clear()
            matricula_1.type(empresa)
            page.wait_for_timeout(500)
            matricula_2 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[6]/input[1]")
            matricula_2.type(matricula)
            continue

        logger.info("TABELA BOXIAMENTO DE CARGAS")
        logger.info(tabulate(tabela, headers="keys", tablefmt="grid"))

def login_prweb(page,
                empresa,
                matricula,
                password):
    """
    Realiza o login
    """

    url = "https://prweb01/bahia/gateway?hptAppId=W1A1&hptExec=Y"

    page.goto(url)

    page.wait_for_timeout(500)
    page.locator("b", has_text="Aplicações WEB").wait_for()
    logger.info("Página carregada com sucesso")

    logger.info("Etapa login iniciada")
    page.wait_for_timeout(500)
    input_empresa = page.locator("xpath=/html/body/form[1]/table[1]/tbody/tr[1]/td[1]/input[1]")
    input_empresa.type(empresa) # ID empresa

    page.wait_for_timeout(500)
    matricula_ = page.locator("xpath=/html/body/form[1]/table[1]/tbody/tr[1]/td[2]/input[1]")
    matricula_.type(matricula) # Matricula

    page.wait_for_timeout(500)
    senha = page.locator("xpath=/html/body/form[1]/table[1]/tbody/tr[1]/td[3]/b[1]/input")
    senha.type(password) # Senha
    page.wait_for_timeout(500)

    processa = page.locator("xpath=/html/body/form[1]/table[2]/tbody/tr/td[2]/input")
    processa.click()
    logger.info("Etapa login finalizada")

    roteirizacao = page.locator('select[name="U01_DS_APL_VIS_SLC"]')
    roteirizacao.select_option(label="Roteirizacao")
    processa.click()
    
    empresa_2 = page.locator("xpath=/html/body/form[1]/table[2]/tbody/tr/td[2]/input[1]")
    empresa_2.clear()
    empresa_2.type('21') # ID empresa novamente

    filial = page.locator("xpath=/html/body/form[1]/table[2]/tbody/tr/td[3]/input[1]")
    filial.type("1200") # Filial

    tipo_ativ = page.locator("xpath=/html/body/form[1]/table[2]/tbody/tr/td[4]/input[1]")
    tipo_ativ.type("D") # Tipo ativ.

    page.wait_for_timeout(500)

def filtragem_de_carga(page,
                empresa,
                matricula,
                password,
                dt_limite_exp_retro: str = "",
                dt_limite_exp_posterior: str = "",
                dt_limite_exp_start: str = "",
                dt_limite_exp_end: str = "",
                mono: str = "Não",
                multiplo: str = "Não",
                B2B: str = "Não",
                B2C: str = "Não",
                CROSSDOCKING: str = "Não",
                dt_entrega: str = "",
                modalidade= "OUTRAS TRANSPORTADORAS (LEVE)" or "ENTREGA PELOS CORREIOS"):

    """
    Faz a filtragem das cargas\n
    page: herdado da função login_prweb\n
    dt_limite_exp_retro: Data limite de expedição retroativa (DDMMAAAA)\n
    dt_limite_exp_posterior: Data limite de expedição posterior (DDMMAAAA)\n
    dt_limite_exp_start: Data limite de expedição inicial (DDMMAAAA)\n
    dt_limite_exp_end: Data limite de expedição final (DDMMAAAA)\n
    mono: Seleção de cargas monotransportadas (Sim/Não)\n
    multiplo: Seleção de cargas multitransportadas (Sim/Não)\n
    B2B: Seleção de cargas B2B (Sim/Não)\n
    B2C: Seleção de cargas B2C (Sim/Não)\n
    CROSSDOCKING: Seleção de cargas CROSSDOCKING (Sim/Não)\n
    dt_entrega: Data de entrega (DDMMAAAA)\n
    modalidade: Modalidade da rota (OUTRAS TRANSPORTADORAS (LEVE) ou ENTREGA PELOS CORREIOS)
    """

    logger.info("Iniciando filtragem das cargas")

    documento_carga = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr/td[1]/table/tbody/tr[13]/td[1]/input")
    documento_carga.click() # Checkbox Documentos/Carga

    transfere = page.locator('xpath=//*[@id="NM_BOT_TRA"]')
    transfere.click() # transfere

    transportadora_sku = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr[3]/td[1]/input")
    transportadora_sku.click() # Checkbox Documento de carga por transportador/sku

    processa_1 =  page.locator('xpath=//*[@id="NM_BOT_PRC"]')
    processa_1.click()

    # Preenchimento de login ==========
    empresa_ = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[5]/input[1]")
    empresa_.clear()
    empresa_.type(empresa)

    matricula_1 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[6]/input[1]")
    matricula_1.type(matricula)

    senha_1 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[7]/b[1]/input")
    senha_1.type(password)
    page.wait_for_timeout(500)

    modalidade_da_rota = page.locator("select[name='U01_MOD_ROTETG_SLC']")
    modalidade_da_rota.select_option(label=modalidade) # <<< Procurar por valor e não posição
    modalidade_da_rota.click()

    data_limite_de_expedicao_retroativa = page.locator("xpath=/html/body/form/table[4]/tbody/tr[6]/td[2]/input[1]")
    data_limite_de_expedicao_retroativa.type(dt_limite_exp_retro)

    data_limite_exp_posterior = page.locator("xpath=/html/body/form/table[4]/tbody/tr[7]/td[2]/input[1]")
    data_limite_exp_posterior.type(dt_limite_exp_posterior)

    data_limite_exp_inicial = page.locator("xpath=/html/body/form/table[4]/tbody/tr[8]/td[2]/input[1]")
    data_limite_exp_inicial.type(dt_limite_exp_start)

    data_limite_exp_final = page.locator("xpath=/html/body/form/table[4]/tbody/tr[8]/td[2]/input[3]")
    data_limite_exp_final.type(dt_limite_exp_end)

    data_entrega = page.locator("xpath=/html/body/form/table[4]/tbody/tr[10]/td[2]/input[1]")
    data_entrega.type(dt_entrega)
    
    # Seleção de tipos de carga
    if mono == "Sim":
        page.locator("xpath=/html/body/form/table[4]/tbody/tr[12]/td[2]/input[1]").click()
        logger.info("Cargas monotransportadas selecionadas")
    elif multiplo == "Sim":
        page.locator("xpath=/html/body/form/table[4]/tbody/tr[12]/td[2]/input[2]").click()
        logger.info("Cargas multitransportadas selecionadas")
    elif B2B == "Sim":
        page.locator("xpath=/html/body/form/table[4]/tbody/tr[14]/td[2]/input[1]").click()
        logger.info("Cargas B2B selecionadas")
    elif B2C == "Sim":
        page.locator("xpath=/html/body/form/table[4]/tbody/tr[14]/td[2]/input[2]").click()
        logger.info("Cargas B2C selecionadas")
    elif CROSSDOCKING == "Sim":
        page.locator("xpath=/html/body/form/table[4]/tbody/tr[16]/td[2]/input").click()
        logger.info("Cargas CROSSDOCKING selecionadas")

    # Verificação de caixa de dialog
    def handle_dialog(dialog):
        dialog.accept()
        logger.info("Caixa de confirmação ACEITA")
    
    page.once("dialog", handle_dialog)
    page.wait_for_timeout(500)

    button_processa =  page.locator('xpath=//*[@id="NM_BOT_PRC"]')
    button_processa.click()
    page.wait_for_timeout(5000)

    # Dados tabela
    logger.info("Tabela de resultados:\n")
    pedidos_selecionados = page.locator("xpath=/html/body/form/table[5]/tbody/tr/td[2]").inner_text()
    logger.info("Pedidos Selecionados:", pedidos_selecionados)

    pedidos_selecionados_mono = page.locator("xpath=/html/body/form/table[6]/tbody/tr/td[2]").inner_text()
    logger.info("Pedidos Selecionados Mono:", pedidos_selecionados_mono)

    pedidos_selecionados_multl = page.locator("xpath=/html/body/form/table[7]/tbody/tr/td[2]").inner_text()
    logger.info("Pedidos Selecionados Multliplo:", pedidos_selecionados_multl,"\n")
    logger.info("Resumo\n")

    qtd_cargas = page.locator("xpath=/html/body/form/table[8]/tbody/tr[2]/td[2]").inner_text()
    logger.info("Quantidade de cargas:", qtd_cargas)
    qtde_transportadoras = page.locator("xpath=/html/body/form/table[8]/tbody/tr[3]/td[2]").inner_text()
    logger.info("Quantidade de transportadoras:", qtde_transportadoras)
    pedidos_processados = page.locator("xpath=/html/body/form/table[8]/tbody/tr[4]/td[2]").inner_text()
    logger.info("Pedidos processados:", pedidos_processados)

    page.wait_for_timeout(5000)

    menu = page.locator('xpath=//*[@id="NM_BOT_MEU"]')
    menu.click()

    page.wait_for_timeout(500)

def boxiamento_carga(page,
                    empresa,
                    matricula,
                    password,
                    data):
    """
    Realiza o boxiamento
    """
    logger.info("Iniciando boxiamento de notas fiscais")


    carga_de_entrega = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr/td[1]/table/tbody/tr[11]/td[1]/input")
    carga_de_entrega.click()

    consulta = page.locator('xpath=//*[@id="NM_BOT_CON"]')
    consulta.click()

    cargas_fracionada = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr[5]/td[1]/input")
    cargas_fracionada.click()

    processa = page.locator('xpath=//*[@id="NM_BOT_PRC"]')
    processa.click()

    matricula_1 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[5]/input[1]")
    matricula_1.clear()
    matricula_1.type(empresa)
    page.wait_for_timeout(500)

    matricula_2 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[6]/input[1]")
    matricula_2.type(matricula)
    page.wait_for_timeout(500)

    for rota in sp_rotas:
        
        page.wait_for_timeout(500)

        senha = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[7]/b/input")
        senha.type(password)
        page.wait_for_timeout(500)

        rota_1 = page.locator("xpath=/html/body/form/table[5]/tbody/tr[1]/td[6]/input[1]")
        rota_1.type("sp")
        page.wait_for_timeout(500)

        rota_2 = page.locator("xpath=/html/body/form/table[5]/tbody/tr[1]/td[6]/input[3]")
        rota_2.type(rota)
        page.wait_for_timeout(500)

        dt_entrega = page.locator("xpath=/html/body/form/table[5]/tbody/tr[1]/td[8]/input[1]")
        dt_entrega.type(data)
        page.wait_for_timeout(500)

        sem_emissao_nf = page.locator("xpath=/html/body/form/table[6]/tbody/tr/td/input[1]")
        sem_emissao_nf.click()
        page.wait_for_timeout(500)

        processa = page.locator('xpath=//*[@id="NM_BOT_PRC"]')
        processa.click()
        page.wait_for_timeout(500)

        # Verificação de caixa de dialog
        def handle_dialog(dialog):
            dialog.accept()
            logger.info("Caixa de confirmação ACEITA")
        
        page.once("dialog", handle_dialog)
        page.wait_for_timeout(500)

        if page.locator("xpath=/html/body/form/table[8]/tbody/tr[1]/td").count() > 0:
            qtd_carga_string = page.locator("xpath=/html/body/form/table[8]/tbody/tr[1]/td").inner_text()
            page.wait_for_timeout(500)
            qtd_carga_int = int(re.search(r"\d+",qtd_carga_string).group())
        
            tabela = []
            
            while True:
                
                qtd_carga_string = page.locator("xpath=/html/body/form/table[8]/tbody/tr[1]/td").inner_text()
                qtd_carga_int = int(re.search(r"\d+",qtd_carga_string).group())
                logger.info(f"Quantidade de cargas exibidas: {qtd_carga_int} da rota {rota}")
                    
                for i in range(1, qtd_carga_int * 3 + 1, 3):

                    id = i

                    # ============== Extração de Carga ==============

                    def resolve_xpath_carga(page, i):
                        base = f"/html/body/form/table[8]/tbody/tr[2]/td/table[{i}]/tbody/tr/td[2]"
                        xpath_com_a = base + "/a"

                        if page.locator(f"xpath={xpath_com_a}").count() > 0:
                            return xpath_com_a
                        else:
                            return base

                    xpath_carga = resolve_xpath_carga(page, i)

                    # logger.info(f"Path:\n",xpath,"\n")

                    carga_ = page.locator(f"xpath={xpath_carga}").inner_text()
                    carga = re.search(r"\d+", carga_).group()

                    # ============== Extração de Status da Carga ==============

                    xpath_status_carga = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i}]/tbody/tr/td[2]").inner_text()

                    if "Aberta" in xpath_status_carga:
                        status_carga = "Aberta"
                    elif "Fechada" in xpath_status_carga:
                        status_carga = "Fechada"

                    # ============== Extração de Valor no Box ==============

                    xpath_valor_box = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i+1}]/tbody/tr[1]/td[2]/input[1]")

                    # ============== Extração de Status CHECKBOX Emite ==============

                    xpath_checkbox_emite = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i+2}]/tbody/tr/td/table/tbody/tr/td[3]/input")

                    # ============== Extração de contrato ==============

                    xpath_contrato_ = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i+1}]/tbody/tr[10]/td[2]")

                    if xpath_contrato_.count() == 0:
                        if status_carga == "Fechada" and "ANJUN" in xpath_transportadora:
                            if estado_checkbox_antes == "checked":
                                xpath_checkbox_emite.click()
                        
                        elif status_carga == "Fechada":
                            if estado_checkbox_antes == "unchecked":
                                xpath_checkbox_emite.click()
                        
                        logger.info("Contrato não encontrado")
                        continue

                    xpath_contrato = xpath_contrato_.inner_text()
                        
                    # ============== Extração de transportadora ==============

                    xpath_transportadora = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i+1}]/tbody/tr[9]/td[2]").inner_text()

                    # ============== Condição: Se o status_carga for "Fechado" a checkbox EMITE deve ser "checked" ==============

                    def get_checkbox_state(locator):
                        return (
                            "disabled" if locator.get_attribute("disabled") is not None
                            else "checked" if locator.is_checked()
                            else "unchecked"
                        )
                    
                    estado_checkbox_antes = get_checkbox_state(xpath_checkbox_emite)

                    # ============== Lógica de Checkbox Emite ==============
                    if status_carga == "Fechada" and "ANJUN" in xpath_transportadora: # status da carga = 'Fechada' e 'ANJUN' escrito no campo de transportadora

                        if estado_checkbox_antes == "checked":
                            xpath_checkbox_emite.click()
                    
                    elif status_carga == "Fechada" : # <<< Status da carga = 'Fechada'

                        if estado_checkbox_antes == "unchecked": # <<< Checkbox estiver desmarcado
                            xpath_checkbox_emite.click() # <<< Marca checkbox
                        
                    elif status_carga == "Aberta": # <<< Status da carga = 'Aberta'

                        if estado_checkbox_antes == "checked": # <<< Checkbox estiver marcada
                            xpath_checkbox_emite.click() # <<< Desmarca checkbox

                    estado_checkbox_depois = get_checkbox_state(xpath_checkbox_emite)

                    # ============== Lógica de Boxiamento ==============
                    box = ""
                    v_box = xpath_valor_box.input_value()

                    if status_carga == "Fechada": # <<< Status da carga = 'Fechada' e valor do box estiver vazio
                        
                        if v_box == "999":
                            if estado_checkbox_antes == "checked": # <<< Checkbox estiver desmarcado
                                xpath_checkbox_emite.click() # <<< Desmarca checkbox

                        elif "ANJUN" in xpath_transportadora:
                            xpath_valor_box.clear()

                        # Boxiamento levando em considerações a rota inserida

                        if rota == "2872":
                            xpath_valor_box.clear()
                            box = "840"
                            xpath_valor_box.type(box)
                        
                        elif rota == "2873":
                            xpath_valor_box.clear()
                            box = "871"
                            xpath_valor_box.type(box)

                        elif rota == "2874":
                            xpath_valor_box.clear()
                            box = "872"
                            xpath_valor_box.type(box)
                        
                        elif rota == "2875":
                            xpath_valor_box.clear()
                            box = "871"
                            xpath_valor_box.type(box)

                         # Boxiamento levando em consideração o contrato

                        elif "JT TRANSPORTES" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "849"
                            xpath_valor_box.type(box)

                        elif "PACIFICO" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "843"
                            xpath_valor_box.type(box)

                        elif "BRASIL WEB" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "847"
                            xpath_valor_box.type(box)

                        elif "LOGAN" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "842"
                            xpath_valor_box.type(box)

                        elif "VENKON" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "844"
                            xpath_valor_box.type(box)

                        elif "SEDEX" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "850"
                            xpath_valor_box.type(box)

                        elif "L MEGA 1200>1624" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "840"
                            xpath_valor_box.type(box)

                        elif "L MEGA 1200>1475" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "871"
                            xpath_valor_box.type(box)

                        elif "L MEGA 1200>1500" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "872"
                            xpath_valor_box.type(box)

                        elif "L MEGA 1200>1760" in xpath_contrato:
                            xpath_valor_box.clear()
                            box = "871"
                            xpath_valor_box.type(box)

                        # Boxiameno levando em consideração a transportadora

                        elif "TRILOG" in xpath_transportadora:
                            xpath_valor_box.clear()
                            box = "839"
                            xpath_valor_box.type(box)

                        elif "ASAP LOG" in xpath_transportadora:
                            xpath_valor_box.clear()
                            box = "870"
                            xpath_valor_box.type(box)

                    # ============== Tabela ==============

                    linha = {
                        "Rota": rota,
                        "Nº Carga": carga,
                        "Transportadora": xpath_transportadora,
                        "Box": box,
                        "Status da Carga": status_carga,
                        "Botão Emite Antes": estado_checkbox_antes,
                        "Botão Emite Depois":estado_checkbox_depois
                        }

                    tabela.append(linha)

                if qtd_carga_int < 55: # <<< Processa, limpa e finalizada
                    page.locator('xpath=//*[@id="NM_BOT_PRC"]').click()
                    page.wait_for_timeout(500)

                    page.once("dialog", handle_dialog)
                    
                    page.wait_for_timeout(500)

                    page.locator('xpath=//*[@id="NM_BOT_LIM"]').click()
                    page.wait_for_timeout(500)
                    break

                elif qtd_carga_int == 55: # <<< Avança
                    btn_avancar = page.locator('xpath=//*[@id="NM_BOT_AVA"]')
                    if btn_avancar.is_visible() and btn_avancar.is_enabled():
                        btn_avancar.click()
                    else:
                        page.locator('xpath=//*[@id="NM_BOT_PRC"]').click()
                        page.wait_for_timeout(500)

                        page.once("dialog", handle_dialog)
                        
                        page.wait_for_timeout(500)

                        page.locator('xpath=//*[@id="NM_BOT_LIM"]').click()
                        page.wait_for_timeout(500)
                        break

        else:  
            logger.info(f"Zero cargas encontradas para a rota {rota}")
            logger.info(f"Ignorando rota {rota} e indo para a próxima rota...")

            page.locator('xpath=//*[@id="NM_BOT_RET"]').click() # <<< Retorna
            page.wait_for_timeout(500)
            page.locator('xpath=/html/body/form[1]/table[3]/tbody/tr[5]/td[1]/input').click() # <<< Seleciona Cargas de entrega geral - Fracionada
            page.wait_for_timeout(500)
            page.locator('xpath=//*[@id="NM_BOT_PRC"]').click() # <<< Processa
            page.wait_for_timeout(500)
            matricula_1 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[5]/input[1]")
            matricula_1.clear()
            matricula_1.type(empresa)
            page.wait_for_timeout(500)
            matricula_2 = page.locator("xpath=/html/body/form/table[3]/tbody/tr/td[6]/input[1]")
            matricula_2.type(matricula)
            continue

        logger.info("TABELA BOXIAMENTO DE CARGAS")
        logger.info(tabulate(tabela, headers="keys", tablefmt="grid"))