import os
import json

from pathlib import Path
from logging import getLogger

logger = getLogger("RPA")

class AppConfig:

    DEFAULT_ROTAS = [
        "2950", "1989", "2023", "2869",
        "2870", "2871", "2872", "2873",
        "2874", "2875", "2896", "2922",
        "2923", "2925", "2937", "2938",
        ]

    def __init__(self, theme_source_path: Path | None = None):
        self.CONFIG_ROTA = self._CREATE_CONFIG_DIRECTORY()
        self.ROTAS_FILE = self.CONFIG_ROTA / "rotas.json"
        self.DARK_THEME_FILE = self.CONFIG_ROTA / 'dark_theme.qss'
        self.theme_source_path = Path(theme_source_path) if theme_source_path else None

        self._ensure_rotas_file()
        self._ensure_dark_theme_file()

    def _CREATE_CONFIG_DIRECTORY(self) -> Path:
        # Pega caminho padrão do AppData Local
        local_appdata = os.getenv("LOCALAPPDATA")

        if not local_appdata:
            logger.warning("Não foi possível encontrar o diretório LOCALAPPDATA.")

        ROTA_PATH = Path(local_appdata) / 'config_app_online'
        ROTA_PATH.mkdir(parents=True, exist_ok=True)

        return ROTA_PATH
    
    def _ensure_rotas_file(self):
        """
        Cria o rotas.json se ele não existir,
        Não sobreescreve
        """
        if not self.ROTAS_FILE.exists():
            DATA = {
                "sp_rotas": self.DEFAULT_ROTAS
            }

            with open(self.ROTAS_FILE, 'w', encoding='utf-8') as f:
                json.dump(DATA, f, indent=4, ensure_ascii=False)

    def _ensure_dark_theme_file(self):
        """
        Cria o dark_theme.qss na pasta local se ele não existir,
        copiando o conteúdo do arquivo padrão do projeto.
        """

        if self.DARK_THEME_FILE.exists():
            return
        
        if not self.theme_source_path or not self.theme_source_path.exists():
            logger.warning("Arquivo dark_theme.qss padrão não encontrado pela cópia.")
            return
        
        with open(self.theme_source_path, "r", encoding='utf-8') as source_file:
            theme_content = source_file.read()
        
        with open(self.DARK_THEME_FILE, "w", encoding='utf-8') as target_file:
            target_file.write(theme_content)