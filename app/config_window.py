
"""
Módulo responsável pela construção do layout da página de configurações das regras de negócio logísticas.
"""

import json

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QLabel,
)

from settings.config import AppConfig

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.app_config = AppConfig()
        self.setup_ui()
        self.carregar_configuracoes()

    def setup_ui(self):
        """
        Responsável pela construção da interface da página de configuração,
        incluindo a configuração dos componentes visuais, interação do usuario
        e acionamento das funções da automação.
        """

        layout = QVBoxLayout()

        # Rotas
        descricao_rotas = QLabel("Rotas SP")
        layout.addWidget(descricao_rotas)

        self.lista_rotas = QListWidget()
        self.lista_rotas.setSelectionMode(QListWidget.SingleSelection)
        self.lista_rotas.itemSelectionChanged.connect(self._on_rota_selection_changed)
        layout.addWidget(self.lista_rotas)

        add_layout_rotas = QHBoxLayout()
        self.input_rota = QLineEdit()
        self.input_rota.setPlaceholderText("Digite a nova rota")

        self.btn_add_rota = QPushButton("Adicionar")
        self.btn_add_rota.clicked.connect(self.adicionar_rota)

        add_layout_rotas.addWidget(self.input_rota)
        add_layout_rotas.addWidget(self.btn_add_rota)
        layout.addLayout(add_layout_rotas)

        # Cargas/Box
        descricao_cargas_box = QLabel("Cargas / Box")
        layout.addWidget(descricao_cargas_box)

        descricao_regra_rota = QLabel("Dica: para regra por rota, deixe a Carga em branco e preencha a Rota + Box.")
        layout.addWidget(descricao_regra_rota)

        self.lista_cargas_box = QListWidget()
        self.lista_cargas_box.setSelectionMode(QListWidget.SingleSelection)
        self.lista_cargas_box.itemSelectionChanged.connect(self._on_carga_box_selection_changed)
        layout.addWidget(self.lista_cargas_box)

        add_layout_cargas = QHBoxLayout()
        self.input_carga = QLineEdit()
        self.input_carga.setPlaceholderText("Ex: JT TRANSPORTES (opctional se usar só rota)")

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ex.: 849 (opcional)")

        self.input_rota_carga = QLineEdit()
        self.input_rota_carga.setPlaceholderText("Ex: 2872 (opcional)")

        self.btn_add_carga_box = QPushButton("Adicionar regra (carga/rota/box)")
        self.btn_add_carga_box.clicked.connect(self.adicionar_carga_box)

        add_layout_cargas.addWidget(self.input_carga)
        add_layout_cargas.addWidget(self.input_box)
        add_layout_cargas.addWidget(self.input_rota_carga)
        add_layout_cargas.addWidget(self.btn_add_carga_box)
        layout.addLayout(add_layout_cargas)

        actions_layout = QHBoxLayout()

        self.btn_remover = QPushButton("Excluir selecionada")
        self.btn_remover.clicked.connect(self.remover_item_selecionado)

        self.btn_recarregar = QPushButton("Recarregar")
        self.btn_recarregar.clicked.connect(self.carregar_configuracoes)

        self.btn_restaurar_padrao = QPushButton("Restaurar padrões")
        self.btn_restaurar_padrao.clicked.connect(self.restaurar_padrao)

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_configuracoes)

        actions_layout.addWidget(self.btn_remover)
        actions_layout.addWidget(self.btn_recarregar)
        actions_layout.addWidget(self.btn_restaurar_padrao)
        actions_layout.addWidget(self.btn_salvar)
        layout.addLayout(actions_layout)

        self.setLayout(layout)

    def _on_rota_selection_changed(self):
        """
        Caso o usuário selecione uma rota específica na interface,
        qualquer seleção previamente definida nos campos de carga box 
        será removida.
        """

        if self.lista_rotas.currentItem() is None:
            return
        self.lista_cargas_box.clearSelection()

    def _on_carga_box_selection_changed(self):
        """
        Caso o usuário selecione uma carga box específica na interface,
        qualquer seleção previamente definida nos campos de rota 
        será removida.
        """

        if self.lista_cargas_box.currentItem() is None:
            return
        self.lista_rotas.clearSelection()

    def carregar_configuracoes(self):
        """
        Carrega as configurações definidas pelo usuário.
        """

        self.carregar_rotas()
        self.carregar_cargas_box()

    def carregar_rotas(self):
        """
        Carrega as rotas definidas pelo usuário.
        """

        self.lista_rotas.clear()

        try:
            with open(self.app_config.ROTAS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            QMessageBox.warning(self, "Arquivo não encontrado", "rotas.json não encontrado. Será recriado com padrão.")
            self.app_config._ensure_rotas_file()
            with open(self.app_config.ROTAS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Erro no JSON", "O arquivo rotas.json está inválido.")
            return

        for rota in data.get("sp_rotas", []):
            self.lista_rotas.addItem(str(rota).strip())

    def _parse_carga_box_item(self, item_text):
        """
        Realiza o parsing de uma configuração de carga box informada em formato textual.
        
        A função interpreta os dados de carga, box e rota
        a partir de uma string no formato:
            
            "CARGA => BOX | Rota: XXX
        
        Regras aplicadas:
        - Caso o separador "=>" não exista, retorna None;
        - O valor "[ROTA]" é convertio para string vazia;
        - A rota é opcional;
        - Quando presente, a rota deve seguir o padrão:
            "Rota: <valor>".

        Parâmetros:
            item_text(str):
                Texto contendo a configuração da carga box.
        
        Retorno:
            dict | None:
                Retorna um dicionário contendo:
                {
                    "carga":str,
                    "box":str,
                    "rota":str
                }

                Retorna None caso o formato seja inválido.
        """

        if "=>" not in item_text:
            return None
        
        carga, resto = item_text.split("=>", 1)
        carga = carga.strip()
        if carga == "[ROTA]":
            carga = ""
        resto = resto.strip()

        rota = ""
        box = resto

        if "|" in resto:
            box_part, rota_part = resto.split("|", 1)
            box = box_part.strip()
            rota_part = rota_part.strip()
            if rota_part.lower().startswith("rota:"):
                rota = rota_part.split(":", 1)[1].strip()

        return {"carga": carga, "box": box, "rota": rota}
    
    def _format_carga_box_item(self, carga, box, rota=""):
        """
        Formata os dados de carga, box e rota para o padrão
        textual utilizados nas configurações de boxeamento.
        
        Formatos gerados:
            "CARGA => BOX"
            "CARGA => BOX | rota: XXX"
            "[ROTA] => BOX | rota: XXX"

        Regras aplicadas:
        - Quando existe rota e a carga está vazia,
            o identificador "[ROTA]" é utilizado;
        - A rota é adicionada apenas quando informada;
        - O retorno é utilizado para exibição e armazenameno
            das configurações de carga box.

        Parâmetros:
            carga (str):;
                Identificador da carga.
            box (str):
                Código ou identificação do box.
            rota (str, opcional):
                Identificador da rota associada.
        
        Retorno:
            str:
                String formatada no pardrão esperado
                pela lógica de boxeamento.
            
        """
        if rota and not carga:
            return f"[ROTA] => {box} | rota: {rota}"
        
        if rota:
            return f"{carga} => {box} | rota: {rota}"
        
        return f"{carga} => {box}"

    def carregar_cargas_box(self):
        """
        Carrega as configurações de cargas box a partir
        do arquivo JSON configurado no sistema.

        Fluxo executado:
        - Limpa os itens atuais da interface;
        - Realiza a leitura do arquivo 'carga_box.json';
        - Recria o arquivo padrã caso ele não exista;
        - Valida a estrutura do JSON carregado;
        - Formata os registros utilizando o padrão
            textual da aplicação;
        - Adiciona os itens válidos na lista da interface.

        Estrutra suportadas:
        1. Dicionário:
            {
                "CARGA": "BOX"
            }
        
        2. Lista de objetos:
            [
                {
                    "carga": "...",
                    "box": "...",
                    "rota": "..."
                }
            ]

        Regras aplicadas:
        - Registros inválidos são ignorados;
        - Itens sem carga e sem rota não são adicionados;
        - Em caso de JSON inválido, uma mensagem de erro
            é exibida ao usuário.
        
        Exceções tratadas:
        - FileNotFoundError:
            Recria automaticamente o arquivo padrão.
        
            - json.JSONDecodeError:
                Interrompe o carregamento quando o JSON
                possui estrutura inválida.
        """

        self.lista_cargas_box.clear()

        try:
            with open(self.app_config.CARGAS_BOX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            QMessageBox.warning(self, "Arquivo não encontrado", "cargas_box.json não encontrado. Será recriado com padrão.")

            self.app_config._ensure_cargas_box_file()
            with open(self.app_config.CARGAS_BOX_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Erro no JSON", "O arquivo carga_box.json está inválido.")
            return
        
        if isinstance(data, dict):
            for carga, box in data.items():
                self.lista_cargas_box.addItem(self._format_carga_box_item(str(carga).strip(), str(box).strip(), ""))
            return

        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue

                carga = str(item.get("carga", "")).strip()
                box = str(item.get("box", "")).strip()
                rota = str(item.get("rota", "")).strip()

                if not carga and not rota:
                    continue

                self.lista_cargas_box.addItem(self._format_carga_box_item(carga, box, rota))

    def adicionar_rota(self):
        """
        Adiciona uma nota rota à lista de rotas configuradas
        na interface.

        Fluxo executado:
        - Obtém o valor informado no campo de entrada;
        - Remove espaços excedentes da rota digitada;
        - Valida se o campo foi preenchido;
        - Verifica se a rota já está cadastrada;
        - Adiciona a nova rota à lista da interface;
        - Limpa o campo de entrada após a inclusão.

        Regras aplicadas:
        - Rotas vazias não são permitidas;
        - Rotas duplicadas não são adicionadas;
        - Mensagens informativas são exibidas ao usuário
            em casos de vaidação.

        """

        rota = self.input_rota.text().strip()

        if not rota:
            QMessageBox.warning(self, "Campo vazio", "Digite uma rota para adicionar.")
            return

        rotas_existentes = [self.lista_rotas.item(i).text() for i in range(self.lista_rotas.count())]
        if rota in rotas_existentes:
            QMessageBox.information(self, "Rota duplicada", "Essa rota já está cadastrada.")
            return

        self.lista_rotas.addItem(rota)
        self.input_rota.clear()

    def adicionar_carga_box(self):
        """
        Adiciona uma nova regra de carga box à interface
        de configurações da automação.

        Fluxo executado:
        - Obtém os valores informados nos campos de entrada;
        - Remove espaços excedentes dos dados inseridos;
        - Vlaida se ao menos um dos campos foi preenchido;
        - Verifica se a combinação de transportadora e rota
            já existe na lista;
        - Adiciona a nova configuração à lista da interface;
        - Limpa os campos após a inclusão do registro.

        Regras aplicadas:
        - Não permite inclusão de registros totalmente vazios
        - Não permite duplicidade da combinação
            transportada/rota;
        - A validação é realizada com base nos itens já
            cadastrados na lista de carga box.
        
        Estrutura adicionada:
            "CARGA => BOX"
            "CARGA => BOX | rota: XXX"
            "[ROTA] => BOX | rota: XXX"
        """

        carga = self.input_carga.text().strip()
        box = self.input_box.text().strip()
        rota = self.input_rota_carga.text().strip()

        if not rota and not carga and not box:
            QMessageBox.warning(self, "Campo vazio", "Digite ao menos transportadora, box ou rota para adicionar.")
            return

        
        for i in range(self.lista_cargas_box.count()):
            item = self.lista_cargas_box.item(i).text()
            parsed = self._parse_carga_box_item(item)
            if not parsed:
                continue

            nome_existente = parsed["carga"]
            rota_existente = parsed["rota"]
            if nome_existente == carga and rota_existente == rota:
                QMessageBox.information(self, "Transportadora duplicada", "Essa regra de transportadora/rota já está cadastrada.")
                return

        self.lista_cargas_box.addItem(self._format_carga_box_item(carga, box, rota))
        self.input_carga.clear()
        self.input_box.clear()
        self.input_rota_carga.clear()

    def remover_item_selecionado(self):
        """
        Remove o item atualmente selecionado nas listas de rotas ou cargas box da interface.

        Fluxo executado:
        - Verifica se existe uma rota selecionada;
        - Remove a rota selecionada da lista;
        - Caso não exista rota selecionada, verifica
            a seleção de carga box;
        - Remove o item de carga box selecionado;
        - Exibe uma mensagem de aviso caso nenhum
            ietm esteja selecionado.

        Regras aplicadas:
        - Apenas um item é removido por execução;
        - A lista de rotas possui prioridade na remoção;
        - Nenhuma ação é executada quando não há seleção.
        """

        item_rota = self.lista_rotas.currentItem()
        item_carga_box = self.lista_cargas_box.currentItem()

        if item_rota:
            self.lista_rotas.takeItem(self.lista_rotas.row(item_rota))
            return
        
        if item_carga_box:
            self.lista_cargas_box.takeItem(self.lista_cargas_box.row(item_carga_box))
            return
        
        QMessageBox.warning(self, "Seleção obrigatória", "Selecione uma rota ou uma carga/box para excluir.")

    def salvar_configuracoes(self):
        """
        Salva as configurações de rotas e cargas box
        nos arquivos JSON utilizados pela automação.

        Fluxo executado:
        - Obtém todas as rotas cadastradas na interface;
        - Percorre os itens de carga box configurados;
        - Realiza o parsing e validação dos registros;
        - Ignora itens inválidos ou incompletos;
        - Salva as rotas no arquivo de configuração
            de rotas;
        - Salva as regras de carga box no arquivo
            de configuração correspondente;
        - Exibe mensagens informativas de sucesso
            ou erro ao usuário.
        
            1. Rotas:
                {
                    "sp_rotas": [...]
                }
            2. Cargas box:
                [
                    {
                        "carga": "...",
                        "box": "...",
                        "rota": "...",
                    }
                ]
        
        Regras aplicadas:
        - Registros inválidos são ignorados;
        - Itens sem carga e sem rota não são persistidos;
        - Os arquivos são salvos utilizando codificação UTF-8;
        - A 

        """

        rotas = [self.lista_rotas.item(i).text().strip() for i in range(self.lista_rotas.count())]

        cargas_box = []
        for i in range(self.lista_cargas_box.count()):
            item_text = self.lista_cargas_box.item(i).text()
            parsed = self._parse_carga_box_item(item_text)
            if not parsed:
                continue
            carga = parsed["carga"]
            box = parsed["box"]
            rota = parsed["rota"]

            if not carga and not rota:
                continue
            
            cargas_box.append({"carga": carga, "box": box, "rota": rota})

        try:
            with open(self.app_config.ROTAS_FILE, "w", encoding="utf-8") as f:
                json.dump({"sp_rotas": rotas}, f, indent=4, ensure_ascii=False)
            
            with open(self.app_config.CARGAS_BOX_FILE, 'w', encoding='utf-8') as f:
                json.dump(cargas_box, f , indent=4, ensure_ascii=False)

        except OSError as e:
            QMessageBox.critical(self, "Erro ao salvar", f"Não foi possível salvar os arquivos de configuração.\n{e}")
            return

        QMessageBox.information(self, "Sucesso", "Configuraçãoes salvas com sucesso.")

    def restaurar_padrao(self):
        resposta = QMessageBox.question(
            self,
            "Restaurar padrões",
            "Deseja restaurar rotas e cargas/box para os valores padrão?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return
        
        try:
            with open(self.app_config.ROTAS_FILE, "w", encoding='utf-8') as f:
                json.dump({"sp_rotas": self.app_config.DEFAULT_ROTAS}, f, indent=4, ensure_ascii=False)

            with open(self.app_config.CARGAS_BOX_FILE, "w", encoding='utf-8') as f:
                json.dump(self.app_config.DEFAULT_CARGAS_BOX, f, indent=4, ensure_ascii=False)
        except OSError as e:
            QMessageBox.critical(self, "Erro ao restaurar", f"Não foi possível restaurar os arquivos padrão.\n{e}")
            return
        
        self.carregar_configuracoes()
        QMessageBox.information(self, "Sucesso", "Arquivos restaurados para o padrão.")