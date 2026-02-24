import json

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTextEdit,
)

class LogExportWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.log_messages = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)

        self.btn_save = QPushButton("Salvar registro")
        self.btn_save.clicked.connect(self.salvar_log_json)

        layout.addWidget(self.preview)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)
    
    def append_log(self, message: str):
        self.log_messages.append(message)
        self.preview.append(message)
    
    def salvar_log_json(self):
        if not self.log_messages:
            QMessageBox.information(self, "Sem logs", "Ainda não há logs para salvar.")
            return 
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar logs",
            "logs_registro.json",
            "JSON (*.json)",
        )

        if not file_path:
            return
        
        payload = {"logs": self.log_messages}

        try:
            with open(file_path, "w", encoding='utf-8') as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
        except OSError as exc:
            QMessageBox.critical(self, "Erro ao salvar", f"Não foi possível salvar o arquivo.\n{exc}")
            return
        
        QMessageBox.information(self, "Sucesso", "Registro salvo com sucesso.")