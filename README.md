# APLICATIVO ONLINE

Aplicativo voltado a automação da programação do online,


Para instalar o app, rode no terminal e baixe a pasta chromium-1194 da biblioteca playwright
    pyinstaller main.py `
    --onefile `
    --windowed `
    --icon=app/assets/icons/app.ico `
    --add-data "app/assets;app/assets" `
    --add-data "app/styles;app/styles" `
    --add-data "playwright;playwright"