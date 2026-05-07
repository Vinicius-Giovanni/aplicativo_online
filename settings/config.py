import os
import json

from pathlib import Path
from logging import getLogger

logger = getLogger("RPA")

class AppConfig:
    """
    Gerencia arquivos de configuração locais da aplicação, garantindo a existência
    e integridade de arquivos JSON e arquivos de tema (QSS).

    Responsável por:
        - Criar diretório de configuração no AppData (Windows)
        - Inicializar arquivos de rotas e cargas/box
        - Sincronizar arquivo de tema (dark_theme.qss)
    """

    DEFAULT_ROTAS = [
        "2950", "1989", "2023", "2869",
        "2870", "2871", "2872", "2873",
        "2874", "2875", "2896", "2922",
        "2923", "2925", "2937", "2938",
        ]
    
    DEFAULT_CARGAS_BOX = [
        {"carga": "", "box": "840", "rota": "2872"},
        {"carga": "", "box": "871", "rota": "2875"},
        {"carga": "", "box": "872", "rota": "2874"},
        {"carga": "", "box": "871", "rota": "2873"},
        {"carga": "L MEGA 1200>1624", "box": "840", "rota": "2872"},
        {"carga": "L MEGA 1200>1475", "box": "871", "rota": "2875"},
        {"carga": "L MEGA 1200>1500", "box": "872", "rota": "2874"},
        {"carga": "L MEGA 1200>1760", "box": "871", "rota": "2873"},
        {"carga": "JT TRANSPORTES", "box": "849", "rota": ""},
        {"carga": "CARRIERS", "box": "", "rota": ""},
        {"carga": "ANJUN", "box": "848", "rota": ""},
        {"carga": "PACIFICO", "box": "843", "rota": ""},
        {"carga": "BRASIL WEB", "box": "847", "rota": ""},
        {"carga": "LOGAN", "box": "842", "rota": ""},
        {"carga": "VENKON", "box": "844", "rota": ""},
        {"carga": "SEDEX", "box": "850", "rota": ""},
        {"carga": "TRILOG", "box": "839", "rota": ""},
        {"carga": "ASAP LOG", "box": "870", "rota": ""}
    ]

    def __init__(self, theme_source_path: Path | None = None):
        self.CONFIG_ROTA = self._CREATE_CONFIG_DIRECTORY()
        self.ROTAS_FILE = self.CONFIG_ROTA / "rotas.json"
        self.CARGAS_BOX_FILE = self.CONFIG_ROTA / "cargas_box.json"
        self.DARK_THEME_FILE = self.CONFIG_ROTA / 'dark_theme.qss'
        self.theme_source_path = Path(theme_source_path) if theme_source_path else None

        self._ensure_rotas_file()
        self._ensure_cargas_box_file()
        self._ensure_dark_theme_file()

    def _CREATE_CONFIG_DIRECTORY(self) -> Path:
        """
        Cria e retorna o diretório de configuração da aplicação no AppData Local.

        O diretório criado segue o padrão:
            %LOCALAPPDATA%/config_app_online

        Returns:
            Path: Caminho do diretório de configuração.

        Raises:
            Warning: Caso a variável de ambiente LOCALAPPDATA não esteja disponível.
        """

        local_appdata = os.getenv("LOCALAPPDATA")

        if not local_appdata:
            logger.warning("Não foi possível encontrar o diretório LOCALAPPDATA.")

        ROTA_PATH = Path(local_appdata) / 'config_app_online'
        ROTA_PATH.mkdir(parents=True, exist_ok=True)

        return ROTA_PATH
    
    def _ensure_rotas_file(self):
        """
        Garante a existência do arquivo rotas.json.

        Caso o arquivo não exista, cria com as rotas padrão definidas em DEFAULT_ROTAS.
        Não sobrescreve arquivos existentes.
        """
        if not self.ROTAS_FILE.exists():
            DATA = {
                "sp_rotas": self.DEFAULT_ROTAS
            }

            with open(self.ROTAS_FILE, 'w', encoding='utf-8') as f:
                json.dump(DATA, f, indent=4, ensure_ascii=False)

    def _ensure_dark_theme_file(self):
        """
        Garante a existência do arquivo cargas_box.json.

        Caso não exista, cria o arquivo utilizando os dados padrão definidos em
        DEFAULT_CARGAS_BOX. Não sobrescreve arquivos existentes.
        """
        
        if not self.theme_source_path or not self.theme_source_path.exists():
            logger.warning("Arquivo dark_theme.qss padrão não encontrado pela cópia.")
            return
        
        with open(self.theme_source_path, "r", encoding='utf-8') as source_file:
            theme_content = source_file.read()

        if self.DARK_THEME_FILE.exists():
            with open(self.DARK_THEME_FILE, "r", encoding="utf-8") as target_file:
                current_content = target_file.read()
            
            if current_content == theme_content:
                return
            
            logger.info("Atualizando dark_theme.qss local com a versão mais recente do projeto.")
        
        with open(self.DARK_THEME_FILE, "w", encoding='utf-8') as target_file:
            target_file.write(theme_content)

    def _ensure_cargas_box_file(self):
        """
        Garante sincronização do arquivo dark_theme.qss local com o arquivo base.

        Regras:
            - Se o arquivo base não existir, apenas registra warning.
            - Se o arquivo local não existir, ele é criado.
            - Se existir e estiver diferente, é atualizado.

        Comportamento:
            - Evita sobrescrita desnecessária.
            - Mantém o tema local sempre atualizado com o padrão do projeto.
        """
        if not self.CARGAS_BOX_FILE.exists():
            with open(self.CARGAS_BOX_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CARGAS_BOX, f, indent=4, ensure_ascii=False)