from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QMessageBox, QListWidget, QLabel, QHBoxLayout
)

from PySide6.QtCore import QThread
from workers.prweb_worker import PrwebWorker
from settings.config import AppConfig
import json

class EmissaoWindow(QWidget):
    def __init__(self, empresa, matricula, password):
        super().__init__()

        self.empresa = empresa
        self.matricula = matricula
        self.password = password
        self.app_config = AppConfig()

        self.setup_ui()

    def setup_ui(self):
        """
        Configura e monta a interface gráfica da janela de emissão.

        A função cria os campos de entrada, botões e listas utilizados
        no processo de emissão, além de definir os layouts da janela
        e conectar os eventos aos respectivos métodos.

        Componentes configurados:
        - Campo de data de entrega
        - Lista de rotas para emissão
        - Campo para inclusão manual de rotas
        - Botão de adicionar rota
        - Botão de execução de emissão
        """

        # Data
        self.data = QLineEdit(maxLength=8)
        self.data.setPlaceholderText("DDMMAAAA")

        # Botão
        self.btn_executar = QPushButton("Executar Emissão")
        self.btn_executar.clicked.connect(self.executar_emissao)

        self.label_rotas = QLabel("Selecione as rotas para emissão:")
        self.lista_rotas = QListWidget()
        self.lista_rotas.setSelectionMode(QListWidget.MultiSelection)
        self.carregar_rotas()

        self.input_rota_manual = QLineEdit()
        self.input_rota_manual.setPlaceholderText("Emitir rota fora da lista")

        self.btn_add_rota_manual = QPushButton("Adicionar rota")
        self.btn_add_rota_manual.clicked.connect(self.adicionar_rota_manual)

        # Layout
        form = QFormLayout()
        form.addRow("Data Entrega:", self.data)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.label_rotas)
        layout.addWidget(self.lista_rotas)

        add_rota_layout = QHBoxLayout()
        add_rota_layout.addWidget(self.input_rota_manual)
        add_rota_layout.addWidget(self.btn_add_rota_manual)
        layout.addLayout(add_rota_layout)

        layout.addWidget(self.btn_executar)

        self.setLayout(layout)
    
    def executar_emissao(self):
        """
        Executa o processo de emissão das rotas selecionadas.

        A função valida os campos obrigatórios, coleta os parâmetros
        da emissão e inicia a execução em uma thread separada para evitar bloqueio da interface gráfica.

        Fluxo executado:
        - Validação da data de entrega
        - Validação das rotas selecionadas
        - Montagem dos parâmetros da emissão
        - Inicialização da thread e do worker
        - Conexão dos sinas de execução, finalização e erro
        - Início do processamento da emissão
        """
        
        if not self.data.text():
            QMessageBox.warning(self, "Campo obrigatório", "A data de entrega deve ser preenchida.")
            return
        
        rotas_selecionadas = [item.text().strip() for item in self.lista_rotas.selectedItems()]
        if not rotas_selecionadas:
            QMessageBox.warning(self, "Campo obrigatório", "Selecione pelo menos uma rota para emissão.")
            return
        
        self.btn_executar.setEnabled(False)

        params = {
            "action": "emissao",
            "empresa": self.empresa,
            "matricula": self.matricula,
            "password": self.password,
            "data": self.data.text(),
            "rotas": rotas_selecionadas
        }

        self.thread = QThread()
        self.worker = PrwebWorker(params)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

        self.thread.start()

    def on_finished(self):
        """
        Trata a finalização do processo de emissão.

        Exibe uma mensagem de sucesso ao usuário e
        reabilita o botão de execução de emissão.
        """

        QMessageBox.information(self, "Concluído", "Emissão de cargas concluída com sucesso.")
        self.btn_executar.setEnabled(True)

    def on_error(self, message):
        """
        Trata erros ocorridos durante o processo de emissão.

        Args:
            message(str): Mensagem de erro retornada pelo processo.
        
        Exibe a mensagem de erro ao usuário e
        reabilita o botão de execução da emissão.
        """

        QMessageBox.critical(self, "Erro", message)
        self.btn_executar.setEnabled(True)

    def carregar_rotas(self):
        """
        Carrega as rotas disponíveis no arquivo de configuração.

        A função realiza a leitura do arquivo 'rotas.json',
        adiciona as rotas na lista da interface e seleciona
        automaticamente todos as rotas carregadas.

        Tratamentos realizados:
        - Criação do arquivo de rotas caso não exista
        - Validação de estrutura JSON inválida
        """

        self.lista_rotas.clear()

        try:
            with open(self.app_config.ROTAS_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.app_config._ensure_rotas_file()
            with open(self.app_config.ROTAS_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Erro no JSON", "O arquivo rotas.json está inválido.")
            return
        
        for rota in data.get("sp_rotas", []):
            self.lista_rotas.addItem(str(rota).strip())

        for i in range(self.lista_rotas.count()):
            self.lista_rotas.item(i).setSelected(True)

    def adicionar_rota_manual(self):
        """
        Adiciona manualmente uma rota à lista de emissão.

        A função valida o preenchimento do campo de rota,
        evita duplicidades na lista e seleciona automaticamente
        a rota adicionada ou já existente.
        """

        rota = self.input_rota_manual.text().strip()
        if not rota:
            QMessageBox.warning(self, "Campo vazio", "Digite uma rota para adicionar.")
            return
        
        rotas_existentes = [
            self.lista_rotas.item(i).text().strip()
            for i in range(self.lista_rotas.count())
        ]

        if rota not in rotas_existentes:
            self.lista_rotas.addItem(rota)

        for i in range(self.lista_rotas.count()):
            item = self.lista_rotas.item(i)
            if item.text().strip() == rota:
                item.setSelected(True)
                break