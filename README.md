# RoboSoco 5001 - Simulador de Resgate em Túnel

Este projeto é um simulador de um robô de resgate (`RoboSoco 5001`) que explora um túnel, detecta vítimas, avalia sua condição e presta os primeiros socorros. A aplicação possui uma interface gráfica completa para monitoramento da missão em tempo real.

## Pré-requisitos

- Python 3.8+ instalado e adicionado ao PATH do sistema.

## Instalação

Siga os passos abaixo para configurar e rodar o ambiente de desenvolvimento localmente.

**1. Clone o Repositório (Opcional)**

Se você estiver baixando o código de um repositório Git, use o comando:
```bash
git clone <url-do-seu-repositorio>
cd <nome-da-pasta-do-projeto>
```

**2. Crie um Ambiente Virtual**

É uma boa prática isolar as dependências do projeto em um ambiente virtual.

```bash
# No Windows
python -m venv venv
```

**3. Ative o Ambiente Virtual**

```powershell
# No Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# No Windows (Command Prompt)
.\venv\Scripts\activate.bat
```

**4. Instale as Dependências**

Instale todas as bibliotecas necessárias de uma vez usando o arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

## Como Executar

Com o ambiente virtual ativado e as dependências instaladas, execute o seguinte comando no terminal:

```bash
python robosoco.py
```

A interface gráfica da Central de Controle será iniciada e a simulação começará automaticamente.

## Arquivos Gerados

Ao final de cada missão, você pode gerar um relatório. Se optar por salvá-lo, um arquivo de texto será criado na pasta raiz do projeto com o seguinte formato:

- `relatorio_missao_AAAA-MM-DD_HH-MM-SS.txt`