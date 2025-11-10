try:
    import pandas as pd
except ImportError:
    print("Error importing pandas. Please install it using: pip install pandas")
    exit(1)
import numpy as np
import random
import os
from time import sleep
import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# --- 1. GERAÇÃO DE DADOS DE CENÁRIO (AGORA COM OS 3 CENÁRIOS REAIS) ---
def gerar_dados_de_cenario(cenario='incendio_galpao', pontos_medidos=2000, grid_largura=70):
    """
    Gera um DataFrame com dados 3D, ambientais e logísticos 
    DE FORMA CORRELACIONADA, baseado em um dos 3 cenários reais.
    """
    print(f"\n[CENÁRIO] Gerando mundo para: '{cenario}' com {pontos_medidos} pontos...")

    # --- 1.1 Configurações Padrão ---
    posicao_x = np.arange(pontos_medidos) % grid_largura
    posicao_y = np.arange(pontos_medidos) // grid_largura
    grid_altura = pontos_medidos // grid_largura
    
    vitimas_locs = []
    risco_locs = []
    zonas_termicas = []
    
    # Valores base dos gases
    co2_base = 415.0 # Atmosférico
    co_base = 0.0     # Monóxido de Carbono (normalmente zero)
    metano_base = 0.0 # Metano (normalmente zero)
    
    gps_funciona = True
    bateria_gasto_coef = 1.0 # Coeficiente de gasto de bateria

    # --- 1.2 Configurações Específicas do Cenário ---
    if cenario == 'incendio_galpao':
        # Chão plano, fumaça tóxica, focos de calor
        print("[CENÁRIO] Config: Galpão plano, fumaça (CO), focos de calor, risco de re-ignição.")
        co2_base = 600.0 # Ar já viciado pela fumaça
        co_base = 100.0  # Fumaça gera Monóxido de Carbono
        
        
        num_vitimas = random.randint(1, 3) # Sorteia de 1 a 3 vítimas!
        print(f"[CENÁRIO] Sorteando {num_vitimas} vítima(s) aleatoriamente no mapa...")
        
        for _ in range(num_vitimas):
            rand_x = random.randint(5, grid_largura - 5) # Sorteia X (evitando as bordas)
            rand_y = random.randint(5, grid_altura - 5) # Sorteia Y (evitando as bordas)
            rand_sinal = random.randint(4500, 6000)     # Sorteia a força do sinal
            
            vitimas_locs.append(
                {'x': rand_x, 'y': rand_y, 'sinal_max': rand_sinal, 'tipo': 'bombeiro_perdido'}
            )


        zonas_termicas = [
            {'x': 35, 'y': 45, 'temp_offset': 80, 'raio': 7}, # Foco de re-ignição
            {'x': 5, 'y': 50, 'temp_offset': 60, 'raio': 5}   # Escombros quentes
        ]
        risco_locs = zonas_termicas # Risco é o calor
        
    elif cenario == 'tunel_metro':
        # Plano, longo, sem GPS, fumaça
        print("[CENÁRIO] Config: Túnel longo, SEM GPS, fumaça (CO), risco de pânico.")
        gps_funciona = False # GPS não funciona em túnel
        co2_base = 800.0     # Ar confinado
        co_base = 200.0      # Fumaça de curto-circuito
        bateria_gasto_coef = 1.5 # Missão longa, gasto maior
        # Sorteia 2-4 vítimas ao longo do túnel (y pequeno)
        vitimas_locs = []
        num_vitimas_tunel = random.randint(2, 4)
        for _ in range(num_vitimas_tunel):
            rx = random.randint(5, max(6, grid_largura - 6))
            ry = random.randint(2, max(3, min(10, grid_altura - 1)))
            sinal = random.randint(4000, 8000)
            vitimas_locs.append({'x': rx, 'y': ry, 'sinal_max': sinal, 'tipo': 'passageiro'})
        zonas_termicas = [
            {'x': 5, 'y': 5, 'temp_offset': 50, 'raio': 10}, # Ponto do curto-circuito
        ]
        risco_locs = zonas_termicas
        
   
    elif cenario == 'vazamento_quimico':
        # Plano, ar tóxico, risco de explosão
        print("[CENÁRIO] Config: Fábrica plana, vazamento de gás (Metano), risco de explosão.")
        metano_base = 200.0 # Nível de fundo
        bateria_gasto_coef = 1.2
        # Pode haver 0-2 vítimas aleatórias espalhadas pela planta
        vitimas_locs = []
        num_vitimas_quim = random.randint(0, 2)
        for _ in range(num_vitimas_quim):
            rx = random.randint(5, max(6, grid_largura - 6))
            ry = random.randint(5, max(6, grid_altura - 6))
            sinal = random.randint(5000, 7000)
            vitimas_locs.append({'x': rx, 'y': ry, 'sinal_max': sinal, 'tipo': 'operador_desmaiado'})
        # O "Risco" é a nuvem de metano
   
        risco_locs = [
            {'x': 60, 'y': 40, 'risco_max': 4, 'raio': 20, 'sinal_gas_max': 50000} # Fonte do vazamento de metano
        ]
        zonas_termicas = [
            {'x': 60, 'y': 40, 'temp_offset': -10, 'raio': 8} # Gás vazando pode ser frio
        ]

    # --- 1.3 Simulação de Caminhada do Robô ---
    current_lat, current_lon = 40.7128, -74.0060
    current_z = 2.0 # Começa no nível do solo
    current_roll = 0.0

    lats, lons, zs, rolls = [], [], [], []
    
    timestamp = pd.to_datetime(pd.Series(range(pontos_medidos), name='Timestamp'), unit='s')

    for i in range(pontos_medidos):
        delta_z = np.random.normal(0, 0.05)
        delta_roll = np.random.normal(0, 1) # Robô de rodas, pouca variação de roll

        # GPS só funciona se o cenário permitir
        if gps_funciona:
            delta_lat = np.random.normal(0, 0.00001)
            delta_lon = np.random.normal(0, 0.00001)
            current_lat += delta_lat
            current_lon += delta_lon
        
        current_z = np.clip(current_z + delta_z, 0.1, 5.0) # Assume altura de 0 a 5m
        current_roll = np.clip(current_roll + delta_roll, 0, 15) # Terreno plano, max 15 graus

        lats.append(current_lat)
        lons.append(current_lon)
        zs.append(current_z)
        rolls.append(current_roll)

    latitude = np.array(lats).round(6)
    longitude = np.array(lons).round(6)
    profundidade_z = np.array(zs).round(1) # Na verdade é "Altura"
    angulacao_roll = np.array(rolls).round(1)
    
    # --- 1.4 Simulação de Sensores (Plumes e Ruído) ---
    df_sensores = pd.DataFrame({
        'Posicao_X': posicao_x, 'Posicao_Y': posicao_y, 
        'Profundidade_Z_m': profundidade_z, 'Angulacao_Roll_Graus': angulacao_roll
    })
    
    # A. Vítimas (CO2)
    df_sensores['CO2_Sinal_Vitimas'] = 0.0
    df_sensores['Vitima_Presente_GT'] = 0 
    for vitima in vitimas_locs:
        dist = np.sqrt((df_sensores['Posicao_X'] - vitima['x'])**2 + (df_sensores['Posicao_Y'] - vitima['y'])**2)
        sinal_plume = vitima['sinal_max'] / (dist**2 + 5)
        df_sensores['CO2_Sinal_Vitimas'] += sinal_plume
        df_sensores.loc[dist < 2.5, 'Vitima_Presente_GT'] = 1 
        
    ruido_co2 = np.random.normal(0, 20, pontos_medidos)
    co2_final = (co2_base + df_sensores['CO2_Sinal_Vitimas'] + ruido_co2).astype(int)

    # B. Temperatura (Base + Zonas Térmicas)
    temp_base = 25 + (profundidade_z * 0.1) # Pouca variação
    temp_zonas = np.zeros(pontos_medidos)
    for zona in zonas_termicas:
        dist = np.sqrt((df_sensores['Posicao_X'] - zona['x'])**2 + (df_sensores['Posicao_Y'] - zona['y'])**2)
        offset = np.where(dist < zona['raio'], zona['temp_offset'] * (1 - dist / zona['raio']), 0)
        temp_zonas += offset
    ruido_temp = np.random.normal(0, 0.5, pontos_medidos)
    temperatura = (temp_base + temp_zonas + ruido_temp).round(1)
    
    # C. Risco, CO (Monóxido) e Metano
    df_sensores['Risco_Estrutural_Raw'] = 0.0
    df_sensores['CO_Plume'] = 0.0
    df_sensores['Metano_Plume'] = 0.0
    
    for zona in risco_locs:
        dist = np.sqrt((df_sensores['Posicao_X'] - zona['x'])**2 + (df_sensores['Posicao_Y'] - zona['y'])**2)
        
        # Risco Estrutural (pode ser calor ou gás)
        if 'risco_max' in zona:
            risco = np.where(dist < zona['raio'], zona['risco_max'] * (1 - dist / zona['raio']), 0)
            df_sensores['Risco_Estrutural_Raw'] = np.maximum(df_sensores['Risco_Estrutural_Raw'], risco)
        
        # Plume de CO (associado a 'zonas_termicas' em 'incendio' e 'tunel')
        if cenario != 'vazamento_quimico' and 'temp_offset' in zona and zona['temp_offset'] > 40:
             sinal_co = (zona['temp_offset'] * 10) / (dist**2 + 5) # CO proporcional ao calor
             df_sensores['CO_Plume'] += sinal_co

        # Plume de Metano (associado a 'risco_locs' em 'vazamento_quimico')
        if cenario == 'vazamento_quimico' and 'sinal_gas_max' in zona:
            sinal_metano = zona['sinal_gas_max'] / (dist**2 + 5)
            df_sensores['Metano_Plume'] += sinal_metano
            
    risco_estrutura = np.clip(df_sensores['Risco_Estrutural_Raw'], 0, 4).round().astype(int)
    co_final = (co_base + df_sensores['CO_Plume'] + np.random.normal(0, 5, pontos_medidos)).astype(int)
    metano_final = (metano_base + df_sensores['Metano_Plume'] + np.random.normal(0, 10, pontos_medidos)).astype(int)


    # --- 1.5 Logística (Bateria com gasto dinâmico) ---
    bateria_gasto_base = (np.arange(pontos_medidos) / pontos_medidos * 40 * bateria_gasto_coef)
    bateria_gasto_extra = (df_sensores['Angulacao_Roll_Graus'] * 0.1) + (df_sensores['Risco_Estrutural_Raw'] * 0.2)
    bateria_robo_perc = 100 - np.clip(bateria_gasto_base + bateria_gasto_extra, None, 99)

    # --- 1.6 Montagem Final do DataFrame ---
    df = pd.DataFrame({
        'Timestamp': timestamp,
        'Latitude': latitude,
        'Longitude': longitude,
        'Posicao_X': posicao_x,
        'Posicao_Y': posicao_y,
        'Profundidade_Z_m': profundidade_z,
        'Angulacao_Roll_Graus': angulacao_roll,
        'Temp_C': temperatura,
        'CO2_ppm': co2_final,
        'CO_ppm': co_final,           # NOVO SENSOR
        'Metano_ppm': metano_final,  # NOVO SENSOR
        'Risco_Estrutural': risco_estrutura,
        'Bateria_Robo_Perc': bateria_robo_perc.round(1),
        'Vitima_Presente_GT': df_sensores['Vitima_Presente_GT']
    })

    df['Tendencia_Temp_C'] = df['Temp_C'].diff().fillna(0).round(1) 
    
    print("[CENÁRIO] Geração de mundo concluída.")
    return df

# --- 2. TREINAMENTO DA IA (AGORA COM ML DE VERDADE) ---
def treinar_modelo_ia(cenario_treino):
    """
    Treina um modelo de IA (Logistic Regression) para detectar vítimas
    usando dados simulados do cenário escolhido.
    """
    print(f"\n[IA] Treinando modelo de IA para o cenário: '{cenario_treino}'...")
    print("[IA] Gerando 10.000 pontos de dados para treino...")
    
    # 1. Gerar um GRANDE dataset de treino
    df_treino = gerar_dados_de_cenario(cenario=cenario_treino, pontos_medidos=10000)
    
    # 2. Definir 'features' (dados dos sensores) e 'target' (o gabarito)
    #    AGORA INCLUINDO OS NOVOS SENSORES!
    features = [
        'CO2_ppm', 
        'Temp_C', 
        'Tendencia_Temp_C', 
        'Profundidade_Z_m',
        'CO_ppm',
        'Metano_ppm'
    ]
    target = 'Vitima_Presente_GT' # O gabarito que a simulação criou!

    X = df_treino[features]
    y = df_treino[target]

    # 3. Treinar o modelo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    # Usamos um 'pipeline' que primeiro normaliza os dados (StandardScaler)
    # e depois aplica a Regressão Logística. Isso é essencial!
    modelo_ia = make_pipeline(StandardScaler(), LogisticRegression(class_weight='balanced'))
    modelo_ia.fit(X_train, y_train)
    
    # 4. Checar a precisão (só pra gente saber)
    preds = modelo_ia.predict(X_test)
    print("\n[IA] Relatório de Classificação do Modelo (dados de teste):")
    print(classification_report(y_test, preds))
    print(f"[IA] Acurácia do Modelo de IA: {accuracy_score(y_test, preds) * 100:.2f}%")
    print("[IA] Modelo treinado e pronto!")
    
    return modelo_ia, features # Retorna o modelo (pipe) e a lista de features

# --- 3. PROCESSAMENTO E FUSÃO (AGORA OTIMIZADO E COM IA) ---
def fusao_e_priorizacao_inteligente(modelo_ia, features_list, ponto_atual, ponto_anterior=None):
    """
    Aplica IA e regras de fusão para determinar a prioridade de UM ÚNICO PONTO.
    Esta função é O(n), muito rápida.
    """
    
    # Copia o dicionário para não mexer no original
    ponto_processado = ponto_atual.copy()

    # --- Cálculo de Tendência (baseado no ponto anterior) ---
    if ponto_anterior is not None:
        ponto_processado['Tendencia_Temp_C'] = round(ponto_processado['Temp_C'] - ponto_anterior['Temp_C'], 1)
    else:
        ponto_processado['Tendencia_Temp_C'] = 0.0

    # --- Passo A: Previsão de Risco (Usando novos sensores) ---
    ponto_processado['Risco_Previsto_Futuro'] = ponto_processado['Risco_Estrutural']
    
    # Risco de Gás/Fumaça é mais importante
    if ponto_processado['CO_ppm'] >= 500: # Nível perigoso de Monóxido
        ponto_processado['Risco_Previsto_Futuro'] = 4
    elif ponto_processado['Metano_ppm'] >= 10000: # 1% de Metano (alto)
        ponto_processado['Risco_Previsto_Futuro'] = 4
    elif (ponto_processado['Risco_Estrutural'] >= 2) and (ponto_processado['Tendencia_Temp_C'] > 4.0):
        ponto_processado['Risco_Previsto_Futuro'] = 4
    
    # --- Passo B: Cálculo de Custos de Rota (Logística) ---
    ponto_processado['Custo_Rota'] = int(
        (ponto_processado['Profundidade_Z_m'] * 10) + 
        (ponto_processado['Risco_Estrutural'] * 50) + 
        (ponto_processado['Angulacao_Roll_Graus'] * 2)
    )

    # --- Passo C: Detecção de Vítimas (USANDO A IA) ---
    
    # 1. Prepara os dados do ponto atual no formato que o modelo espera
    #    O pipeline foi treinado com nomes de colunas; passamos um DataFrame com esses nomes
    dados_para_ia_df = pd.DataFrame([{feature: ponto_processado[feature] for feature in features_list}])

    # 2. Faz a predição usando o DataFrame (preserva os nomes de colunas)
    predicao = modelo_ia.predict(dados_para_ia_df)

    # 3. Pega a PROBABILIDADE (confiança) da IA
    probabilidade_vitima = modelo_ia.predict_proba(dados_para_ia_df)[0][1] # Probabilidade de ser classe "1" (Vítima)
    
    ponto_processado['Vitima_Detectada'] = bool(predicao[0])
    ponto_processado['Vitima_Confianca_Perc'] = round(probabilidade_vitima * 100, 1)

    # --- Passo D: Fusão Final (Score baseado na CONFIANÇA da IA) ---
    
    # 1. CRIA os scores base (Vitima e Risco) PRIMEIRO!
    ponto_processado['Score_Vitima'] = ponto_processado['Vitima_Confianca_Perc'] * 2.0
    ponto_processado['Score_Risco_Estrutural'] = ponto_processado['Risco_Previsto_Futuro'] * 50

    # 2. Agora sim, CALCULA o Score Bruto (usando os scores de cima)
    score_bruto = (
        (ponto_processado['Score_Vitima'] * 0.70) + 
        (ponto_processado['Score_Risco_Estrutural'] * 0.20) +
        (ponto_processado['Angulacao_Roll_Graus'] * 0.05) +
        (np.clip(ponto_processado['Tendencia_Temp_C'], None, 5) * 0.05)
    )

    # 3. Adiciona o "Ruído de Atividade" (pra nunca ficar 0)
    ruido_de_atividade = random.randint(1, 200) 

    # 4. Soma o ruído e converte pra int
    ponto_processado['Prioridade_Resgate'] = int(score_bruto + ruido_de_atividade)
    
    # --- Passo E: Decisão Logística (Comandos com novos riscos) ---
    ponto_processado['Comando_Logistico'] = 'CONTINUAR EXPLORACAO'
    
    # 1. Risco de Explosão (Prioridade Máxima)
    if ponto_processado['Metano_ppm'] >= 25000: # 2.5% LEL (Limite Inferior de Explosividade)
        ponto_processado['Comando_Logistico'] = '!!! EVACUAR IMEDIATAMENTE (RISCO DE EXPLOSÃO) !!!'
    # 2. Risco de Asfixia (CO)
    elif ponto_processado['CO_ppm'] >= 800:
        ponto_processado['Comando_Logistico'] = 'RETIRADA (NÍVEL DE CO PERIGOSO PARA O ROBÔ)'
    # 3. Bateria
    elif ponto_processado['Bateria_Robo_Perc'] < 30:
        ponto_processado['Comando_Logistico'] = 'RETORNAR A BASE (BAIXA BATERIA)'
    # 4. Detecção de Vítima (pela IA)
    elif ponto_processado['Vitima_Detectada'] == True and ponto_processado['Vitima_Confianca_Perc'] > 70:
        ponto_processado['Comando_Logistico'] = 'INICIAR RESGATE (ALTA CONFIANÇA DA IA)'
    # 5. Risco Estrutural (sem vítima)
    elif (ponto_processado['Comando_Logistico'] == 'CONTINUAR EXPLORACAO') and (ponto_processado['Risco_Previsto_Futuro'] == 4):
        ponto_processado['Comando_Logistico'] = 'RETIRADA (RISCO ESTRUTURAL PREVISTO)'
           
    return ponto_processado

# --- 4. EXECUÇÃO PRINCIPAL (COM TUDO INTEGRADO) ---
if __name__ == "__main__":
    
    # --- 4.1 Configuração da Missão ---
    print("=======================================================")
    print(" 🤖 BEM-VINDO AO SIMULADOR DE MISSÃO ROBOSOCO 3000 🤖")
    print("=======================================================")
    print("Escolha o cenário do desastre para a simulação:")
    print("  1: Incêndio em Galpão Industrial (Foco em Fumaça/Calor/CO)")
    print("  2: Incidente em Túnel de Metrô (Foco em Fumaça/Sem GPS)")
    print("  3: Vazamento em Planta Química (Foco em Gás/Risco de Explosão)")
    
    cenario_map = {'1': 'incendio_galpao', '2': 'tunel_metro', '3': 'vazamento_quimico'}
    escolha = input("Digite o número do cenário (1, 2 ou 3): ")
    while escolha not in cenario_map:
        print("Escolha inválida. Por favor, digite 1, 2 ou 3.")
        escolha = input("Digite o número do cenário (1, 2 ou 3): ")
    cenario_escolhido = cenario_map[escolha]
    
    # Suporte opcional a seed para reprodutibilidade (variável de ambiente)
    seed_env = os.environ.get('ROBOSOCO_SEED')
    if seed_env is not None:
        try:
            seed_val = int(seed_env)
            print(f"[SEED] Usando seed fornecida em ROBOSOCO_SEED={seed_val}")
            random.seed(seed_val)
            np.random.seed(seed_val)
        except Exception:
            print("[SEED] Valor de ROBOSOCO_SEED inválido; ignorando.")

    pontos_totais = 500
    grid_largura_cenario = 50
    
    # --- 4.2 Treinamento da IA ---
    # Treina o modelo de IA especificamente para o cenário que vamos rodar
    modelo_ia, lista_features = treinar_modelo_ia(cenario_treino=cenario_escolhido)

    # --- 4.3 Geração do Mundo da Simulação ---
    dados_completos = gerar_dados_de_cenario(cenario=cenario_escolhido, 
                                             pontos_medidos=pontos_totais, 
                                             grid_largura=grid_largura_cenario) 
    
    print("\n=======================================================")
    print(f" 🛰️  INICIANDO MISSÃO: {cenario_escolhido.upper()} ")
    print("  Processamento Otimizado (O(n)) e Visualização Ativados ")
    print("=======================================================")

    # --- 4.4 Configuração da Visualização (Gráfico) ---
    plt.ion() # Ligar o MODO INTERATIVO
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Preparar listas para guardar o histórico do caminho
    mapa_x, mapa_y = [], []
    mapa_vitimas_x, mapa_vitimas_y = [], []
    
    # Definir os limites do mapa
    grid_altura = (pontos_totais // grid_largura_cenario) + 1
    ax.set_xlim(0, grid_largura_cenario) 
    ax.set_ylim(0, grid_altura)

    # --- 4.5 Loop de Simulação em Tempo Real ---
    historico_processado_lista = [] 
    ponto_anterior = None

    for i in range(pontos_totais):
        
        # 1. Pega o novo ponto como um DICIONÁRIO
        novo_ponto_dict = dados_completos.iloc[i].to_dict()

        try:
            # 2. Processa SÓ O PONTO NOVO! (Passando a IA)
            decisao_tempo_real = fusao_e_priorizacao_inteligente(modelo_ia, 
                                                                 lista_features,
                                                                 novo_ponto_dict, 
                                                                 ponto_anterior)
            
            historico_processado_lista.append(decisao_tempo_real)
            ponto_anterior = decisao_tempo_real.copy()

        except Exception as e:
            print(f"Erro de processamento no Ponto {i+1}: {e}")
            continue
            
        # 3. Status da Vítima (Baseado na IA)
        confianca_ia = decisao_tempo_real['Vitima_Confianca_Perc']
        status_vitima = f"🚨 VÍTIMA (IA: {confianca_ia:.0f}%)" if decisao_tempo_real['Vitima_Detectada'] else f"Nenhuma Vítima (IA: {confianca_ia:.0f}%)"
        
        # 4. Apresentação em Tela (Terminal)
        print("\n" + "-"*60)
        print(f"PONTO {i+1:04d}/{pontos_totais} | SCORE: {decisao_tempo_real['Prioridade_Resgate']:.0f} | Bateria: {decisao_tempo_real['Bateria_Robo_Perc']:.1f}%")
        print(f"  -> GPS: ({decisao_tempo_real['Latitude']:.6f}, {decisao_tempo_real['Longitude']:.6f}) | Local: (X:{decisao_tempo_real['Posicao_X']}, Y:{decisao_tempo_real['Posicao_Y']})")
        print(f"  -> AMBIENTE: Temp: {decisao_tempo_real['Temp_C']:.1f}°C | CO2: {decisao_tempo_real['CO2_ppm']:.0f} | CO: {decisao_tempo_real['CO_ppm']:.0f} | Metano: {decisao_tempo_real['Metano_ppm']:.0f}")
        print(f"  -> ROBÔ: Roll: {decisao_tempo_real['Angulacao_Roll_Graus']:.1f}° | Risco Previsto: {decisao_tempo_real['Risco_Previsto_Futuro']:.0f} | Custo Rota: {decisao_tempo_real['Custo_Rota']:.0f}")
        print(f"  -> STATUS IA: {status_vitima}")
        
        # Print de Alerta
        if decisao_tempo_real['Comando_Logistico'] != 'CONTINUAR EXPLORACAO':
             print(f"  -> 🔥 COMANDO: >>> {decisao_tempo_real['Comando_Logistico']} <<<")
        
        # 5. Atualização da Visualização (Gráfico)
        x_atual = decisao_tempo_real['Posicao_X']
        y_atual = decisao_tempo_real['Posicao_Y']
        mapa_x.append(x_atual)
        mapa_y.append(y_atual)

        ax.clear() # Limpa o mapa para redesenhar
        
        # Desenha o caminho percorrido (cinza)
        ax.plot(mapa_x, mapa_y, '.-', color='gray', alpha=0.5, label='Caminho Percorrido')
        
        # Desenha a posição ATUAL (azul)
        ax.plot(x_atual, y_atual, 'o', color='blue', markersize=10, label='Posição Atual Robô')

        # Se a IA detectar vítima com alta confiança, marca no mapa
        if decisao_tempo_real['Vitima_Detectada'] and decisao_tempo_real['Vitima_Confianca_Perc'] > 70:
            mapa_vitimas_x.append(x_atual)
            mapa_vitimas_y.append(y_atual)
            
        # Desenha TODAS as vítimas detectadas (vermelho)
        if mapa_vitimas_x:
            ax.plot(mapa_vitimas_x, mapa_vitimas_y, 'X', color='red', markersize=15, label='Vítima Detectada (IA)')
        
        # Re-setar os limites e legendas
        ax.set_xlim(0, grid_largura_cenario) 
        ax.set_ylim(0, grid_altura)
        ax.set_title(f"MAPA DA MISSÃO: {cenario_escolhido.upper()} (Ponto {i+1}) | Bateria: {decisao_tempo_real['Bateria_Robo_Perc']:.0f}%")
        ax.legend(loc='upper left')
        
        plt.pause(0.001) # Um 'sleep' gráfico muito rápido

    # --- 4.6 Fim da Missão ---
    plt.ioff() # Desliga o modo interativo
    print("\n=======================================================")
    print(" 🏁         MISSÃO ENCERRADA: ANÁLISE COMPLETA         🏁")
    print("=======================================================")
    
    # Converte a lista de resultados em um DataFrame final
    historico_processado_final = pd.DataFrame(historico_processado_lista)
    comandos_criticos = historico_processado_final[historico_processado_final['Comando_Logistico'] != 'CONTINUAR EXPLORACAO']
    
    print(f"Total de Pontos Processados: {len(historico_processado_final)}")
    print(f"Decisões Críticas (Resgate/Retorno/Risco): {len(comandos_criticos)}")
    
    # 7. EXPORTAÇÃO DOS DADOS PROCESSADOS
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    nome_arquivo = f"relatorio_missao_robosoco_{cenario_escolhido}_{timestamp_str}.csv"
    
    try:
        historico_processado_final.to_csv(nome_arquivo, index=False)
        print(f"\n✅ EXPORTAÇÃO CONCLUÍDA: Dados salvos em '{nome_arquivo}'")
    except Exception as e:
        print(f"\n❌ ERRO ao exportar para CSV: {e}")

    print("\nVisualização final do mapa da missão. Pode fechar a janela do gráfico.")
    plt.show() # Mostra o gráfico final e pausa o script até você fechar