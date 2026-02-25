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
        layout = QVBoxLayout()

        # Rotas
        descricao_rotas = QLabel("Rotas SP")
        layout.addWidget(descricao_rotas)

        self.lista_rotas = QListWidget()
        self.lista_rotas.setSelectionMode(QListWidget.SingleSelection)
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

        self.lista_cargas_box = QListWidget()
        self.lista_cargas_box.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.lista_cargas_box)

        add_layout_cargas = QHBoxLayout()
        self.input_carga = QLineEdit()
        self.input_carga.setPlaceholderText("Ex: JT TRANSPORTES")

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ex.: 849 (vazio para ignorar)")

        self.input_rota_carga = QLineEdit()
        self.input_carga.setPlaceholderText("Ex: JT TRANSPORTES (opcional se usar só rota)")

        self.btn_add_carga_box = QPushButton("Adicionar carga/box")
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

    def carregar_configuracoes(self):
        self.carregar_rotas()
        self.carregar_cargas_box()

    def carregar_rotas(self):
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
        if "=>" not in item_text:
            return None
        
        carga, resto = item_text.split("=>", 1)
        carga = carga.strip()
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
        if rota:
            return f"{carga} => {box} | rota: {rota}"
        
        return f"{carga} => {box}"

    def carregar_cargas_box(self):
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

                if not box:
                    continue

                if not carga and not rota:
                    continue

                self.lista_cargas_box.addItem(self._format_carga_box_item(carga, box, rota))

    def adicionar_rota(self):
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
        carga = self.input_carga.text().strip()
        box = self.input_box.text().strip()
        rota = self.input_rota_carga.text().strip()

        if not rota and not carga:
            QMessageBox.warning(self, "Campo vazio", "Digite uma transportadora ou uma rota para adicionar.")
            return

        if not box:
            QMessageBox.warning(self, "Campo vazio", "Digite um box para a regra de boxiamento.")
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

            if not box:
                continue

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