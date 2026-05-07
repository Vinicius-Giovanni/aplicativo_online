import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
)
from datetime import datetime
from pathlib import Path

class LogExportWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.log_messages = []
        self.log_dir = Path.home() / ".rpa_online" / "historico_programao"
        self.setup_ui()
        self.carregar_historico_salvo()

    def setup_ui(self):
        """
        Inicializa e configura a interface gráfica da janela de histórico.

        A função monta os componentes visuais da telaa, define a estrutura
        do layout principal e configura os eventos necessários para interação
        do usuário.

        Funcionalidades:
            - Cria o layout principal da interface.
            - Configura o campo de pesquisa para filtragem dinâmica.
            - Inicializa a árvore de exibição dos registros.
            - Conecta o evento de alteração de texto ao método 'filtrar_datas'.
            - Define o layout final da janela.

        Lógica utilizada:
            - Utiliza um 'QVBoxLayout' para organizar os componentes verticalmente.
            - O sinal 'textChanged' do campo de pesquisa é conectado ao método
                responsável pela filtragem dos registros em tempo real.

        Parâmetros:
            self:
                Instância atual da classe responsável pela interface.

        Retorno:
            None

        """

        layout = QVBoxLayout()

        titulo = QLabel("Histórico de Programação")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.serch_input = QLineEdit()
        self.serch_input.setPlaceholderText("Pesquisar por data (DD-MM-AAAA)")
        self.serch_input.textChanged.connect(self.filtrar_datas)

        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Data / Registro"])
        self.history_tree.setColumnCount(1)

        layout.addWidget(titulo)
        layout.addWidget(self.serch_input)
        layout.addWidget(self.history_tree)
        self.setLayout(layout)
    
    def append_log(self, message: str):
        """
        Adiciona uma nova mensagem de log ao sistema de histórico.

        A função é responsável por registrar a mensagem em memória,
        persistir o log automaticamente em arquivo e atualizar a interface
        gráfica com o novo registro.

        Lógica utilizada:
            - Adiciona a mensagem na lista interna de logs.
            - Salva automaticamente o registro no arquivo correspondente à data atual.
            - Atualiza a árvore de histórico exibida na interface.

        Parâmetros:
            message(str):
                Mensagem que será registrada no histórico de logs.

        Retorno:
            None
        """

        self.log_messages.append(message)
        self.salvar_log_automaticamente(message)
        self.adicionar_log_na_arvore(self.data_atual(), message)

    def data_atual(self) -> str:
        """
        Retorna a data atual formatada para utilização no sistema de logs.

        Lógica utilizada:
            - Obtém a data atual do sistema utilizado 'datetime.now()'.
            - Formata a data no padrão 'DD-MM-YYYY'

        Retorno:
            str:
                Data atual formadada.
        """

        return datetime.now().strftime("%d-%m-%Y")
    
    def caminho_arquivo_data(self, data:str) -> Path:
        """
        Gera o caminho completo do arquivo de log associado a uma data específica.

        A função utiliza o diretório principal de logs para construir
        dinamicamente o nome do arquivono formato JSON.

        Lógica utilizada:
            - Concatena o diretório base de logs com o nome do arquivo
                correspondente à data informada.

        Parâmetros:
            data(str):
                Data utilizando como nome do arquivo de log.

        Retorno:
            Path:
                Caminho completo do arquivo de log.
        """

        return self.log_dir / f"{data}.json"
    
    def salvar_log_automaticamente(self, message:str):
        """
        Realiza o salvamento automático de mensagens de logs em arquivos JSON.

        A função garante a criação do diretório de logs, carrega os registros
        existentes do arquivo correspondente à data atual e adiciona a nova mensagem ao histórico persistido.

        Lógica utilizando:
            - Cria o diretório de logs caso ele não exista.
            - Obtém a data atual para definição do arquivo de armazenamento.
            - Carrega os logs já existentes do arquivo JSON.
            - Inicializa uma estrutura padrão caso o arquivo esteja vazio,
                corrompido ou inválido.
            - Adiciona o arquivo JSON com os dados atualizados.
            - Reescreve o arquivo JSON com os dados atualizados.
            - Exibe uma mensagem crítica caso ocorra erro durante a gravação.
        
        Tratamento de exceções:
            - 'OsError'
                Captura erros relacionados ao sistema de arquivos.
            - 'json.JSONDecodeError':
                Captura falhas ao interpretar arquivos JSON inválidos.

        Parâmetros:
            message (str):
                Mensagem que será adicinoada ao histórico de logs.

        Retorno:
            None

        """

        self.log_dir.mkdir(parents=True, exist_ok=True)

        data= self.data_atual()
        file_path = self.caminho_arquivo_data(data)

        payload = {"data": data, "logs": []}
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except (OSError, json.JSONDecodeError):
                payload = {"data": data, "logs": []}
        
        logs = payload.get("logs", [])
        logs.append(message)
        payload["logs"] = logs

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Erro ao salvar",
                f"Não foi possível salvar o histórico automático.\n{exc}",
            )
    
    def carregar_historico_salvo(self):
        """
        Carrega os arquivos de historico salvos e atualiza a árvore de exibição.

        A função realiza a leitura dos arquivos JSON armazenados no diretório
        de logs, extrai os registros e cria os itens correspondentes na interface.

        Lógica utilizada:
            - Limpa os itens atuais da árvore.
            - Verifica a existência do diretório de logs.
            - Percorre os arquivos JSON disponíveis.
            - Carrega os logs armazenados.
            - Cria os itens visuais na árvore de histórico.
            - Trata arquivos invalidos ou corrompidos.

        Parâmetros:
            self:
                Instância atual da classe.
        """

        self.history_tree.clear()

        if not self.log_dir.exists():
            return
        
        arquivos = sorted(self.log_dir.glob("*.json"), reverse=True)
        for arquivo in arquivos:
            data = arquivo.stem
            logs = []

            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                    logs = payload.get("logs", [])
            except (OSError, json.JSONDecodeError):
                logs = ["⚠️ Arquivo inválido ou corrompido"]

            self.criar_item_data(data, logs)
    
    def criar_item_data(self, data: str, logs: list[str]):
        """
        Cria um item de data na árvore de histórico e adiciona os logs associados.

        A função cria um item principal utilizando a data informada e adiciona
        os registros de log como itens filhos na árvore de exibição.

        Parâmetros:
            data (str):
                Data utilizada como item principal da árvore.

            logs (list[str]):
                Lista de mensagens de log associados à data.

        Retorno:
            None
        """

        item_data = QTreeWidgetItem([data])

        item_data.setExpanded(False)

        for log in logs:
            item_log = QTreeWidgetItem([log])
            item_data.addChild(item_log)

        self.history_tree.addTopLevelItem(item_data)

    def adicionar_log_na_arvore(self, data:str, message:str):
        """
        Adiciona uma nova mensagem de log na árvore de histórico.

        A função localiza o item correspondente à data informada e adiciona
        o log como item filho. Caso a data ainda não exista, um novo item
        pricipal é criado.

        Parâmetross:
            data(str):
                Data associada ao log.
            
            message (str):
                Mensagem que será adicionado na árvore.
        
        Retorno:
            None
        """

        item_data = self.buscar_item_data(data)

        if item_data is None:
            item_data = QTreeWidgetItem([data])
            self.history_tree.insertTopLevelItem(0, item_data)

        item_data.addChild(QTreeWidgetItem([message]))

    def buscar_item_data(self, data: str):
        """
        Busca um item de data na árvore de histórico.

        A função percorre os itens principais da árvore e retorna o item
        correspondente à data informada.

        Parâmetros:
            data(str):
                Data utilizada na busca.

        Retorno:
            QTreeWidgetImte | None:
                Item encontrado ou None caso não exista.
        """

        for i in range(self.history_tree.topLevelItemCount()):
            item = self.history_tree.topLevelItem(i)
            if item.text(0) == data:
                return item
            
        return None
    
    def filtrar_datas(self, texto: str):
        """
        Filtra os itens da árvore de histórico com base no texto informado.

        A função verifica se o termo pesquisado está presente nas datas
        exibidas e oculta os itens que não correspondem ao filtro.

        Parâmetros:
            texto(str):
                Texto utilizado na filtragem das datas.


        Retorno:
            None
        """

        termo = texto.strip().lower()

        for i in range(self.history_tree.topLevelItemCount()):
            item_data = self.history_tree.topLevelItem(i)
            data_texto = item_data.text(0).lower()
            ocultar = termo not in data_texto
            item_data.setHidden(ocultar)
