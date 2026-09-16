"""
Responsavel pela construção do laytou da página que executa a automação 
"""

from pathlib import Path

import pandas as pd

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QFormLayout,
    QMessageBox,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import QThread
from workers.prweb_worker import PrwebWorker
from settings.config import AppConfig
from PySide6.QtWidgets import QFileDialog

class BoxiamentoCargaPAR(QWidget):
    def __init__(self, empresa, matricula, password):
        super().__init__()

        self.empresa = empresa
        self.matricula = matricula
        self.password = password
        self.app_config = AppConfig()

        self.setup_ui()

    def setup_ui(self):
        """
        Responsável pela construção da interface da página de boxeamento, incluindo a configuração
        dos componentes visuais, interação do usuário e achinamento das funções de automação.
        """

        self.df_planejamento = None

        # Data Processamento
        self.dt_entrega_par = QLineEdit(maxLength=8)
        self.dt_entrega_par.setPlaceholderText("DDMMAAAA")

        # Área de upload
        self.drop_area = DropArea(self)

        # Nome do arquivo
        self.lbl_arquivo = QLabel("Nenhum arquivo carregado.")

        # Tabela
        self.tabela_planejamento = QTableWidget()
        self.tabela_planejamento.setObjectName("TabelaPlanejamento")
        self.tabela_planejamento.setVisible(False)

        self.tabela_planejamento.setColumnCount(0)
        self.tabela_planejamento.setRowCount(0)

        # Imepde edição pelo usuário
        self.tabela_planejamento.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        # Ajusta colunas
        self.tabela_planejamento.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # Botão
        self.btn_executar_par = QPushButton("Executar Boxiamento de Cargas BrSamor")
        self.btn_executar_par.clicked.connect(self.executar_boxiamento_par)

        # Botão baixar tabela
        self.btn_baixar_tabela = QPushButton("Baixar tabela")
        self.btn_baixar_tabela.clicked.connect(self.baixar_tabela)

        self.btn_baixar_tabela.setEnabled(False)

        # Layout
        form = QFormLayout()
        form.addRow("Data Processamento:", self.dt_entrega_par)

        layout = QVBoxLayout()
        layout.addLayout(form)

        layout.addWidget(self.drop_area)
        layout.addWidget(self.lbl_arquivo)
        layout.addWidget(self.tabela_planejamento)
        layout.addWidget(self.btn_baixar_tabela)
        layout.addWidget(self.btn_executar_par)
        self.setLayout(layout)

    def atualizar_tabela(self, df):
        """
        Exibe o Df tratado na tabela da interface
        """

        self.tabela_planejamento.clear()

        self.tabela_planejamento.setRowCount(len(df))
        self.tabela_planejamento.setColumnCount(len(df.columns))

        self.tabela_planejamento.setHorizontalHeaderLabels(
            df.columns.tolist()
        )

        for linha in range(len(df)):
            for coluna in range(len(df.columns)):

                valor = df.iloc[linha, coluna]

                # Trata valores NaN
                if pd.isna(valor):
                    valor = ""

                item = QTableWidgetItem(str(valor))

                self.tabela_planejamento.setItem(
                    linha,
                    coluna,
                    item
                )

    def arquivo_recebido(self, caminho):
        from prweb.dataframe import ler_e_tratar_planejamento
        try:
            df = pd.read_excel(caminho)

            self.df_planejamento = ler_e_tratar_planejamento(df)
            self.btn_baixar_tabela.setEnabled(True)

            # att info do arquivo
            self.lbl_arquivo.setText(
                f"Arquivo: {Path(caminho).name} | "
                f"Registros: {len(self.df_planejamento)}"
            )

            # Mostra o df tratato
            self.atualizar_tabela(
                self.df_planejamento
            )

            QMessageBox.information(
                self,
                "Arquivo carregado",
                f"Arquivo carregado com sucesso!\n\n"
                f"Registros: {len(self.df_planejamento)}"
            )

            self.tabela_planejamento.setVisible(True)

        except Exception as e:
            self.df_planejamento = None

            self.tabela_planejamento.clear()
            self.tabela_planejamento.setRowCount(0)
            self.tabela_planejamento.setColumnCount(0)

            self.lbl_arquivo.setText(
                "Nenhum arquivo carregado."
            )

            QMessageBox.critical(
                self,
                "Erro ao carregar arquivo",
                f"Não foi possível processar o arquivo.\n\n{e}"
            )


    def executar_boxiamento_par(self):
        """
        Executa o boxiamento
        """

        if not self.dt_entrega_par.text():
            QMessageBox.warning(self, "Campo obrigatório", "A data de processamento deve ser preenchida.")
            return

        if self.df_planejamento is None:
            QMessageBox.warning(
                self,
                "Arquivo obrigatório",
                "Arraste um arquivo XLSX para a área indicada."
            )
            return

        self.btn_executar_par.setEnabled(False)

        params = {
            "action": "boxiamento par",
            "empresa": self.empresa,
            "matricula": self.matricula,
            "password": self.password,
            "data": self.dt_entrega_par.text(),
            "df": self.df_planejamento,
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
        self.btn_executar_par.setEnabled(True)

    def on_error(self, message):
        """
        Controla o estado do botão de execuçã da automação.

        Em caso de falha durante o processamento,
        o botão é reabilitado para permitir uma nova tentativa. 
        """

        QMessageBox.critical(self, "Erro", message)
        self.btn_executar_par.setEnabled(True)

    def baixar_tabela(self):
        if self.df_planejamento is None or self.df_planejamento.empty:
            QMessageBox.warning(self,
                                "Aviso",
                                "Não existe uma tabela para baixar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar tabela",
            "planejamento_tratado_xlsx",
            "Excel (*.xlsx)"
        )

        if not caminho:
            return

        try:
            self.df_planejamento.to_excel(
                caminho,
                index=False
            )

            QMessageBox.information(
                self,
                "Sucesso",
                "Tabela salva com sucesso!"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível salvar a tabela:\n{e}"
            )


class DropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)

        self.label = QLabel(
            "Arraste o arquivo XLSX para cá"
        )

        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.setMinimumHeight(150)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]

            if url.isLocalFile():
                path = Path(url.toLocalFile())

                if path.suffix.lower() == ".xlsx":
                    event.acceptProposedAction()
                    return

        event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            return

        url = event.mimeData().urls()[0]

        if not url.isLocalFile():
            return

        path = Path(url.toLocalFile())

        if path.suffix.lower() != ".xlsx":
            return

        self.label.setText(path.name)

        # Envia o caminho para a janela principal
        self.parent().arquivo_recebido(str(path))

        event.acceptProposedAction()