import cmath
import math

# ==========================================
# 1. FUNÇÕES AUXILIARES
# ==========================================
def polar_to_rect(modulo, angulo_graus):
    return cmath.rect(modulo, math.radians(angulo_graus))

def rect_to_polar_str(numero_complexo):
    modulo, angulo_rad = cmath.polar(numero_complexo)
    angulo_graus = math.degrees(angulo_rad)
    return f"{modulo:.2f} < {angulo_graus:.2f}°"

def format_power_str(S_VA):
    P_kW = S_VA.real / 1000
    Q_kVAr = S_VA.imag / 1000
    S_kVA_mod = abs(S_VA) / 1000
    angulo = math.degrees(cmath.phase(S_VA))
    return f"{P_kW:>7.2f} kW + j {Q_kVAr:>7.2f} kVAr  |  {S_kVA_mod:>7.2f} < {angulo:>6.2f}° kVA"

# ==========================================
# 2. DEFINIÇÃO DOS PARÂMETROS DO SISTEMA
# ==========================================
fontes = {
    'F1': polar_to_rect(6350.0, 10.0), # Já está em VAN
    'F2': polar_to_rect(13800.0 / math.sqrt(3), 50.0 - 30.0), # VAB convertido para VAN
    'F3': polar_to_rect(6600.0, 15.0)  # Já está em VAN (A'')
}

linhas = {
    'L1': complex(0.375, 0.50), # Sem mútua
    'L2': complex(0.80, 1.40) - complex(0.0, 0.36) # Zp - Zm
}

cargas = {
    'C1': complex(18.0, 6.0),     
    'C2': complex(12.0, -4.0),    
    'C3': complex(20.0, 0.0) / 3.0,      # Delta convertido para Estrela Equivalente
    'C1//C1': complex(18.0, 6.0) / 2.0   # Duas cargas C1 idênticas em paralelo
}

FREQUENCIA = 60.0 # Hz

# ==========================================
# 3. MOTOR DE CÁLCULO
# ==========================================
def calcular_correntes(id_fonte, id_linha, id_carga):
    """Calcula os fasores de corrente na linha para um sistema equilibrado."""
    Van = fontes[id_fonte]
    Z_total = linhas[id_linha] + cargas[id_carga]
    Ia = Van / Z_total
    
    alfa = polar_to_rect(1.0, 120.0)
    
    if id_fonte == 'F2':
        Ib = Ia * alfa          # Sequência Negativa
        Ic = Ia * (alfa ** 2)
    else:
        Ib = Ia * (alfa ** 2)   # Sequência Positiva
        Ic = Ia * alfa
        
    print(f"--- CORRENTES DA LINHA ---")
    print(f"Ia: {rect_to_polar_str(Ia)} A")
    print(f"Ib: {rect_to_polar_str(Ib)} A")
    print(f"Ic: {rect_to_polar_str(Ic)} A\n")
    
    return Ia, Ib, Ic

def calcular_potencias(id_fonte, id_linha, id_carga, Ia):
    """Calcula as potências complexas (S = P + jQ) do circuito."""
    Van = fontes[id_fonte]
    Z_linha = linhas[id_linha]
    Z_carga = cargas[id_carga]
    
    # a) Potência Fornecida pela Fonte (S = V * I*)
    S_fonte_1f = Van * Ia.conjugate()
    S_fonte_3f = 3 * S_fonte_1f
    
    # b) Perdas Ôhmicas na Linha (S = Z * |I|^2)
    S_linha_1f = Z_linha * (abs(Ia)**2)
    S_linha_3f = 3 * S_linha_1f
    
    # c) Potência Consumida pela Carga (S = Z * |I|^2)
    S_carga_1f = Z_carga * (abs(Ia)**2)
    S_carga_3f = 3 * S_carga_1f
    
    print(f"--- POTÊNCIAS COMPLEXAS ---")
    print("a) FORNECIDA PELA FONTE:")
    print(f"   Por Fase (A,B,C) : {format_power_str(S_fonte_1f)}")
    print(f"   Total (Trifásica): {format_power_str(S_fonte_3f)}\n")
    
    print("b) PERDAS NA LINHA:")
    print(f"   Por Fase (A,B,C) : {format_power_str(S_linha_1f)}")
    print(f"   Total (Trifásica): {format_power_str(S_linha_3f)}\n")
    
    print("c) CONSUMIDA PELA CARGA:")
    print(f"   Por Fase (A,B,C) : {format_power_str(S_carga_1f)}")
    print(f"   Total (Trifásica): {format_power_str(S_carga_3f)}\n")
    
    # Verificação de balanço de energia (apenas para conferência do aluno)
    S_soma = S_linha_3f + S_carga_3f
    print(f"   [Check] Linha + Carga = {format_power_str(S_soma)}")
    
    return S_carga_1f, S_linha_3f

def calcular_correcao_fp(id_carga, Ia, S_carga_1f):
    """Executa o raciocínio de correção de fator de potência para FP = 1"""

    Q_carga_fase = S_carga_1f.imag
    
    print("--- CORREÇÃO DO FATOR DE POTÊNCIA (FP = 1) ---")
    
    # Trava de segurança para cargas não-indutivas
    if Q_carga_fase < 1e-5 and Q_carga_fase > -1e-5:
        print("A carga é puramente resistiva. O FP já é 1! Nenhum capacitor é necessário.\n")
        return 0.0, 0.0
    elif Q_carga_fase < -1e-5:
        print(f"A carga é CAPACITIVA (gera {abs(Q_carga_fase)/1000:.2f} kVAr).")
        print("Para corrigir o FP para 1, você precisaria instalar um INDUTOR, não um capacitor!\n")
        return 0.0, 0.0

    Z_carga = cargas[id_carga]
    V_carga_fase = Ia * Z_carga
    V_carga_mod = abs(V_carga_fase)
    
    Xc = (V_carga_mod ** 2) / Q_carga_fase
    C = 1.0 / (2.0 * math.pi * FREQUENCIA * Xc)
    
    print(f"1. Potência Reativa a ser anulada (por fase): {Q_carga_fase/1000:.2f} kVAr")
    print(f"2. Tensão de Fase na Carga (|V_carga|): {V_carga_mod:.2f} V")
    print(f"3. Reatância Capacitiva necessária (Xc): {Xc:.2f} Ohms")
    print(f"4. Capacitância necessária (C): {C * 1e6:.2f} uF  ({C:.6e} F)\n")
    
    return C, Xc

def calcular_perdas_pos_correcao(id_fonte, id_linha, id_carga, Xc, S_linha_antiga):
    """Calcula as novas perdas na linha após a instalação do banco de capacitores."""
    
    print("--- ANÁLISE PÓS-CORREÇÃO DE FATOR DE POTÊNCIA ---")
    
    # Se Xc for 0, significa que não houve correção (carga já era resistiva ou capacitiva)
    if Xc == 0.0:
        print("Sem banco de capacitores instalado. As perdas permanecem iguais.\n")
        return
        
    Van = fontes[id_fonte]
    Z_linha = linhas[id_linha]
    Z_carga_original = cargas[id_carga]
    
    # Passo 1: Criar a impedância do capacitor (Puramente imaginária negativa)
    Z_cap = complex(0.0, -Xc)
    
    # Passo 2: Calcular a nova carga equivalente (Carga Original // Banco de Capacitores)
    # Produto pela soma
    Z_carga_nova = (Z_carga_original * Z_cap) / (Z_carga_original + Z_cap)
    print(f"Nova Impedância da Carga (Eq): {Z_carga_nova.real:.3f} + j{Z_carga_nova.imag:.3f} Ohms")
    
    # Passo 3: Recalcular a corrente da linha
    Z_total_novo = Z_linha + Z_carga_nova
    Ia_nova = Van / Z_total_novo
    print(f"Nova Corrente da Linha (Ia): {rect_to_polar_str(Ia_nova)} A")
    
    # Passo 4: Calcular as novas perdas na linha
    S_linha_nova_1f = Z_linha * (abs(Ia_nova)**2)
    S_linha_nova_3f = 3 * S_linha_nova_1f
    
    print("\nNOVA PERDA NA LINHA (Total Trifásica):")
    print(format_power_str(S_linha_nova_3f))
    
    P_antiga_kW = S_linha_antiga.real / 1000
    P_nova_kW = S_linha_nova_3f.real / 1000
    economia_kW = P_antiga_kW - P_nova_kW
    print(f"-> Economia de dissipação térmica: {economia_kW:.2f} kW a menos aquecendo os cabos!\n")

# ==========================================
# 4. ORQUESTRAÇÃO GERAL
# ==========================================
def analisar_circuito(id_fonte, id_linha, id_carga):
    """Função mestre que aciona as correntes e depois as potências."""
    print("="*60)
    print(f" ANÁLISE DO SISTEMA: {id_fonte} - {id_linha} - {id_carga}")
    print("="*60)
    
    # Passo 1: Obter as correntes
    Ia, Ib, Ic = calcular_correntes(id_fonte, id_linha, id_carga)
    
    # Passo 2: Calcular as potências
    S_carga_1f, S_linha_antiga_3f = calcular_potencias(id_fonte, id_linha, id_carga, Ia)

    # Passo 3: Calcular correção do fator de potência
    C_farads, Xc = calcular_correcao_fp(id_carga, Ia, S_carga_1f)

    # 4. Análise do novo cenário otimizado
    calcular_perdas_pos_correcao(id_fonte, id_linha, id_carga, Xc, S_linha_antiga_3f)

# ==========================================
# 5. EXECUÇÃO
# ==========================================
# Topologia pedida na Questão 1 (I) da Lista 2
analisar_circuito('F2', 'L2', 'C1//C1')