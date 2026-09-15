from __future__ import annotations

from prweb.client import PcommClient
from prweb.reset import ResetPcomm

class RoutineS7EA:

    @staticmethod
    def gotoroutineS7EA(pcom = PcommClient) -> None:

        ResetPcomm.reset_pcom(pcom)

        pcom.send_key('[enter]')
        pcom.wait_ready()

        verif_COMMAND = pcom.wait_text(23, 2, 7)
        if verif_COMMAND != "COMMAND":
            raise RuntimeError(
                f'Verificação de verif_COMMAND: {verif_COMMAND} não retornou a tela esperada, encerrando tentativa'
            )

        pcom.send_text('3')
        pcom.send_key('[enter]')
        pcom.wait_ready()
        pcom.send_text('S7EA')
        pcom.send_text('[enter]')
        pcom.wait_ready()

        verif_S7EA = pcom.wait_text(1 , 2, 4)

        if verif_S7EA != "S7EA":
            raise RuntimeError(
                f'Verificação de verif_S7EA: {verif_S7EA} não retornou a tela esperada, encerrando tentativa'
            )

        pcom.wait_ready()
        pcom.send_text('211200d')

        print('Tela S7EA pronta para uso')