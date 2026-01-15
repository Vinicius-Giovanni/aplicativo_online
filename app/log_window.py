from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class LogWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Acompanhamento da RPA")
        self.showMaximized()

        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_log)
        self.setLayout(layout)
    
    def append_log(self, message:str):
        self.text_log.append(message)
    