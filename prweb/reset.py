from __future__ import annotations

from prweb.client import PcommClient

class ResetPcomm:

    @staticmethod
    def reset_pcom(pcom = PcommClient) -> None:
        """
        Envia série de comandos que retorna para a págijna primária do PCOMM
        """
        pcom.send_key('[pf9]')
        pcom.wait_ready()
        pcom.send_key('[pf3]')