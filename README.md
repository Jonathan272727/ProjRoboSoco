Robosoco Simulator

Como rodar (Windows PowerShell):

1. Criar e ativar ambiente virtual (se não existir):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
python -m pip install -r requirements.txt
```

3. Rodar o simulador (interativo):

```powershell
python robosoco.py
```

4. Rodar sem interação (ex.: cenário 2 - túnel):

```powershell
python robosoco.py --scenario 2
```

Arquivos gerados:
- relatorio_missao_robosoco_<cenario>_YYYY-MM-DD_HHMMSS.csv

Notas:
- Feche a janela do gráfico para que o script termine e exporte o CSV.
- Se ocorrerem warnings do scikit-learn sobre nomes de features, atualize para a versão mais recente do scikit-learn.
