import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import threading
import time
import random
from PIL import Image, ImageTk
import io
import os

# --- CONFIGURAÇÕES DE IMAGENS ---
# Isso garante que o script encontre a pasta 'imagens' que está no mesmo diretório que ele.
DIRETORIO_DO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PASTA_IMAGENS = os.path.join(DIRETORIO_DO_SCRIPT, "imagens")


# Mapeamento dos arquivos
MAP_CENARIOS = {
    # Cenário Leve/Estável/Verde
    'leve': 'verdeconscienteestavel.png',
    'baixa': 'verdeconscienteestavel.png',
    'consciente': 'verdeconscienteestavel.png',
    'estável': 'verdeconscienteestavel.png',
    'estavel': 'verdeconscienteestavel.png',

    # Cenário Médio/Confuso/Vermelho
    'moderado': 'vermelhoconfusoinstavel.png',
    'média': 'vermelhoconfusoinstavel.png',
    'media': 'vermelhoconfusoinstavel.png',
    'instável': 'vermelhoconfusoinstavel.png',
    'instavel': 'vermelhoconfusoinstavel.png',
    'semi-consciente': 'vermelhoconfusoinstavel.png',
    'semiconsciente': 'vermelhoconfusoinstavel.png',

    # Cenário Grave/Crítico
    'grave': 'graveinconscientecritico.png',
    'crítico': 'graveinconscientecritico.png', # A chave pode ter acento
    'critico': 'graveinconscientecritico.png',
    'inconsciente': 'graveinconscientecritico.png',
    
    # Padrão
    '_default_': 'vermelhoconfusoinstavel.png'
}

# --- VERIFICAÇÃO DA PASTA DE IMAGENS ---
def verificar_pasta_imagens():
    """Verifica se a pasta de imagens existe"""
    if not os.path.exists(PASTA_IMAGENS):
        print(f"❌ ERRO CRÍTICO: A pasta de imagens não foi encontrada no caminho:")
        print(f"   '{os.path.abspath(PASTA_IMAGENS)}'")
        return False
    
    print(f"✅ Pasta de imagens encontrada em: {os.path.abspath(PASTA_IMAGENS)}")
    
    arquivos_necessarios = set(MAP_CENARIOS.values())
    arquivos_existentes = set(os.listdir(PASTA_IMAGENS))
    
    print("\n--- VERIFICAÇÃO DE ARQUIVOS ---")
    print(f"Arquivos que o código ESPERA: {sorted(list(arquivos_necessarios))}")
    print(f"Arquivos que o código ENCONTROU na pasta: {sorted(list(arquivos_existentes))}")
    
    arquivos_faltantes = arquivos_necessarios - arquivos_existentes
    if arquivos_faltantes:
        print(f"⚠️ Arquivos faltantes: {arquivos_faltantes}")
        messagebox.showerror("Erro Crítico", f"Arquivos de imagem essenciais estão faltando na pasta 'imagens':\n\n{', '.join(arquivos_faltantes)}")
        return False
    
    print("✅ Pasta de imagens verificada!")
    print("---------------------------------\n")
    return True

# --- CLASSES PRINCIPAIS ---

class Vitima:
    def __init__(self, x, y, gravidade=None, estado=None):
        self.x = x
        self.y = y
        self.gravidade = gravidade or random.choice(["Leve", "Moderado", "Grave", "Crítico"])
        self.estado = estado or random.choice(["Consciente", "Inconsciente", "Semi-consciente"])
        self.detectada_em = None
        self.foto_tirada = False
        self.kit_aplicado = False
        self.id = f"V{random.randint(1000, 9999)}"
        self.foto_data = self._gerar_imagem_vitima()

    def _get_nome_arquivo_imagem(self):
        """Centraliza a lógica para encontrar o nome do arquivo de imagem com base no estado da vítima."""
        nome_arquivo = MAP_CENARIOS.get('_default_')
        chave_grav = self.gravidade.lower()
        chave_est = self.estado.lower().replace('-', '').replace(' ', '')
        if chave_grav in MAP_CENARIOS:
            nome_arquivo = MAP_CENARIOS[chave_grav]
        elif chave_est in MAP_CENARIOS:
            nome_arquivo = MAP_CENARIOS[chave_est]
        return nome_arquivo

    def _gerar_imagem_vitima(self):
        """Gera a imagem da vítima, com a foto de arquivo dentro de um círculo colorido."""
        fig = Figure(figsize=(3, 3), dpi=80, facecolor='#1e3a5f')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1e3a5f')
        
        cores = {"Leve": "#4CAF50", "Moderado": "#FF9800", "Grave": "#F44336", "Crítico": "#8B0000"}
        cor = cores.get(self.gravidade, "white")

        # Isso servirá como a borda colorida ao redor da imagem.
        circle = plt.Circle((0.5, 0.5), 0.4, color=cor, fill=False, linewidth=4)
        ax.add_patch(circle) 
        # --- LÓGICA PARA CARREGAR A IMAGEM DA VÍTIMA ---
        imagem_adicionada = False
        
        # 1. Encontra o nome do arquivo de imagem correto
        nome_arquivo = self._get_nome_arquivo_imagem()

        # 2. Monta o caminho completo para a imagem
        caminho_imagem = os.path.join(PASTA_IMAGENS, nome_arquivo)

        # 3. Tenta carregar e exibir a imagem dentro do círculo
        if os.path.exists(caminho_imagem):
            try:
                img = plt.imread(caminho_imagem)
                im = ax.imshow(img, extent=(0.1, 0.9, 0.1, 0.9)) 
                clip_circle = plt.Circle((0.5, 0.5), 0.4, transform=ax.transData)
                im.set_clip_path(clip_circle)
                imagem_adicionada = True
            except Exception as e:
                print(f"⚠️ Erro ao carregar a imagem '{caminho_imagem}': {e}")


        # Se não foi possível adicionar a imagem, exibe o texto padrão
        if not imagem_adicionada:
            ax.text(0.5, 0.5, "VÍTIMA", ha='center', va='center', fontsize=14, color='white', weight='bold')
            ax.text(0.5, 0.2, self.gravidade.upper(), ha='center', va='center', fontsize=10, color='white')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=80)
        buf.seek(0)
        return buf.getvalue()

    def detectar(self):
        if not self.detectada_em:
            self.detectada_em = datetime.datetime.now()
            return True
        return False

    def tirar_foto(self):
        if not self.foto_tirada:
            self.foto_tirada = True
            return True
        return False

    def aplicar_kit(self):
        if not self.kit_aplicado:
            melhorias = {"Crítico": "Grave", "Grave": "Moderado", "Moderado": "Leve", "Leve": "Leve"}
            self.gravidade = melhorias.get(self.gravidade, self.gravidade)
            self.kit_aplicado = True
            return True
        return False

    def necessita_kit(self):
        return self.gravidade in ["Crítico", "Grave", "Moderado"] and not self.kit_aplicado

class Cenario:
    def __init__(self, comprimento=200):
        self.comprimento = comprimento
        self.objetos = [
            Vitima(x=30, y=5, gravidade="Leve", estado="Consciente"),
            Vitima(x=80, y=3, gravidade="Moderado", estado="Semi-consciente"),
            Vitima(x=120, y=7, gravidade="Grave", estado="Inconsciente"),
            Vitima(x=180, y=4, gravidade="Crítico", estado="Inconsciente")
        ]

class Robo:
    def __init__(self, central_controle=None):
        self.central_controle = central_controle
        self.memoria_fotos = []
        self.kits_primeiros_socorros = 3
        self.posicao_atual = 0
        self.bateria = 100.0
        self.temperatura = 25.0
        self.velocidade = 2.0
        self.status = "Pronto"

    def mover(self, distancia):
        self.posicao_atual += distancia
        self.bateria = max(0, self.bateria - (distancia * 0.1))
        
    def tirar_foto(self, vitima):
        if vitima.tirar_foto():
            foto_info = {
                'vitima_id': vitima.id,
                'posicao': self.posicao_atual,
                'timestamp': datetime.datetime.now(),
                'gravidade': vitima.gravidade,
                'estado': vitima.estado
            }
            self.memoria_fotos.append(foto_info)
            return True
        return False

    def aplicar_kit(self, vitima):
        if self.kits_primeiros_socorros > 0 and vitima.aplicar_kit():
            self.kits_primeiros_socorros -= 1
            return True
        return False

class CentralDeControle:
    def __init__(self):
        self.robo = None
        self.cenario = None
        self.vitimas_detectadas = []
        self.gui = None
        self.simulacao_ativa = False
        self.vitima_selecionada = None
        self.missao_concluida = False

    def selecionar_vitima(self, vitima):
        self.vitima_selecionada = vitima
        if self.gui:
            self.gui.mostrar_detalhes_vitima(vitima)

    def selecionar_proxima_vitima(self):
        """Seleciona a próxima vítima na lista de detectadas."""
        if not self.vitimas_detectadas or len(self.vitimas_detectadas) < 2:
            return

        try:
            idx_atual = self.vitimas_detectadas.index(self.vitima_selecionada)
            proximo_idx = (idx_atual + 1) % len(self.vitimas_detectadas)
        except (ValueError, AttributeError):
            # Caso nenhuma esteja selecionada ou a selecionada não esteja na lista
            proximo_idx = 0
        
        self.selecionar_vitima(self.vitimas_detectadas[proximo_idx])

    def gerar_relatorio_final(self):
        """Gera um relatório textual com o resumo da missão."""
        if not self.missao_concluida:
            return "A missão ainda não foi concluída."

        # Calcula o total de kits necessários com base no estado inicial de todas as vítimas no cenário
        kits_necessarios_total = sum(1 for v in self.cenario.objetos if v.gravidade in ["Crítico", "Grave", "Moderado"])

        status_final = "Concluída" if self.robo.posicao_atual >= self.cenario.comprimento else "Interrompida"
        
        relatorio = f"--- RELATÓRIO FINAL DA MISSÃO ---\n\n"
        relatorio += f"Data e Hora de Emissão: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        relatorio += f"Status da Missão: {status_final}\n\n"
        
        relatorio += "--- Resumo da Operação ---\n"
        relatorio += f"Distância Total Percorrida: {self.robo.posicao_atual:.1f}m\n"
        relatorio += f"Nível Final da Bateria: {self.robo.bateria:.1f}%\n"
        relatorio += f"Kits de Socorro Utilizados pelo Robô: {3 - self.robo.kits_primeiros_socorros}\n"
        relatorio += f"Total de Kits Necessários na Missão: {kits_necessarios_total}\n\n"
        
        relatorio += f"--- VÍTIMAS DETECTADAS ({len(self.vitimas_detectadas)}) - ORDENADAS POR PRIORIDADE ---\n"
        if not self.vitimas_detectadas:
            relatorio += "Nenhuma vítima foi detectada durante a missão.\n"
        else:
            # Define a ordem de prioridade para ordenação
            ordem_prioridade = {"Crítico": 0, "Grave": 1, "Moderado": 2, "Leve": 3}
            
            # Ordena a lista de vítimas detectadas com base na prioridade
            vitimas_ordenadas = sorted(
                self.vitimas_detectadas, 
                key=lambda v: ordem_prioridade.get(v.gravidade, 4)
            )

            for vitima in vitimas_ordenadas:
                relatorio += f"\n  - Vítima ID: {vitima.id}\n"
                relatorio += f"    Coordenadas (X, Y): ({vitima.x}m, {vitima.y}m)\n"
                relatorio += f"    Gravidade: {vitima.gravidade}\n"
                relatorio += f"    Registro de Campo: {'Sim' if vitima.foto_tirada else 'Não'}\n"
                relatorio += f"    Kit de Socorro Aplicado: {'Sim' if vitima.kit_aplicado else 'Não'}\n"
        return relatorio

    def iniciar_missao(self, robo, cenario):
        print("🚀 INICIANDO MISSÃO...")
        self.robo = robo
        self.cenario = cenario
        self.simulacao_ativa = True
        
        threading.Thread(target=self._executar_missao_completa, daemon=True).start()

    def _executar_missao_completa(self):
        if self.gui:
            self.gui.adicionar_mensagem_console("Missão", "Iniciando varredura do túnel...", "INFO")
        
        while (self.simulacao_ativa and 
               self.robo.posicao_atual < self.cenario.comprimento and 
               self.robo.bateria > 5):
            
            self.robo.mover(self.robo.velocidade)
            self.robo.temperatura = 25 + random.uniform(-1, 3)
            
            self._verificar_deteccao_vitimas()
            
            pacote_dados = {
                'pos_x': self.robo.posicao_atual,
                'pos_y': 5,
                'bateria': self.robo.bateria,
                'status_robo': self._determinar_status(),
                'sensores': {
                    'temp': round(self.robo.temperatura, 1),
                    'risco_estrutural': random.randint(1, 3),
                    'gas': round(random.uniform(0, 0.5), 2)
                }
            }
            
            if self.gui:
                self.gui.atualizar_interface_simulacao(pacote_dados)
            
            time.sleep(0.5)
        
        self.missao_concluida = True
        if self.gui:
            status_final = "Concluída" if self.robo.posicao_atual >= self.cenario.comprimento else "Interrompida"
            self.gui.adicionar_mensagem_console("Missão", f"Missão {status_final}! Posição final: {self.robo.posicao_atual:.1f}m", "SUCESSO")
            self.gui.status_var.set(f"Missão {status_final}")
            self.gui.habilitar_botao_relatorio()

    def _verificar_deteccao_vitimas(self):
        for vitima in self.cenario.objetos:
            distancia = abs(vitima.x - self.robo.posicao_atual)
            
            if distancia < 5 and vitima not in self.vitimas_detectadas:
                if vitima.detectar():
                    self.vitimas_detectadas.append(vitima)
                    
                    if self.gui:
                        self.gui.adicionar_mensagem_console("Detecção", f"Vítima {vitima.id} detectada!", "ALERTA")
                        self.gui.adicionar_alerta("ALERTA", f"Vítima {vitima.id} - {vitima.gravidade}")
                
                if distancia < 2 and not vitima.foto_tirada:
                    if self.robo.tirar_foto(vitima) and self.gui:
                        self.gui.adicionar_mensagem_console("Câmera", f"Foto da vítima {vitima.id}", "INFO")
                
                if distancia < 1 and vitima.necessita_kit() and self.robo.kits_primeiros_socorros > 0:
                    if self.robo.aplicar_kit(vitima) and self.gui:
                        self.gui.adicionar_mensagem_console("Socorro", f"Kit aplicado em {vitima.id}!", "SUCESSO")
                        self.gui.adicionar_alerta("SUCESSO", f"Kit aplicado em {vitima.id}")
                
                if self.gui and not self.vitima_selecionada:
                    self.selecionar_vitima(vitima)
                
                return True
        return False

    def _determinar_status(self):
        if self.missao_concluida:
            return "Missão Concluída"
        elif self.robo.bateria < 10:
            return "Bateria Crítica"
        elif self.robo.bateria < 30:
            return "Bateria Baixa"
        elif len(self.vitimas_detectadas) > 0:
            return "Resgatando Vítimas"
        else:
            return "Explorando"

class CentralControleGUI:
    def __init__(self, central_controle):
        self.central = central_controle
        self.root = tk.Tk()
        self.root.title("Central de Controle RoboSoco 5001")
        self.root.geometry("1800x1000")
        self.root.configure(bg='#0a1929')
        
        self.ultima_atualizacao = tk.StringVar(value="Nunca")
        self.status_geral = tk.StringVar(value="Operacional")
        self.historico_posicoes = []
        self.vitima_photo = None
        
        # Variáveis de status
        self.pos_var = tk.StringVar(value="0.0 m")
        self.bat_var = tk.StringVar(value="100.0%")
        self.status_var = tk.StringVar(value="Iniciando...")
        self.temp_var = tk.StringVar(value="25.0°C")
        self.kits_var = tk.StringVar(value="3")
        self.vitimas_var = tk.StringVar(value="0")
        self.fotos_var = tk.StringVar(value="0")
        self.kits_used_var = tk.StringVar(value="0")
        self.distancia_var = tk.StringVar(value="0.0 m")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.criar_header(main_frame)
        
        body_frame = ttk.Frame(main_frame)
        body_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        body_frame.columnconfigure(0, weight=2)
        body_frame.columnconfigure(1, weight=1)
        body_frame.columnconfigure(2, weight=1)
        body_frame.rowconfigure(0, weight=1)
        
        self.criar_mapa_tunel(body_frame)
        self.criar_painel_status(body_frame)
        self.criar_painel_vitima(body_frame)
        self.criar_console_mensagens(main_frame)
        
    def criar_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        ttk.Label(title_frame, text="🤖", font=('Arial', 24)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(title_frame, text="CENTRAL ROBOSOCO 5001", font=('Arial', 16, 'bold'), foreground='#007fff').pack(side=tk.LEFT)
        
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        ttk.Label(status_frame, text="Status:", font=('Arial', 9)).pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.status_geral, font=('Arial', 9, 'bold'), foreground='green').pack(side=tk.LEFT, padx=(5, 15))
        
        self.botao_relatorio = ttk.Button(status_frame, text="Gerar Relatório Final", command=self.abrir_janela_relatorio, state=tk.DISABLED)
        self.botao_relatorio.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(status_frame, text="Última atualização:", font=('Arial', 9)).pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.ultima_atualizacao, font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(5, 0))
        
    def criar_mapa_tunel(self, parent):
        map_frame = ttk.LabelFrame(parent, text="MAPEAMENTO DO TÚNEL", padding=10)
        map_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='#0a1929')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#0c1a2a')
        
        self.ax.set_xlim(0, 200)
        self.ax.set_ylim(0, 10)
        self.ax.set_xlabel('Distância (m)', color='white')
        self.ax.set_ylabel('Largura (m)', color='white')
        self.ax.set_title('Trajetória do Robô', color='white', pad=20)
        self.ax.grid(True, alpha=0.3)
        self.ax.tick_params(colors='white')
        
        self.robo_marker, = self.ax.plot([], [], 'o', color='#007fff', markersize=15, label='Robô')
        self.caminho_line, = self.ax.plot([], [], '.-', color='#00ff88', alpha=0.7, linewidth=2, label='Trajetória')
        self.vitimas_marker, = self.ax.plot([], [], 'X', color='red', markersize=12, label='Vítimas')
        
        self.ax.legend(facecolor='#132f4c', labelcolor='white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, map_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect('button_press_event', self.on_map_click)
        
    def on_map_click(self, event):
        if event.xdata and event.ydata:
            for vitima in self.central.cenario.objetos:
                distancia = ((event.xdata - vitima.x) ** 2 + (event.ydata - vitima.y) ** 2) ** 0.5
                if distancia < 3:
                    self.central.selecionar_vitima(vitima)
                    break
        
    def criar_painel_status(self, parent):
        status_frame = ttk.LabelFrame(parent, text="STATUS DA MISSÃO", padding=10)
        status_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        
        # Status do Robô
        info_frame = ttk.LabelFrame(status_frame, text="STATUS DO ROBÔ", padding=5)
        info_frame.pack(fill=tk.X, pady=5, expand=False)
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X, padx=5, pady=5)
        
        status_info = [
            ("Posição:", self.pos_var),
            ("Bateria:", self.bat_var),
            ("Status:", self.status_var),
            ("Temperatura:", self.temp_var),
            ("Kits Restantes:", self.kits_var)
        ]
                  
        for i, (texto, var) in enumerate(status_info):
            ttk.Label(info_grid, text=texto, font=('Arial', 9)).grid(row=i, column=0, sticky='w', pady=2)
            ttk.Label(info_grid, textvariable=var, font=('Arial', 9, 'bold')).grid(row=i, column=1, sticky='w', pady=2, padx=(10, 0))
        
        # Barra de bateria
        self.bateria_bar = ttk.Progressbar(info_grid, orient='horizontal', length=150, mode='determinate')
        self.bateria_bar.grid(row=1, column=2, sticky='w', padx=(10, 0))
        self.bateria_bar['value'] = 100
            
        # Alertas
        alertas_frame = ttk.LabelFrame(status_frame, text="ALERTAS ATIVOS", padding=5)
        alertas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.alertas_text = scrolledtext.ScrolledText(alertas_frame, height=8, bg='#0c1a2a', fg='white', font=('Consolas', 9))
        self.alertas_text.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        self.alertas_text.insert(tk.END, "Aguardando início da missão...\n")
        self.alertas_text.config(state=tk.DISABLED)
        
        ttk.Separator(status_frame, orient='horizontal').pack(fill=tk.X, pady=(5, 10))
        
        # Estatísticas
        stats_frame = ttk.LabelFrame(status_frame, text="ESTATÍSTICAS", padding=5)
        stats_frame.pack(fill=tk.X, pady=5, expand=False)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        stats_info = [
            ("Vítimas Detectadas:", self.vitimas_var),
            ("Fotos Registradas:", self.fotos_var),
            ("Kits Utilizados:", self.kits_used_var),
            ("Distância Percorrida:", self.distancia_var)
        ]

        for i, (texto, var) in enumerate(stats_info):
            ttk.Label(stats_grid, text=texto, font=('Arial', 9)).grid(row=i, column=0, sticky='w', pady=1)
            ttk.Label(stats_grid, textvariable=var, font=('Arial', 9, 'bold')).grid(row=i, column=1, sticky='w', pady=1, padx=(10, 0))

    def criar_painel_vitima(self, parent):
        vitima_frame = ttk.LabelFrame(parent, text="DETALHES DA VÍTIMA", padding=10)
        vitima_frame.grid(row=0, column=2, sticky="nsew")
        
        self.vitima_vazia_frame = ttk.Frame(vitima_frame)
        self.vitima_vazia_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.vitima_vazia_frame, text="🔍", font=('Arial', 48), foreground='#666666').pack(expand=True, pady=20)
        ttk.Label(self.vitima_vazia_frame, text="Nenhuma Vítima Selecionada", font=('Arial', 12, 'bold'), foreground='#666666').pack()
        
        self.vitima_detalhes_frame = ttk.Frame(vitima_frame)
        vitima_frame.rowconfigure(0, weight=1)
        
        self.vitima_foto_label = ttk.Label(self.vitima_detalhes_frame)
        self.vitima_foto_label.pack(pady=10)
        
        self.vitima_id_label = ttk.Label(self.vitima_detalhes_frame, font=('Arial', 14, 'bold'))
        self.vitima_id_label.pack()
        
        info_grid = ttk.Frame(self.vitima_detalhes_frame)
        info_grid.pack(fill=tk.X, pady=15, padx=20)
        
        ttk.Label(info_grid, text="Gravidade:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=3)
        self.vitima_gravidade_label = ttk.Label(info_grid, font=('Arial', 10))
        self.vitima_gravidade_label.grid(row=0, column=1, sticky='w', pady=3, padx=(10, 0))
        
        ttk.Label(info_grid, text="Estado:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=3)
        self.vitima_estado_label = ttk.Label(info_grid, font=('Arial', 10))
        self.vitima_estado_label.grid(row=1, column=1, sticky='w', pady=3, padx=(10, 0))
        
        ttk.Label(info_grid, text="Posição:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=3)
        self.vitima_posicao_label = ttk.Label(info_grid, font=('Arial', 10))
        self.vitima_posicao_label.grid(row=2, column=1, sticky='w', pady=3, padx=(10, 0))
        
        ttk.Label(info_grid, text="Registro de Campo:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=3)
        self.vitima_foto_status = ttk.Label(info_grid, font=('Arial', 9))
        self.vitima_foto_status.grid(row=3, column=1, sticky='w', pady=3, padx=(5, 0))
        
        ttk.Label(info_grid, text="Kit:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=3)
        self.vitima_kit_status = ttk.Label(info_grid, font=('Arial', 9))
        self.vitima_kit_status.grid(row=4, column=1, sticky='w', pady=3, padx=(10, 0))

    def mostrar_detalhes_vitima(self, vitima):
        self.vitima_vazia_frame.pack_forget()
        self.vitima_detalhes_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            image = Image.open(io.BytesIO(vitima.foto_data))
            image = image.resize((220, 220), Image.Resampling.LANCZOS)
            self.vitima_photo = ImageTk.PhotoImage(image)
            self.vitima_foto_label.configure(image=self.vitima_photo)
        except Exception as e:
            print(f"Erro ao exibir imagem: {e}")
            self.vitima_foto_label.configure(image='', text="🩺", font=('Arial', 48))
        
        self.vitima_id_label.configure(text=f"Vítima {vitima.id}")
        self.vitima_posicao_label.configure(text=f"{vitima.x}m")
        
        cores_gravidade = {"Leve": "#4CAF50", "Moderado": "#FF9800", "Grave": "#F44336", "Crítico": "#8B0000"}
        cor_grav = cores_gravidade.get(vitima.gravidade, "white")
        self.vitima_gravidade_label.configure(text=vitima.gravidade, foreground=cor_grav)
        self.vitima_estado_label.configure(text=vitima.estado)
        
        if vitima.foto_tirada:
            self.vitima_foto_status.configure(text="✅ Registrada", foreground="#4CAF50")
        else:
            self.vitima_foto_status.configure(text="⚠️ Aguardando Robô", foreground="#FF9800")
        
        if vitima.kit_aplicado:
            self.vitima_kit_status.configure(text="✅ Aplicado", foreground="#4CAF50")
        elif vitima.necessita_kit():
            self.vitima_kit_status.configure(text="⚠️ Necessário", foreground="#FF9800")
        else:
            self.vitima_kit_status.configure(text="ℹ️ Estável", foreground="#2196F3")

    def criar_console_mensagens(self, parent):
        console_frame = ttk.LabelFrame(parent, text="LOG DA MISSÃO", padding=10)
        console_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.console_text = scrolledtext.ScrolledText(console_frame, height=6, bg='#0c1a2a', fg='white', font=('Consolas', 9))
        self.console_text.pack(fill=tk.BOTH, expand=True)
        
        self.console_text.tag_configure("INFO", foreground="#FFFFFF")
        self.console_text.tag_configure("ALERTA", foreground="#FF9800")
        self.console_text.tag_configure("SUCESSO", foreground="#4CAF50")
        self.console_text.tag_configure("PERIGO", foreground="#F44336")
        
        self.adicionar_mensagem_console("Sistema", "Central inicializada - Missão de Resgate", "INFO")

    def adicionar_mensagem_console(self, fonte, mensagem, tipo="INFO"):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, f"[{timestamp}] {fonte}: {mensagem}\n", tipo)
        self.console_text.config(state=tk.DISABLED)
        self.console_text.see(tk.END)
        
    def adicionar_alerta(self, tipo, mensagem):
        self.alertas_text.config(state=tk.NORMAL)
        alerta_config = {"PERIGO": ("🚨", "#F44336"), "SUCESSO": ("✅", "#4CAF50"), "ALERTA": ("⚠️", "#FF9800")}
        icon, cor = alerta_config.get(tipo, ("ℹ️", "#2196F3"))
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.alertas_text.insert(tk.END, f"[{timestamp}] {icon} {mensagem}\n", tipo)
        self.alertas_text.see(tk.END)
        self.alertas_text.config(state=tk.DISABLED)
        self.alertas_text.tag_configure(tipo, foreground=cor)

    def habilitar_botao_relatorio(self):
        """Habilita o botão de gerar relatório."""
        self.botao_relatorio.config(state=tk.NORMAL)

    def abrir_janela_relatorio(self):
        """Cria e exibe a janela com o relatório final da missão."""
        relatorio_texto = self.central.gerar_relatorio_final()
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Relatório Final da Missão")
        report_window.geometry("600x700")
        report_window.configure(bg='#0a1929')
        
        # Frame para os botões na parte inferior
        button_frame = ttk.Frame(report_window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(5, 10))

        # Botão para salvar o relatório
        save_button = ttk.Button(button_frame, text="Salvar Relatório em .txt", command=lambda: self.salvar_relatorio(relatorio_texto))
        save_button.pack(side=tk.RIGHT)

        # Área de texto para exibir o relatório
        text_area = scrolledtext.ScrolledText(report_window, wrap=tk.WORD, bg='#0c1a2a', fg='white', font=('Consolas', 10))
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(10, 0))
        text_area.insert(tk.INSERT, relatorio_texto)
        text_area.config(state=tk.DISABLED)

    def salvar_relatorio(self, relatorio_texto):
        """Salva o conteúdo do relatório em um arquivo de texto."""
        try:
            # Cria um nome de arquivo único com data e hora
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nome_arquivo = f"relatorio_missao_{timestamp}.txt"
            caminho_arquivo = os.path.join(DIRETORIO_DO_SCRIPT, nome_arquivo)

            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(relatorio_texto)
            
            messagebox.showinfo("Sucesso", f"Relatório salvo com sucesso em:\n{caminho_arquivo}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o relatório.\nErro: {e}")

    def atualizar_interface_simulacao(self, dados):
        self.atualizar_status_robo(dados)
        self.atualizar_mapa(dados['pos_x'], dados['pos_y'])
        
        vitimas_count = len(self.central.vitimas_detectadas)
        fotos_count = len(self.central.robo.memoria_fotos)
        kits_used = 3 - self.central.robo.kits_primeiros_socorros
        
        self.vitimas_var.set(str(vitimas_count))
        self.fotos_var.set(str(fotos_count))
        self.kits_used_var.set(str(kits_used))
        self.distancia_var.set(f"{dados['pos_x']:.1f} m")
        
        self.ultima_atualizacao.set(datetime.datetime.now().strftime('%H:%M:%S'))
        self.status_var.set(dados['status_robo'])

    def atualizar_mapa(self, x, y):
        self.historico_posicoes.append((x, y))
        if len(self.historico_posicoes) > 50: 
            self.historico_posicoes.pop(0)
            
        self.robo_marker.set_data([x], [y])
        
        if self.historico_posicoes:
            traj_x, traj_y = zip(*self.historico_posicoes)
            self.caminho_line.set_data(traj_x, traj_y)
        
        vitimas_x = [v.x for v in self.central.cenario.objetos]
        vitimas_y = [v.y for v in self.central.cenario.objetos]
        self.vitimas_marker.set_data(vitimas_x, vitimas_y)
        
        self.canvas.draw_idle()

    def atualizar_status_robo(self, dados):
        self.pos_var.set(f"{dados['pos_x']:.1f} m")
        self.bat_var.set(f"{dados['bateria']:.1f}%")
        self.temp_var.set(f"{dados['sensores']['temp']}°C")
        self.kits_var.set(str(self.central.robo.kits_primeiros_socorros))
        self.bateria_bar['value'] = dados['bateria']

    def integrar_com_central(self, robo, cenario):
        self.central.robo = robo
        self.central.cenario = cenario
        self.central.gui = self

    def iniciar_interface(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#0a1929', foreground='white')
        style.configure('TFrame', background='#0a1929')
        style.configure('TLabel', background='#0a1929', foreground='white')
        style.configure('TLabelframe', background='#132f4c', foreground='white')
        style.configure('TLabelframe.Label', background='#132f4c', foreground='white')
        style.configure('TButton', background='#007fff', foreground='white', font=('Arial', 9, 'bold'))
        
        if not verificar_pasta_imagens():
            self.root.destroy() # Fecha a aplicação se a verificação falhar
            return
        self.root.mainloop()

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("🤖 Inicializando Central RoboSoco...")
    
    cenario_tunel = Cenario()
    central_obj = CentralDeControle()
    robo_obj = Robo(central_controle=central_obj)

    gui = CentralControleGUI(central_obj)
    gui.integrar_com_central(robo_obj, cenario_tunel)
    
    def iniciar_simulacao():
        time.sleep(2)
        central_obj.iniciar_missao(robo_obj, cenario_tunel)
        
    threading.Thread(target=iniciar_simulacao, daemon=True).start()
    
    print("✅ Sistema pronto! Iniciando interface...")
    gui.iniciar_interface()