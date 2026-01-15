import shutil
from pathlib import Path

def launch_chromium_custom(playwright):
    """
    Inicializa o chromium com ambiente controlado
    """

    desktop_path = Path.home() / 'Desktop'
    temp_profile = desktop_path / 'playwright_profile'

    # --- Limpeza da temp_profile antes de cada run
    if temp_profile.exists():
        shutil.rmtree(temp_profile)
    temp_profile.mkdir(parents=True, exist_ok=True)

    # --- Configuração Chromium
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=str(temp_profile),
        headless=False,
        args=[
            "--disable-popup-blocking",
            "--disable-notifications",
            "--disable-infobars",
            "--disable-blink-features=AutomationControlled",
            "--no-default-browser-check",
            "--no-first-run",
            "--start-maximized",
            "--disable-extensions",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ],
        chromium_sandbox=False,
    )

    page = browser.new_page()
    return browser, page