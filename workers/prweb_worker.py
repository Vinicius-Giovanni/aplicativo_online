from PySide6.QtCore import QObject, Signal

from prweb.prweb_functions import (
    start_browser,
    login_prweb,
    filtragem_de_carga,
    emissao_de_carga,
    boxiamento_carga
)

class PrwebWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, params: dict):
        super().__init__()
        self.params = params

    def run(self):
        try:
            playwright, browser, page = start_browser()

            login_prweb(
                page=page,
                empresa=self.params["empresa"],
                matricula=self.params["matricula"],
                password=self.params["password"]
            )

            action = self.params.get("action")

            if action == "filtragem":
                filtragem_de_carga(
                    page=page,
                    empresa=self.params["empresa"],
                    matricula=self.params["matricula"],
                    password=self.params["password"],
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
                    data=self.params["data"]
                )
                
            elif action == "boxiamento":
                boxiamento_carga(
                    page=page,
                    empresa=self.params["empresa"],
                    matricula=self.params["matricula"],
                    password=self.params["password"],
                    data=self.params["data"]
                )
            else:
                raise ValueError("Ação não reconhecida, verifique o módulo prweb_worker")

        except Exception as e:
            self.error.emit(str(e))

        finally:
            try:
                browser.close()
                playwright.stop()
            except:
                pass

            self.finished.emit()
