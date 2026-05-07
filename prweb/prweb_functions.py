from playwright.sync_api import sync_playwright
from settings.chromium_settings import launch_chromium_custom
from settings.config import AppConfig
import json
import re
from tabulate import tabulate
from logging import getLogger


logger = getLogger("RPA")


def _load_sp_rotas_from_config():
    """
    Carrega a lista de rotas SP a partir do arquivo de configuração.

    A função lê o arquivo de configuração definido em `AppConfig`,
    interpreta seu conteúdo em formato JSON e retorna apenas as rotas
    relacionadas a SP.

    Lógica utilizada:
        - Instancia a configuração da aplicação.
        - Abre o arquivo de rotas definido em `ROTAS_FILE`.
        - Realiza o parsing do conteúdo JSON.
        - Retorna a chave `sp_rotas` caso exista.

    Retorno:
        list:
            Lista de rotas SP. Caso a chave não exista, retorna lista vazia.
    """
    app_config = AppConfig()

    with open(app_config.ROTAS_FILE, "r", encoding="utf-8") as f:
        rotas_data = json.load(f)

    return rotas_data.get("sp_rotas", [])

def _normalize_cargas_box(cargas_box_data):
    """
    Normaliza diferentes formatos de dados de cargas e boxes.

    A função padroniza a estrutura de entrada, garantindo que o retorno
    seja sempre uma lista de dicionários no formato esperado pela aplicação.

    Lógica utilizada:
        - Se a entrada for uma lista:
            * Filtra apenas itens do tipo dict.
            * Normaliza e limpa os campos "carga", "box" e "rota".
            * Ignora registros inválidos (sem box ou sem identificação).
        - Se a entrada for um dict:
            * Converte pares chave/valor em estrutura padrão.
            * Define "rota" como vazio por padrão.
        - Retorna sempre uma lista padronizada de registros válidos.

    Parâmetros:
        cargas_box_data (list | dict):
            Estrutura de dados contendo informações de carga e box.

    Retorno:
        list[dict]:
            Lista normalizada no formato:
            {
                "carga": str,
                "box": str,
                "rota": str
            }
    """
    if isinstance(cargas_box_data, list):
        normalized = []
        for item in cargas_box_data:
            if not isinstance(item, dict):
                continue

            carga = str(item.get("carga", "")).strip()
            box = str(item.get("box", "")).strip()
            rota = str(item.get("rota", "")).strip()

            if not box:
                continue

            if not carga and not rota:
                continue

            normalized.append({"carga": carga, "box": box, "rota": rota})

        return normalized

    normalized = []
    if isinstance(cargas_box_data, dict):
        for carga, box in cargas_box_data.items():
            carga = str(carga).strip()
            if not carga:
                continue

            normalized.append({"carga": carga, "box": str(box).strip(), "rota": ""})

    return normalized

def _normalize_text_for_match(value):
    """
    Normaliza um texto para padronização de comparação.

    A função trata o texto de entrada para facilitar comparações,
    removendo inconsistências de espaçamento e padronizando o formato.

    Lógica utilizada:
        - Converte o valor para string em caixa alta.
        - Remove espaços extras no início e fim.
        - Substitui múltiplos espaços por um único espaço.
        - Normaliza espaços ao redor de caracteres especiais (> e -).

    Parâmetros:
        value:
            Texto de entrada que será normalizado.

    Retorno:
        str:
            Texto normalizado para comparação.
    """
    normalized = str(value or "").upper().strip()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"\s*>\s*", ">", normalized)
    normalized = re.sub(r"\s*-\s*", "-", normalized)
    return normalized

def _resolve_box_for_carga(cargas_box_map, rota_atual, contrato, transportadora):
    """
    Resolve o box correspondente a uma carga com base em regras de prioridade.

    A função aplica um conjunto de regras para determinar o box mais adequado,
    considerando rota, contrato e transportadora.

    Lógica utilizada:
        - Normaliza os parâmetros de entrada para comparação.
        - Separa as regras em três grupos:
            * Somente rota
            * Com rota definida
            * Sem rota definida
        - Aplica a seguinte prioridade de decisão:
            1. Regras com rota e carga vazia (prioridade máxima por rota)
            2. Regras com rota + match em contrato
            3. Regras com rota + match em transportadora
            4. Regras sem rota + match em contrato
            5. Regras sem rota + match em transportadora
        - Retorna o primeiro box que satisfaz a regra.
        - Caso nenhuma regra seja atendida, retorna string vazia.

    Parâmetros:
        cargas_box_map (list[dict]):
            Lista de regras contendo carga, box e rota.

        rota_atual (str):
            Rota atual utilizada como filtro principal.

        contrato (str):
            Informação de contrato usada para matching.

        transportadora (str):
            Nome da transportadora usada para matching.

    Retorno:
        str:
            Box resolvido conforme as regras ou string vazia caso não encontre.
    """
    """
    Resolve o box com suporte a regra somente por rota.

    Ordem de prioridade:
    1) Regras com rota igual à rota atual e carga vazia (ignora contrato/transportadora)
    2) Regras com rota igual à rota atual + match em contrato
    3) Regras com rota igual à rota atual + match em transportadora
    4) Regras sem rota + match em contrato
    5) Regras sem rota + match em transportadora
    """

    rota_atual = str(rota_atual).strip()
    contrato_norm = _normalize_text_for_match(contrato)
    transportadora_norm = _normalize_text_for_match(transportadora)

    regras_somente_rota = []
    regras_com_rota = []
    regras_sem_rota = []

    for regra in cargas_box_map:
        carga_regra = str(regra.get("carga", "")).strip()
        box_regra = str(regra.get("box", "")).strip()
        rota_regra = str(regra.get("rota", "")).strip()

        if not box_regra:
            continue

        carga_regra_norm = _normalize_text_for_match(carga_regra)

        if rota_regra:
            if rota_regra != rota_atual:
                continue

            if not carga_regra_norm:
                regras_somente_rota.append(box_regra)
            else:
                regras_com_rota.append((carga_regra_norm, box_regra))
            continue

        if carga_regra_norm:
            regras_sem_rota.append((carga_regra_norm, box_regra))

    if regras_somente_rota:
        return regras_somente_rota[0]

    for carga_regra_norm, box_regra in regras_com_rota:
        if carga_regra_norm in contrato_norm:
            return box_regra

    for carga_regra_norm, box_regra in regras_com_rota:
        if carga_regra_norm in transportadora_norm:
            return box_regra

    for carga_regra_norm, box_regra in regras_sem_rota:
        if carga_regra_norm in contrato_norm:
            return box_regra

    for carga_regra_norm, box_regra in regras_sem_rota:
        if carga_regra_norm in transportadora_norm:
            return box_regra

    return ""

def _load_cargas_box_from_config():
    """
    Carrega e normaliza a configuração de cargas e boxes.

    A função lê o arquivo de configuração definido em `AppConfig`,
    carrega os dados em formato JSON e aplica normalização para
    padronizar a estrutura utilizada na aplicação.

    Lógica utilizada:
        - Instancia a configuração da aplicação.
        - Abre o arquivo definido em `CARGAS_BOX_FILE`.
        - Carrega os dados em formato JSON.
        - Normaliza os dados utilizando `_normalize_cargas_box`.

    Retorno:
        list[dict]:
            Lista de cargas e boxes já normalizados.
    """
    app_config = AppConfig()

    with open(app_config.CARGAS_BOX_FILE, 'r', encoding='utf-8') as f:
        cargas_box_data = json.load(f)

    return _normalize_cargas_box(cargas_box_data)

def start_browser():
    """
    Inicializa e configura a instância do navegador.

    A função inicia o Playwright em modo síncrono, lança uma instância
    personalizada do Chromium e retorna os objetos necessários para
    controle da automação.

    Lógica utilizada:
        - Inicia o Playwright.
        - Abre o navegador Chromium via configuração customizada.
        - Retorna os objetos de controle da sessão.

    Retorno:
        tuple:
            (playwright, browser, page)
            Instâncias necessárias para controle do navegador.
    """

    playwright = sync_playwright().start()
    browser, page = launch_chromium_custom(playwright)
    return playwright, browser, page

def emissao_de_carga(page,
                empresa,
                matricula,
                password,
                data: str,
                rotas=None):
    
    """
    Executa o processo automatizado de emissão de cargas no sistema web.

    A função utiliza automação de navegador para navegar no sistema,
    processar rotas, extrair informações de cargas e ajustar estados
    de emissão com base nas regras de negócio.

    Lógica utilizada:
        - Inicializa o fluxo de emissão de cargas na interface web.
        - Preenche credenciais e dados operacionais (empresa, matrícula, senha).
        - Obtém lista de rotas (parâmetro ou configuração externa).
        - Para cada rota:
            * Preenche dados de filtro (rota, data e credenciais).
            * Processa a consulta de cargas.
            * Lê quantidade de cargas retornadas.
            * Itera sobre os registros extraindo informações como:
                - código da carga
                - status da carga
                - transportadora
                - estado do box
                - estado do checkbox de emissão
            * Aplica regras condicionais para marcar/desmarcar emissão.
            * Monta tabela de controle da execução.
        - Trata paginação quando necessário.
        - Finaliza processamento de cada rota.
        - Consolida resultados em uma tabela geral.

    Regras principais:
        - Carga "Fechada" com box preenchido ativa emissão.
        - Carga "Fechada" sem box desativa emissão.
        - Carga "Aberta" desativa emissão.
        - Controle de paginação quando limite de registros é atingido.

    Parâmetros:
        page:
            Instância do Playwright responsável pela automação do navegador.

        empresa:
            Código da empresa utilizado no login/processo.

        matricula:
            Identificação do usuário no sistema.

        password:
            Senha de acesso ao sistema.

        data (str):
            Data de referência da emissão.

        rotas (list | None):
            Lista de rotas a serem processadas. Caso não informado,
            utiliza configuração padrão.

    Retorno:
        None
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

    sp_rotas = rotas if rotas else _load_sp_rotas_from_config()

    tabela_geral = []

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
                        """
                        Resolve dinamicamente o XPath da carga na tabela do sistema.

                        A função determina qual estrutura de XPath deve ser utilizada
                        para acessar corretamente o elemento da carga, dependendo da
                        presença de um link (<a>) no nó esperado.

                        Lógica utilizada:
                            - Monta o XPath base da carga com base no índice informado.
                            - Verifica se existe um elemento <a> no caminho esperado.
                            - Se existir, retorna o XPath com link.
                            - Caso contrário, retorna o XPath base.

                        Parâmetros:
                            page:
                                Instância da página do Playwright utilizada para inspeção.

                            i (int):
                                Índice da linha da tabela onde a carga está localizada.

                        Retorno:
                            str:
                                XPath correto para acessar o elemento da carga.
                        """
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
                        """
                        Retorna o estado atual de um checkbox no DOM.

                        A função avalia o elemento e determina se ele está desabilitado,
                        marcado ou desmarcado.

                        Lógica utilizada:
                            - Verifica se o atributo "disabled" está presente.
                            - Caso não esteja desabilitado, verifica se está marcado.
                            - Caso contrário, considera como desmarcado.

                        Parâmetros:
                            locator:
                                Elemento (Playwright Locator) representando o checkbox.

                        Retorno:
                            str:
                                Estado do checkbox:
                                - "disabled"
                                - "checked"
                                - "unchecked"
                        """                        
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

        tabela_geral.extend(tabela)

    if tabela_geral:
        logger.info("TABELA FINAL - EMISSÃO DE CARGAS")
        logger.info(tabulate(tabela_geral, headers="keys", tablefmt="grid"))
    else:
        logger.info("Nenhum registro encontrado para emissão de cargas;")

def login_prweb(page,
                empresa,
                matricula,
                password):
    """
    Realiza o processo de autenticação no sistema PRWEB.

    A função acessa a URL do sistema, preenche os campos de login,
    executa a autenticação e configura a aplicação para o módulo
    de roteirização.

    Lógica utilizada:
        - Abre a URL do sistema PRWEB.
        - Aguarda carregamento da página inicial.
        - Preenche credenciais (empresa, matrícula e senha).
        - Executa o login.
        - Seleciona o módulo "Roteirização".
        - Preenche dados adicionais de contexto (empresa, filial e tipo de atividade).
        - Avança para a próxima etapa do sistema.

    Parâmetros:
        page:
            Instância do Playwright utilizada para automação do navegador.

        empresa:
            Código da empresa utilizado no login.

        matricula:
            Identificação do usuário no sistema.

        password:
            Senha de acesso ao sistema.

    Retorno:
        None
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
                sku: str = "",
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
    Executa o processo de filtragem de cargas no sistema PRWEB.

    A função automatiza a aplicação de filtros na interface web,
    consulta os resultados e retorna informações consolidadas sobre
    cargas, pedidos e transportadoras.

    Lógica utilizada:
        - Acessa a tela de filtragem de cargas.
        - Seleciona opções iniciais de consulta.
        - Preenche credenciais e parâmetros de busca.
        - Aplica filtros de modalidade, SKU e datas.
        - Seleciona tipos de carga conforme parâmetros (mono, multi, B2B, B2C, crossdocking).
        - Executa a consulta no sistema.
        - Lê e registra os resultados retornados:
            * pedidos selecionados
            * pedidos por tipo
            * quantidade de cargas
            * transportadoras
            * pedidos processados
        - Finaliza retornando ao menu principal.

    Parâmetros:
        page:
            Instância do Playwright responsável pela automação.

        empresa:
            Código da empresa utilizada no login.

        matricula:
            Identificação do usuário no sistema.

        password:
            Senha de acesso.

        sku (str):
            Código SKU para filtro de produtos.

        dt_limite_exp_retro (str):
            Data limite de expedição retroativa.

        dt_limite_exp_posterior (str):
            Data limite de expedição posterior.

        dt_limite_exp_start (str):
            Data inicial do período de expedição.

        dt_limite_exp_end (str):
            Data final do período de expedição.

        mono (str):
            Flag para cargas monotransportadas.

        multiplo (str):
            Flag para cargas multitransportadas.

        B2B (str):
            Flag para cargas B2B.

        B2C (str):
            Flag para cargas B2C.

        CROSSDOCKING (str):
            Flag para cargas crossdocking.

        dt_entrega (str):
            Data de entrega.

        modalidade (str):
            Modalidade da rota selecionada.

    Retorno:
        None

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

    sku_ = page.locator("xpath=/html/body/form/table[4]/tbody/tr[3]/td[2]/input[1]")
    sku_.type(sku)

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
    
    if multiplo == "Sim":
        page.locator("xpath=/html/body/form/table[4]/tbody/tr[12]/td[2]/input[2]").click()
        logger.info("Cargas multitransportadas selecionadas")
    
    if B2B == "Sim":
        page.locator("xpath=/html/body/form/table[4]/tbody/tr[14]/td[2]/input[1]").click()
        logger.info("Cargas B2B selecionadas")
    
    if B2C == "Sim":
        page.locator("xpath=/html/body/form/table[4]/tbody/tr[14]/td[2]/input[2]").click()
        logger.info("Cargas B2C selecionadas")
    
    if CROSSDOCKING == "Sim":
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

def transferencia_pedido(page,
                         empresa,
                         matricula,
                         password,
                         motivo_mudanca,
                         carga,
                         n_pedido: list[str]):
    
    """
    Executa a transferência de pedidos vinculados a uma carga no sistema PRWEB.

    A função automatiza a navegação na tela de transferência, realiza o
    preenchimento de credenciais e processa cada pedido informado.

    Lógica utilizada:
        - Inicia o fluxo de transferência de pedidos.
        - Seleciona a opção de documentos/carga.
        - Acessa a funcionalidade de inclusão.
        - Preenche credenciais do usuário (empresa, matrícula e senha).
        - Para cada pedido da lista:
            * Insere o número do documento.
            * Executa o processamento da transferência.

    Parâmetros:
        page:
            Instância do Playwright utilizada na automação.

        empresa:
            Código da empresa para autenticação.

        matricula:
            Identificação do usuário no sistema.

        password:
            Senha de acesso ao sistema.

        motivo_mudanca:
            Motivo da transferência (não utilizado no fluxo atual).

        carga:
            Identificador da carga associada à transferência.

        n_pedido (list[str]):
            Lista de números de pedidos a serem transferidos.

    Retorno:
        None
    """
    
    logger.info(f"Iniciando transferencia de pedidos\nCarga:{carga}")

    documento_carga = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr/td[1]/table/tbody/tr[13]/td[1]/input")
    documento_carga.click() # Checkbox Documentos/Carga

    inclui = page.locator('xpath=//*[@id="NM_BOT_ICL"]')
    inclui.click()

    empresa_ = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr/td[5]/input")
    empresa_.clear()
    empresa_.type(empresa)

    matricula_ = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr/td[6]/input")
    matricula_.type(matricula)

    senha_ = page.locator("xpath=/html/body/form[1]/table[3]/tbody/tr/td[7]/b/input")
    senha_.type(password)

    for i in n_pedido:
        n_do_documento_ = page.locator("xpath=/html/body/form[1]/table[4]/tbody/tr[1]/td[2]/input[1]")
        n_do_documento_.type(i)

        processa_ = page.locator('xpath=//*[@id="NM_BOT_PRC"]')
        processa_.click()
        
    pass

def boxiamento_carga(page,
                    empresa,
                    matricula,
                    password,
                    data,
                    rotas=None):
    """
    Executa o processo automatizado de boxiamento de cargas no sistema PRWEB.

    A função realiza a consulta de cargas por rota, aplica regras de boxiamento
    e ajusta automaticamente valores de box e status de emissão conforme regras
    de negócio definidas.

    Lógica utilizada:
        - Inicializa o fluxo de consulta de cargas no sistema.
        - Preenche credenciais de acesso.
        - Obtém lista de rotas (parâmetro ou configuração padrão).
        - Para cada rota:
            * Realiza consulta de cargas.
            * Aguarda retorno da tabela de resultados.
            * Percorre as cargas retornadas (com paginação quando necessário).
            * Para cada carga:
                - Extrai informações como:
                    * código da carga
                    * status (Aberta/Fechada)
                    * transportadora
                    * contrato
                    * estado
                    * valor de box atual
                    * checkbox de emissão
                - Aplica regras de emissão:
                    * Cargas abertas desmarcam emissão.
                    * Cargas fechadas marcam emissão.
                    * Casos com contrato ausente seguem regra simplificada.
                - Aplica lógica de boxiamento:
                    * Regra especial para estado "PE" (box fixo).
                    * Caso contrário, utiliza `_resolve_box_for_carga`.
            * Registra cada carga processada em uma tabela de controle.
        - Trata paginação quando o limite de registros é atingido.
        - Reprocessa consulta quando não há cargas.
        - Consolida e exibe tabela final de execução.

    Regras principais:
        - Estado "PE" recebe box fixo.
        - Box é definido por regras configuradas + matching de contrato/transportadora.
        - Checkbox de emissão depende do status da carga.
        - Cargas sem contrato seguem fluxo simplificado.

    Parâmetros:
        page:
            Instância do Playwright usada na automação.

        empresa:
            Código da empresa utilizada no processo.

        matricula:
            Identificação do usuário.

        password:
            Senha de acesso ao sistema.

        data:
            Data de referência da operação.

        rotas (list | None):
            Lista de rotas a serem processadas. Caso não informado,
            utiliza configuração padrão.

    Retorno:
        None
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

    sp_rotas = rotas if rotas else _load_sp_rotas_from_config()
    cargas_box_map = _load_cargas_box_from_config()

    tabela_geral = []

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
                        """
                        Resolve o XPath correto do elemento de carga na tabela.

                        A função verifica se o elemento de carga está encapsulado em um link (<a>)
                        e retorna o XPath apropriado conforme a estrutura da página.

                        Lógica utilizada:
                            - Monta o XPath base do elemento com base no índice informado.
                            - Verifica se existe um elemento <a> dentro do caminho.
                            - Se existir, retorna o XPath com o link.
                            - Caso contrário, retorna o XPath base.

                        Parâmetros:
                            page:
                                Instância do Playwright usada para interação com a página.

                            i (int):
                                Índice da linha da tabela onde a carga está localizada.

                        Retorno:
                            str:
                                XPath correto para acesso ao elemento de carga.
                        """
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

                    def get_checkbox_state(locator):
                        """
                        Retorna o estado atual de um checkbox.

                        A função avalia as propriedades do elemento para identificar se ele está
                        desabilitado, marcado ou desmarcado.

                        Lógica utilizada:
                            - Verifica se o atributo "disabled" está presente.
                            - Caso não esteja desabilitado, verifica se está selecionado.
                            - Caso contrário, considera como desmarcado.

                        Parâmetros:
                            locator:
                                Elemento (Playwright Locator) representando o checkbox.

                        Retorno:
                            str:
                                Estado do checkbox:
                                - "disabled"
                                - "checked"
                                - "unchecked"
                        """
                        return (
                            "disabled" if locator.get_attribute("disabled") is not None
                            else "checked" if locator.is_checked()
                            else "unchecked"
                        )
                    
                    estado_checkbox_antes = get_checkbox_state(xpath_checkbox_emite)

                    if xpath_contrato_.count() == 0:
                        if status_carga == "Fechada":
                            if estado_checkbox_antes == "unchecked":
                                xpath_checkbox_emite.click()
                        
                        logger.info("Contrato não encontrado")
                        continue

                    xpath_contrato = xpath_contrato_.inner_text()
                        
                    # ============== Extração de transportadora ==============

                    xpath_transportadora = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i+1}]/tbody/tr[9]/td[2]").inner_text()

                    # ============== Condição: Se o status_carga for "Fechado" a checkbox EMITE deve ser "checked" ==============

                    # ============== Lógica de Checkbox Emite ==============             
                    if status_carga == "Fechada" : # <<< Status da carga = 'Fechada'

                        if estado_checkbox_antes == "unchecked": # <<< Checkbox estiver desmarcado
                            xpath_checkbox_emite.click() # <<< Marca checkbox
                        
                    elif status_carga == "Aberta": # <<< Status da carga = 'Aberta'

                        if estado_checkbox_antes == "checked": # <<< Checkbox estiver marcada
                            xpath_checkbox_emite.click() # <<< Desmarca checkbox

                    estado_checkbox_depois = get_checkbox_state(xpath_checkbox_emite)

                    # ============== Extração de Estado da Carga =============

                    xpath_estado_carga = page.locator(f"xpath=/html/body/form/table[8]/tbody/tr[2]/td/table[{i}]/tbody/tr/td[5]").inner_text()

                    logger.info(f"Carga do estado de {xpath_estado_carga}")

                    # ============== Lógica de Boxiamento ==============
                    box = ""
                    v_box = xpath_valor_box.input_value()

                    if status_carga == "Fechada": # <<< Status da carga = 'Fechada' e valor do box estiver vazio
                        
                        if v_box == "999":
                            if estado_checkbox_antes == "checked": # <<< Checkbox estiver desmarcado
                                xpath_checkbox_emite.click() # <<< Desmarca checkbox

                        if "PE" in xpath_estado_carga:
                            box = "921"
                            xpath_valor_box.fill(box)

                            logger.info(f"Box PE {box}")

                        else:
                            # Boxiamento priorizando regras com rota e match em contrato
                            box_resolvido = _resolve_box_for_carga(
                                cargas_box_map=cargas_box_map,
                                rota_atual=rota,
                                contrato=xpath_contrato,
                                transportadora=xpath_transportadora,
                            )
                            
                            if box_resolvido:
                                xpath_valor_box.clear()
                                box = box_resolvido
                                xpath_valor_box.type(box)

                    # ============== Tabela ==============

                    linha = {
                        "Rota": rota,
                        "Nº Carga": carga,
                        "Transportadora": xpath_transportadora,
                        "Box": box,
                        "Status da Carga": status_carga,
                        "Botão Emite Antes": estado_checkbox_antes,
                        "Botão Emite Depois":estado_checkbox_depois,
                        "Estado": xpath_estado_carga
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

        tabela_geral.extend(tabela)
    
    if tabela_geral:
        logger.info("TABELA FINAL - BOXIAMENTO DE CARGAS")
        logger.info(tabulate(tabela_geral, headers="keys", tablefmt="grid"))
    else:
        logger.info("Nenhum registro encontrado para boxiamento de cargas.")