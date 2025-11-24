# 🤖 Central de Controle RoboSoco 5001

Simulador de uma central de controle para um robô de resgate em túneis, chamado "RoboSoco 5001". A interface gráfica, construída com Tkinter, permite monitorar o robô em tempo real, visualizar vítimas detectadas, e gerar relatórios de missão.

## ✨ Funcionalidades

- **Dashboard em Tempo Real**: Monitore a posição, bateria, temperatura e status do robô.
- **Mapeamento do Túnel**: Visualize a trajetória do robô e a localização das vítimas em um mapa 2D.
- **Detecção de Vítimas**: O robô detecta vítimas, tira fotos e aplica kits de primeiros socorros automaticamente.
- **Painel de Detalhes da Vítima**: Veja informações detalhadas de cada vítima selecionada, incluindo gravidade, estado e uma imagem representativa.
- **Logs e Alertas**: Acompanhe os eventos da missão através de um console de logs e um painel de alertas.
- **Geração de Relatório**: Ao final da missão, gere e salve um relatório detalhado em formato `.txt`.

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **Tkinter**: Para a interface gráfica.
- **Matplotlib**: Para a criação dos gráficos (mapa do túnel e imagem das vítimas).
- **Pillow (PIL)**: Para manipulação de imagens.

## 🚀 Como Executar

1.  **Clone o repositório:**
    ```bash
    git clone <URL-DO-SEU-REPOSITORIO>
    cd ProjRoboSoco
    ```

2.  **Instale as dependências:**
    Certifique-se de ter o Python 3 instalado e execute o comando abaixo para instalar as bibliotecas necessárias.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute a aplicação:**
    O script precisa da pasta `imagens` com os arquivos de cenário no mesmo diretório.
    ```bash
    python robosoco.py
    ```