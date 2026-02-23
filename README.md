# Aplicativo Online (RPA PRWEB)

Aplicativo desktop em **Python + PySide6** para automatizar etapas operacionais no PRWEB, reduzindo tarefas manuais de programação de cargas e aumentando a velocidade do fluxo logístico.

---

## 📌 Visão geral

O projeto foi desenvolvido para transformar um processo repetitivo e demorado em uma operação guiada por interface, com execução automatizada via Playwright.

Com o aplicativo, é possível concentrar a atuação do time em análise e tomada de decisão, enquanto o sistema executa automaticamente os passos operacionais no PRWEB.

---

## 🚀 Funcionalidades principais

- **Login no PRWEB com interface gráfica**.
- **Filtragem de cargas** com parâmetros de data e modalidade.
- **Emissão de cargas** automatizada.
- **Boxiamento de carga** automatizado.
- **Painel de logs em tempo real** dentro do aplicativo.
- **Tema escuro e configuração local automática** (rotas e estilo).

---

## 🧱 Arquitetura do projeto

A aplicação é organizada por camadas simples:

- `app/`: telas e componentes da interface (login, painel principal, módulos operacionais e logs).
- `workers/`: worker responsável por executar a automação em background.
- `prweb/`: funções de automação com Playwright para login, filtragem, emissão e boxiamento.
- `settings/`: configuração da aplicação (tema, diretório local, rotas padrão e Chromium customizado).
- `log/`: configuração e integração de logs com a UI.
- `main.py`: ponto de entrada da aplicação.

---

## 🛠️ Stack tecnológica

- **Python 3.12+**
- **PySide6** (interface desktop)
- **Playwright** (automação web)
- **Pandas / NumPy** (tratamento de dados)
- **PyInstaller** (empacotamento para distribuição)

---

## ✅ Pré-requisitos

Antes de executar o projeto, garanta que você tenha:

1. Python 3.12 ou superior
2. Dependências instaladas
3. Navegador do Playwright disponível na pasta esperada pelo app

> Observação: o projeto foi estruturado com foco em ambiente Windows (uso de `LOCALAPPDATA` e dependências específicas como `pywin32`).

---

## 📦 Instalação

### Opção 1 — usando `uv` (recomendado se você já usa uv)

```bash
uv sync
```

### Opção 2 — usando `pip`

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -U pip
pip install -e .
```

---

## ▶️ Executando localmente

```bash
python main.py
```

Ao iniciar, o app:

- define a variável `PLAYWRIGHT_BROWSERS_PATH`;
- carrega o tema escuro;
- cria arquivos de configuração local automaticamente quando necessário.

---

## ⚙️ Configuração local automática

Na primeira execução, a aplicação cria uma pasta em `%LOCALAPPDATA%/config_app_online` com:

- `rotas.json` (rotas padrão);
- `dark_theme.qss` (tema escuro para customização local).

Essa estratégia permite ajustar tema/rotas sem editar o código-fonte.

---

## 🧪 Qualidade e testes

O projeto inclui `pytest` nas dependências, porém os testes automatizados ainda podem ser expandidos para cobrir:

- fluxos da interface;
- validação de parâmetros;
- cenários de erro da automação no PRWEB.

---

## 📁 Estrutura resumida

```text
aplicativo_online/
├── app/
├── log/
├── prweb/
├── settings/
├── workers/
├── main.py
├── pyproject.toml
└── README.md
```

---

## 🏗️ Empacotamento (build)

Exemplo de build com PyInstaller:

```bash
pyinstaller main.py \
  --onefile \
  --windowed \
  --icon=app/assets/icons/app.ico \
  --add-data "app/assets;app/assets" \
  --add-data "app/styles;app/styles" \
  --add-data "playwright;playwright"
```

---

## 🔒 Boas práticas operacionais

- Utilize credenciais de acesso conforme políticas internas.
- Evite executar múltiplas automações concorrentes com a mesma conta.
- Monitore o painel de logs para auditoria e diagnóstico rápido.

---

## 🤝 Contribuição

Sugestões de melhoria:

- padronização adicional de tipagem e lint;
- suíte de testes para fluxos críticos;
- documentação de troubleshooting (erros comuns de ambiente e PRWEB).

---

## 📄 Licença

Defina a licença do projeto (ex.: MIT, Proprietária, Interna) conforme política da empresa.