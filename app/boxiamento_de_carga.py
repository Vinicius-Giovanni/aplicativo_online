
"""
Responsável pela construção do layout da página que executa a automação do processo de boxeamento de cargas.

Esta interface permite:
- Execução do processo de boxeamento;
- Integração com as regras de negócio do sistema logístico.
"""


from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QMessageBox, QListWidget, QLabel, QHBoxLayout
)

from PySide6.QtCore import QThread
from workers.prweb_worker import PrwebWorker
from settings.config import AppConfig

import json

class BoxiamentoCarga(QWidget):
    def __init__(self, empresa, matricula, password):
        super().__init__()

        self.empresa = empresa
        self.matricula = matricula
        self.password = password
        self.app_config = AppConfig()

        self.setup_ui()

    def setup_ui(self):
        """
        Responsável pela construção da interface da página de boxeamento,
        incluindo a configuração dos componentes visuais, interação do usuario
        e acionamento das funções da automação.
        """

        # Data
        self.dt_entrega = QLineEdit(maxLength=8)
        self.dt_entrega.setPlaceholderText("DDMMAAAA")

        # Botão
        self.btn_executar = QPushButton("Executar Boxiamento de Cargas")
        self.btn_executar.clicked.connect(self.executar_boxiamento)

        self.label_rotas = QLabel("Selecione as rotas para boxiamento:")
        self.lista_rotas = QListWidget()
        self.lista_rotas.setSelectionMode(QListWidget.MultiSelection)
        self.carregar_rotas()

        self.input_rota_manual = QLineEdit()
        self.input_rota_manual.setPlaceholderText("Boxear rota fora da lista")

        self.btn_add_rota_manual = QPushButton("Adicionar rota")
        self.btn_add_rota_manual.clicked.connect(self.adicionar_rota_manual)

        # Layout
        form = QFormLayout()
        form.addRow("Data Entrega:", self.dt_entrega)

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

    def executar_boxiamento(self):
        """
        Executa a automação de boxeamento a partir dos parâmetros
        informados pelo usuário, encaminhando os dados para
        a rotina principal de processamento.
        """

        if not self.dt_entrega.text():
            QMessageBox.warning(self, "Campo obrigatório", "A data de entrega deve ser preenchida.")
            return
        
        rotas_selecionadas = [item.text().strip() for item in self.lista_rotas.selectedItems()]
        if not rotas_selecionadas:
            QMessageBox.warning(self, "Campo obrigatório", "Selecione pelo menos uma rota para boxiamento.")
            return
        
        self.btn_executar.setEnabled(False)

        params = {
            "action": "boxiamento",
            "empresa": self.empresa,
            "matricula": self.matricula,
            "password": self.password,
            "data": self.dt_entrega.text(),
            "rotas": rotas_selecionadas
        }

        self.thread = QThread()
        self.worker = PrwebWorker(params)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.succeeded.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        
        self.thread.start()

    def on_finished(self):
        """
        Controla o estado do botão responsável por executar
        a automação de boxeamento.

        O botão permanece desabilitado durante a execução
        do processamento e é reabilitado após a finalização
        da automação.
        """

        QMessageBox.information(self, "Concluído", "Boxiamento de carga concluído com sucesso.")
        self.btn_executar.setEnabled(True)

    def on_error(self, message):
        """
        Controla o estado do botão de execuçã da automação.

        Em caso de falha durante o processamento,
        o botão é reabilitado para permitir uma nova tentativa. 
        """

        QMessageBox.critical(self, "Erro", message)
        self.btn_executar.setEnabled(True)

    def carregar_rotas(self):
        """
        Realiza a leitura do arquivo JSON contendo as regras
        de negócio logísticas utilizadas na lógica de boxeamento.

        As regras são aplicadas considerando a rota e o código da transportadora.
        """

        self.lista_rotas.clear()

        try:
            with open(self.app_config.ROTAS_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.app_config._ensure_rotas_file()
            with open(self.app_config.ROTAS_FILE, "r", encoding="utf-8") as f:
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
        Permite ao usuário adicionar uma rota temporária manualmente.

        A rota informada não é persistida no arquivo JSON
        e será considerada apenas durante a execução atual
        da lógica de boxeamento.
        """
        rota = self.input_rota_manual.text().strip()
        if not rota:
            QMessageBox.warning(self, "Campo vazio", "Digite uma rota para adicionar.")
            return
        
        rotas_exitentes = [
            self.lista_rotas.item(i).text().strip()
            for i in range(self.lista_rotas.count())
        ]
        if rota not in rotas_exitentes:
            self.lista_rotas.addItem(rota)

        for i in range(self.lista_rotas.count()):
            item = self.lista_rotas.item(i)
            if item.text().strip() == rota:
                item.setSelected(True)
                break

        self.input_rota_manual.clear()
        