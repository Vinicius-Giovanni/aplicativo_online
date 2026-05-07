import sys
from PySide6.QtWidgets import QApplication

from app.login_window import LoginWindow
from settings.config import AppConfig

import os
from pathlib import Path
from PySide6.QtGui import QIcon

from logging import getLogger
logger = getLogger("RPA")

def configure_playwright():
    """
    Configura o caminho dos browsers do Playwright para execução local ou empacotada.

    Define a variável de ambiente PLAYWRIGHT_BROWSERS_PATH de acordo com o contexto:
        - Execução empacotada (PyInstaller): usa sys._MEIPASS
        - Execução local: usa diretório 'playwright' do projeto
    """
    if hasattr(sys, "_MEIPASS"):
        browser_path = Path(sys._MEIPASS) / "playwright"
    else:
        browser_path = Path("playwright")

    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_path)

configure_playwright()

def resource_path(relative_path):
    """
    Resolve o caminho de recursos da aplicação, compatível com execução local e empacotada.

    Em modo empacotado (PyInstaller), utiliza sys._MEIPASS como base.
    Em modo de desenvolvimento, utiliza o diretório raiz do projeto.

    Args:
        relative_path (str | Path): Caminho relativo do recurso.

    Returns:
        Path: Caminho absoluto resolvido do recurso.
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

def app():
    """
    Inicializa a aplicação desktop com PySide6.

    Responsável por:
        - Criar instância da aplicação Qt
        - Definir ícone da aplicação
        - Inicializar configuração global (AppConfig)
        - Carregar e aplicar tema (QSS)
        - Abrir janela de login
        - Iniciar loop principal da aplicação

    Fluxo:
        1. Inicializa QApplication
        2. Resolve recursos (ícone e tema)
        3. Configura ambiente da aplicação
        4. Aplica stylesheet global
        5. Exibe LoginWindow
        6. Executa loop da aplicação
    """
    app = QApplication(sys.argv)

    icon_path = resource_path(r"app\assets\icons\app.ico")

    app.setWindowIcon(QIcon(str(icon_path)))

    theme_source_path = resource_path(Path('app') / 'styles' / 'dark_theme.qss')
    app_config = AppConfig(theme_source_path=theme_source_path)

    try:
        with open(app_config.DARK_THEME_FILE, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        logger.info("Arquivo dark_teme.qss não encontrado na pasta de configuração local.")

    # loggin window
    window = LoginWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    app()