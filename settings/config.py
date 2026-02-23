import os
import json

from pathlib import Path
from logging import getLogger

logger = getLogger("RPA")

sp_rotas = [
    "2950",
    "1989",
    "2023",
    "2869",
    "2870",
    "2871",
    "2872",
    "2873",
    "2874",
    "2875",
    "2896",
    "2922",
    "2923",
    "2925",
    "2937",
    "2938",
]

class AppConfig:

    DEFAULT_ROTAS = [
        "2950", "1989", "2023", "2869",
        "2870", "2871", "2872", "2873",
        "2874", "2875", "2896", "2922",
        "2923", "2925", "2937", "2938",
        ]

    def __init__(self):
        self.CONFIG_ROTA = self._CREATE_CONFIG_DIRECTORY()
        self.ROTAS_FILE = self.CONFIG_ROTA / "rotas.json"

        self._ensure_rotas_file()

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





    