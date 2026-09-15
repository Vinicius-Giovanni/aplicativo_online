from __future__ import annotations

from prweb.client import PcommClient
from prweb.reset import ResetPcomm

class RoutineJ2CD:

    @staticmethod
    def gotoroutineJ2CD(pcom = PcommClient) -> None:

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
        pcom.send_text('J2CD')
        pcom.send_text('[enter]')
        pcom.wait_ready()

        verif_J2CD = pcom.wait_text(1 , 2, 4)

        if verif_J2CD != "J2CD":
            raise RuntimeError(
                f'Verificação de verif_J2CD: {verif_J2CD} não retornou a tela esperada, encerrando tentativa'
            )

        pcom.send_text('211200d0200')

        print('Tela J2CD pronta para uso')