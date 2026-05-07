from PySide6.QtCore import QObject, Signal

from prweb.prweb_functions import (
    start_browser,
    login_prweb,
    filtragem_de_carga,
    emissao_de_carga,
    boxiamento_carga
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
        Executa o fluxo principal de automação no PRWEB.

        Fluxo:
            1. Inicializa navegador via Playwright
            2. Realiza login no sistema PRWEB
            3. Executa a ação definida em params["action"]:
                - "filtragem" → filtragem_de_carga
                - "emissao" → emissao_de_carga
                - "boxiamento" → boxiamento_carga
            4. Emite sinal de sucesso ou erro
            5. Finaliza e fecha navegador de forma segura

        Sinais emitidos:
            - succeeded: execução concluída com sucesso
            - error(str): erro capturado durante execução
            - finished: sempre emitido ao final (cleanup garantido)
        """
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
                raise ValueError("Ação não reconhecida, verifique o módulo prweb_worker")
            
            self.succeeded.emit()

        except Exception as e:
            self.error.emit(str(e))

        finally:
            try:
                browser.close()
                playwright.stop()
            except:
                pass

            self.finished.emit()
