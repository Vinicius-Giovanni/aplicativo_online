import sys
from PySide6.QtWidgets import QApplication

from app.login_window import LoginWindow

import os
from pathlib import Path
from PySide6.QtGui import QIcon

from logging import getLogger
logger = getLogger("RPA")

def configure_playwright():
    if hasattr(sys, "_MEIPASS"):
        browser_path = Path(sys._MEIPASS) / "playwright"
    else:
        browser_path = Path("playwright")

    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_path)

configure_playwright()

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

def app():
    app = QApplication(sys.argv)

    icon_path = resource_path(r"app\assets\icons\app.ico")

    app.setWindowIcon(QIcon(str(icon_path)))

    try:
        with open(r"app\styles\dark_theme.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        logger.info("Arquivo dark_teme.qss não encontrado.")

    # loggin window
    window = LoginWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    app()