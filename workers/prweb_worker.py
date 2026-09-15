from PySide6.QtCore import QObject, Signal

from prweb.prweb_functions import (
    start_browser,
    login_prweb,
    filtragem_de_carga,
    emissao_de_carga,
    boxiamento_carga,
    boxiamento_carga_par
)

class PrwebWorker(QObject):
    """
    Worker assíncrono responsável pela execução de automações no sistema PRWEB
    utilizando Playwright, integrado ao Qt via sinais (PySide6).

    Executa diferentes fluxos de automação baseados na ação informada em `params`:
        - filtragem de carga
        - emissão de carga
        - boxeamento de carga

    Emite sinais para controle de estado da execução:
        - finished: sempre emitido ao final da execução (sucesso ou falha)
        - succeeded: emitido quando o fluxo executa sem erros
        - error: emitido em caso de exceção
    """
    finished = Signal()
    succeeded = Signal()
    error = Signal(str)

    def __init__(self, params: dict):
        super().__init__()
        self.params = params

    def run(self):
        """
        Executa o fluxo de automação definido em params["action"].
        """

        playwright = None
        browser = None

        try:

            # ==========================================================
            # BOXIAMENTO PAR
            # ==========================================================
            # Essa automação NÃO utiliza Playwright.
            # Portanto, executamos diretamente antes de iniciar
            # o navegador.
            # ==========================================================

            action = self.params.get("action")

            if action == "boxiamento par":

                boxiamento_carga_par(
                    empresa=self.params["empresa"],
                    matricula=self.params["matricula"],
                    password=self.params["password"],
                    dt_entrega=self.params["data"],
                    df=self.params["df"]
                )

            else:

                # ======================================================
                # AUTOMAÇÕES QUE UTILIZAM PLAYWRIGHT
                # ======================================================

                playwright, browser, page = start_browser()

                login_prweb(
                    page=page,
                    empresa=self.params["empresa"],
                    matricula=self.params["matricula"],
                    password=self.params["password"]
                )

                if action == "filtragem":

                    filtragem_de_carga(
                        page=page,
                        empresa=self.params["empresa"],
                        matricula=self.params["matricula"],
                        password=self.params["password"],
                        sku=self.params.get("sku", ""),
                        dt_limite_exp_retro=self.params["dt_limite_exp_retro"],
                        dt_limite_exp_posterior=self.params["dt_limite_exp_posterior"],
                        dt_limite_exp_start=self.params["dt_limite_exp_start"],
                        dt_limite_exp_end=self.params["dt_limite_exp_end"],
                        mono=self.params["mono"],
                        multiplo=self.params["multiplo"],
                        B2B=self.params["B2B"],
                        B2C=self.params["B2C"],
                        CROSSDOCKING=self.params["CROSSDOCKING"],
                        dt_entrega=self.params["dt_entrega"],
                        modalidade=self.params["modalidade"]
                    )

                elif action == "emissao":

                    emissao_de_carga(
                        page=page,
                        empresa=self.params["empresa"],
                        matricula=self.params["matricula"],
                        password=self.params["password"],
                        data=self.params["data"],
                        rotas=self.params.get("rotas")
                    )

                elif action == "boxiamento":

                    boxiamento_carga(
                        page=page,
                        empresa=self.params["empresa"],
                        matricula=self.params["matricula"],
                        password=self.params["password"],
                        data=self.params["data"],
                        rotas=self.params.get("rotas")
                    )

                else:
                    raise ValueError(
                        "Ação não reconhecida, verifique o módulo prweb_worker"
                    )

            # Se chegou aqui sem exceção, deu certo.
            self.succeeded.emit()

        except Exception as e:

            self.error.emit(str(e))

        finally:

            # Só tenta fechar o navegador se ele realmente foi iniciado.
            if browser:
                browser.close()

            if playwright:
                playwright.stop()

            self.finished.emit()