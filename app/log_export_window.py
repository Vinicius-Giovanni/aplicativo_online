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
        self.log_messages.append(message)
        self.salvar_log_automaticamente(message)
        self.adicionar_log_na_arvore(self.data_atual(), message)

    def data_atual(self) -> str:
        return datetime.now().strftime("%d-%m-%Y")
    
    def caminho_arquivo_data(self, data:str) -> Path:
        return self.log_dir / f"{data}.json"
    
    def salvar_log_automaticamente(self, message:str):
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
        item_data = QTreeWidgetItem([data])

        item_data.setExpanded(False)

        for log in logs:
            item_log = QTreeWidgetItem([log])
            item_data.addChild(item_log)

        self.history_tree.addTopLevelItem(item_data)

    def adicionar_log_na_arvore(self, data:str, message:str):
        item_data = self.buscar_item_data(data)

        if item_data is None:
            item_data = QTreeWidgetItem([data])
            self.history_tree.insertTopLevelItem(0, item_data)

        item_data.addChild(QTreeWidgetItem([message]))

    def buscar_item_data(self, data: str):
        for i in range(self.history_tree.topLevelItemCount()):
            item = self.history_tree.topLevelItem(i)
            if item.text(0) == data:
                return item
            
        return None
    
    def filtrar_datas(self, texto: str):
        termo = texto.strip().lower()

        for i in range(self.history_tree.topLevelItemCount()):
            item_data = self.history_tree.topLevelItem(i)
            data_texto = item_data.text(0).lower()
            ocultar = termo not in data_texto
            item_data.setHidden(ocultar)
