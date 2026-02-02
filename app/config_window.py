from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget,
    QPushButton, QHBoxLayout, QInputDialog, QMessageBox
)

from settings.config_manager import ConfigManager

class ConfigWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configurações")
        self.resize(300,400)

        self.config = ConfigManager()

        self.layout = QVBoxLayout(self)

        self.lista = QListWidget()
        self.layout.addWidget(self.lista)

        self.load_rotas()

        btn_layout = QHBoxLayout()

        btn_add = QPushButton("Adicionar")
        btn_remove = QPushButton("Remover")
        btn_save = QPushButton("Salvar")

        btn_add.clicked.connect(self.add_rota)
        btn_remove.clicked.connect(self.remove_rota)
        btn_save.clicked.connect(self.save)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_save)

        self.layout.addLayout(btn_layout)

    def load_rotas(self):
        self.lista.clear()
        for rota in self.config.get_rotas():
            self.lista.addItem(rota)
        

    def add_rota(self):
        rota, ok = QInputDialog.getText(self, "Nova rota", "Digite a rota:")
        if ok and rota:
            self.lista.addItem(rota)
    
    def remove_rota(self):
        item = self.lista.currentItem()
        if item:
            self.lista.takeItem(self.lista.row(item))
    
    def save(self):
        rotas = [
            self.lista.item(i).text()
            for i in range(self.lista.count())
        ]

        self.config.set_rotas(rotas)

        QMessageBox.information(self, "Sucesso", "Configurações salvas!")