from __future__ import annotations

from typing import Optional

import pythoncom
import win32com.client

class PcommClient:

    def __init__(self):
        self.conn_list = None
        self.session = None
        self.ps = None
        self.oia = None

    def connect(self):
        """
        Cria uma instânia de objeto PCOMM, linca handle com sessão
        Obtém objeto OIA e PS
        """
        pythoncom.CoInitialize() # <-- Inicializa a biblioteca COM para a thread atual, permitindo que ela utilize objts COM do Windows.

        """
        Cria uma instância do objt COM PCOMM.autECLConnList do IBM Personal Communications (PCOMM) e a armazena no atributo self.conn_list
        """
        self.conn_list = win32com.client.Dispatch(
            "PCOMM.autECLConnList"
        )

        self.conn_list.Refresh() # <-- Atualiza a lista de sessões do PCOMM disponíveis naquele momento

        if self.conn_list.Count == 0:
            raise RuntimeError(
                "Nenhuma sessão PCOMM aberta encontrada"
            )

        """
        Extrai informações da conexão localizada e armazena em 'target', informações como:
        - Nome da sessão
        - Handle da conexão
        - Estado da sessão
        """
        target = self.conn_list.ConnInfo(1)

        print('Usando sessão:')
        print('Nome:', target.Name)
        print('Handle:', target.Handle)

        self.session = win32com.client.Dispatch(
            "PCOMM.autECLSession"
        )
        """
        Esse objt representa a sessão do PCOMM, permitindo que o programa interaja diretamente com um
        terminaç específico
        """

        self.session.SetConnectionBuHandle(
            target.Handle
        )
        """
        Conecta o objt self.session à sessão do PCOMM identificada pelo Handle (target.Handle)

        SetConnectionByHandle faz com que self.session aponte para a sessão específica.
        """

        self.ps = self.session.autECLPS
        """
        Obtém o objt Presentation Space (PS) da sessão
        Esse objt representa a tela do terminal e permite:
        - Ler textos 
        - Escrever em campos
        - bter caracteres em posições específicas
        - Verificar o conteúdo exibido
        """
        self.oia = self.session.autECLOIA
        """
        Obtém o objt Operator Information Area (OIA) da sessão e o armazena em self.oia
        Esse objt representa a área de status do terminal, permitindo verificar o estado da sessão, como:
        - Teclado bloqueado/liberado
        - Host ocupado/processando
        - Sessão pronta para receber comando
        """

    def disconnect(self):
        """
        Desconecta do PS, OIA, session e conn_list
        """
        self.ps = None
        self.oia = None
        self.session = None
        self.conn_list = None

    try:
        pythoncom.CoUninitialize()
    except Exception:
        pass

    def send_text(
            self,
            text: str,
            row: Optional[int] = None,
            column: Optional[int] = None
    ):
        """
        Envia um texto, a localização do cursor é opcional
        """

        if row is not None and column is not None:
            self.ps.SetCursosPos(row, column)

        self.ps.SendKeys(text)

    def send_key(self, key: str):
        """
        Envia comandos de tecla
        Exemplos:

        send_key('[enter]')
        send_key('[pf3]')
        send_key('[clear]')
        send_key('[pf12]')
        """

        self.ps.SendKeys(key)

    def read(
            self,
            row: int,
            column: int,
            length: int
    ) -> str:
        """
        Faz a leitura de acordo com a posição indicada, retorna em formato de texto
        e remove espaços vázios do inicio e fim com .strip()
        """
        return self.ps.GetText(
            row,
            column,
            length
        ).strip()

    def wait_text(
            self,
            row: int,
            column: int,
            length: int,
            timeout: int = 0.1,
            default: str = ''
    ):
        """
        Espera um texto especificado aparecer
        """
        import time

        start = time.time()

        while True:

            value = self.read(
                row=row,
                column=column,
                length=length
            )

            if value.strip():
                return value.strip()

            if time.time() - start > timeout:
                return default

            time.sleep(0.05)

    def wait_ready(self, timeout: int = 30):
        """
        Espera o terminal ficar disponível para próxima ação    
        """

        import time

        start = time.time()

        while True:

            if self.oia.InputInhibited == 0:
                return

            if time.time() - start > timeout:
                raise TimeoutError(
                    "Terminal não está disponível"
                )

            time.sleep(0.05)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()