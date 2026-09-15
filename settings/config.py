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
    DEFAULT_CARGAS_BOX_BR_SAMOR = [
        {"Filial": 1042, "Box": 875},
        {"Filial": 1393, "Box": 876},
        {"Filial": 1144, "Box": 877},
        {"Filial": 1691, "Box": 878},
        {"Filial": 1261, "Box": 879},
        {"Filial": 1002, "Box": 880},
        {"Filial": 1348, "Box": 881},
        {"Filial": 1616, "Box": 882},
        {"Filial": 718, "Box": 883},
        {"Filial": 1532, "Box": 884},
        {"Filial": 1252, "Box": 885},
        {"Filial": 1304, "Box": 886},
        {"Filial": 1009, "Box": 887},
        {"Filial": 1115, "Box": 888},
        {"Filial": 1013, "Box": 889},
        {"Filial": 1028, "Box": 890},
        {"Filial": 1114, "Box": 891},
        {"Filial": 1525, "Box": 892},
        {"Filial": 1270, "Box": 893},
        {"Filial": 1224, "Box": 894},
        {"Filial": 1560, "Box": 895},
        {"Filial": 1220, "Box": 896},
        {"Filial": 1286, "Box": 897},
        {"Filial": 1061, "Box": 898},
        {"Filial": 1218, "Box": 899},
        {"Filial": 1015, "Box": 900},
        {"Filial": 2233, "Box": 901},
        {"Filial": 1391, "Box": 902},
        {"Filial": 735, "Box": 903},
        {"Filial": 1265, "Box": 904},
        {"Filial": 1060, "Box": 905},
        {"Filial": 1098, "Box": 906},
        {"Filial": 1535, "Box": 907},
        {"Filial": 1022, "Box": 908},
        {"Filial": 1256, "Box": 909},
        {"Filial": 1029, "Box": 910},
        {"Filial": 1527, "Box": 911},
        {"Filial": 1394, "Box": 912},
        {"Filial": 1336, "Box": 913},
        {"Filial": 1392, "Box": 914},
        {"Filial": 1269, "Box": 915},
        {"Filial": 1150, "Box": 916},
        {"Filial": 1406, "Box": 917},
        {"Filial": 1413, "Box": 918},
        {"Filial": 1146, "Box": 919},
        {"Filial": 1353, "Box": 920},
        {"Filial": 1603, "Box": 921},
        {"Filial": 1271, "Box": 922},
        {"Filial": 85, "Box": 923},
        {"Filial": 1050, "Box": 924},
        {"Filial": 1210, "Box": 925},
        {"Filial": 1046, "Box": 926},
        {"Filial": 1116, "Box": 927},
        {"Filial": 1008, "Box": 928},
        {"Filial": 1023, "Box": 929},
        {"Filial": 1276, "Box": 930},
        {"Filial": 1209, "Box": 931},
        {"Filial": 1476, "Box": 932},
        {"Filial": 1590, "Box": 933},
        {"Filial": 1024, "Box": 934},
        {"Filial": 1172, "Box": 935},
        {"Filial": 1287, "Box": 936},
        {"Filial": 1456, "Box": 937},
        {"Filial": 1072, "Box": 938},
        {"Filial": 1594, "Box": 939},
        {"Filial": 1366, "Box": 940},
        {"Filial": 1086, "Box": 941},
        {"Filial": 1455, "Box": 942},
        {"Filial": 2061, "Box": 943},
        {"Filial": 1100, "Box": 944},
        {"Filial": 1147, "Box": 945},
        {"Filial": 1057, "Box": 946},
        {"Filial": 2032, "Box": 947},
        {"Filial": 1207, "Box": 948},
        {"Filial": 1000, "Box": 949},
        {"Filial": 2098, "Box": 950},
        {"Filial": 1282, "Box": 951},
        {"Filial": 1487, "Box": 952},
        {"Filial": 1865, "Box": 953},
        {"Filial": 1294, "Box": 954},
        {"Filial": 3000, "Box": 955},
        {"Filial": 1268, "Box": 956},
        {"Filial": 2227, "Box": 957},
        {"Filial": 1563, "Box": 958},
        {"Filial": 1430, "Box": 959},
        {"Filial": 1592, "Box": 960},
        {"Filial": 1231, "Box": 961},
        {"Filial": 1034, "Box": 962},
        {"Filial": 1564, "Box": 963},
        {"Filial": 1367, "Box": 964},
        {"Filial": 1031, "Box": 965},
        {"Filial": 1103, "Box": 966},
        {"Filial": 1709, "Box": 967},
        {"Filial": 1235, "Box": 968},
        {"Filial": 1593, "Box": 969},
        {"Filial": 1821, "Box": 970},
        {"Filial": 1613, "Box": 971},
        {"Filial": 1411, "Box": 972},
        {"Filial": 1360, "Box": 973},
        {"Filial": 1408, "Box": 974},
        {"Filial": 1129, "Box": 975},
        {"Filial": 2047, "Box": 976},
        {"Filial": 1263, "Box": 977},
        {"Filial": 1058, "Box": 978},
        {"Filial": 1127, "Box": 979},
        {"Filial": 1295, "Box": 980},
        {"Filial": 1219, "Box": 981},
        {"Filial": 2120, "Box": 982},
        {"Filial": 1226, "Box": 983},
        {"Filial": 1434, "Box": 984},
        {"Filial": 3100, "Box": 985},
        {"Filial": 1211, "Box": 986},
        {"Filial": 1073, "Box": 987},
        {"Filial": 1236, "Box": 988},
        {"Filial": 1213, "Box": 989},
        {"Filial": 2219, "Box": 990},
        {"Filial": 4000, "Box": 991},
        {"Filial": 1612, "Box": 992},
        {"Filial": 1068, "Box": 993},
        {"Filial": 1389, "Box": 994},
    ]

    def __init__(self, theme_source_path: Path | None = None):
        self.CONFIG_ROTA = self._CREATE_CONFIG_DIRECTORY()
        self.ROTAS_FILE = self.CONFIG_ROTA / "rotas.json"
        self.CARGAS_BOX_FILE = self.CONFIG_ROTA / "cargas_box.json"
        self.BOX_BR_SAMOR_FILE = self.CONFIG_ROTA / "boxiamento_br_samor_par.json"
        self.DARK_THEME_FILE = self.CONFIG_ROTA / 'dark_theme.qss'
        self.theme_source_path = Path(theme_source_path) if theme_source_path else None

        self._ensure_rotas_file()
        self._ensure_cargas_box_file()
        self._ensure_dark_theme_file()
        self._ensure_cargas_box_br_samor()

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

    def _ensure_cargas_box_br_samor(self):
        """
        Garane que o arquivo de boxiamento padrao seja criado
        """

        if not self.BOX_BR_SAMOR_FILE.exists():
            with open(self.BOX_BR_SAMOR_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CARGAS_BOX_BR_SAMOR, f, indent=4, ensure_ascii=False)