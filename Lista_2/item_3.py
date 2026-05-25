import cmath
import math

# ==========================================
# 1. FUNÇÕES AUXILIARES
# ==========================================
def polar_to_rect(modulo, angulo_graus):
    return cmath.rect(modulo, math.radians(angulo_graus))

def rect_to_polar_str(numero_complexo):
    modulo, angulo_rad = cmath.polar(numero_complexo)
    return f"{modulo:>8.2f} < {math.degrees(angulo_rad):>7.2f}°"

def format_power_str(S_VA):
    P_kW = S_VA.real / 1000
    Q_kVAr = S_VA.imag / 1000
    S_kVA_mod = abs(S_VA) / 1000
    angulo = math.degrees(cmath.phase(S_VA))
    return f"{P_kW:>8.2f} kW + j {Q_kVAr:>8.2f} kVAr  |  {S_kVA_mod:>8.2f} < {angulo:>6.2f}° kVA"

# ==========================================
# 2. DEFINIÇÃO DE PARÂMETROS
# ==========================================
# Operador de Rotação 120°
alfa = polar_to_rect(1.0, 120.0)

# FONTES (Convertidas para tensões de fase A, B e C)
fontes = {}
# F3: 6600 < 15° (Sequência Positiva)
Va_f3 = polar_to_rect(6600.0, 15.0)
fontes['F3'] = {
    'Va': Va_f3,
    'Vb': Va_f3 * (alfa ** 2), # Atrasada
    'Vc': Va_f3 * alfa         # Adiantada
}

# F2: VAB = 13800 < 50° (Sequência Negativa)
# VAN = (VAB / raiz(3)) < (50 - 30) = 7967.43 < 20°
Va_f2 = polar_to_rect(13800.0 / math.sqrt(3), 50.0 - 30.0)
fontes['F2'] = {
    'Va': Va_f2,
    'Vb': Va_f2 * alfa,        # Adiantada (Seq Negativa)
    'Vc': Va_f2 * (alfa ** 2)  # Atrasada
}

# LINHA L2
Zp_L2 = complex(0.80, 1.40)
Zm_L2 = complex(0.0, 0.36)
ZL_eff = Zp_L2 - Zm_L2   # Impedância efetiva da linha

# CARGA C4 (Desequilibrada)
Z_C4_A = complex(20.0, 10.0)
Z_C4_B = complex(20.0, 0.0)
Z_C4_C = complex(10.0, -20.0)
Z_At   = complex(0.1, 10.0)

# ==========================================
# 3. MOTOR DE CÁLCULO (SISTEMA TOTALMENTE DESEQUILIBRADO)
# ==========================================
def analisar_sistema_c4(id_fonte):
    print("="*80)
    print(f" ANÁLISE DE DESEQUILÍBRIO TOTAL: {id_fonte} - L2 - C4")
    print("="*80)

    # Captura das tensões da fonte
    Va, Vb, Vc = fontes[id_fonte]['Va'], fontes[id_fonte]['Vb'], fontes[id_fonte]['Vc']

    # 1. Admitâncias Totais por Fase (Linha + Carga)
    Z_total_A = ZL_eff + Z_C4_A
    Z_total_B = ZL_eff + Z_C4_B
    Z_total_C = ZL_eff + Z_C4_C
    
    Ya = 1.0 / Z_total_A
    Yb = 1.0 / Z_total_B
    Yc = 1.0 / Z_total_C

    # 2. Admitância Efetiva de Retorno (Aterramento + Mútua)
    Z_N_eff = Z_At + Zm_L2
    Yn_eff = 1.0 / Z_N_eff

    # 3. Deslocamento "Virtual" de Neutro (Teorema de Millman modificado)
    V_shift = (Va*Ya + Vb*Yb + Vc*Yc) / (Ya + Yb + Yc + Yn_eff)

    # 4. a) Correntes de Linha
    Ia = (Va - V_shift) * Ya
    Ib = (Vb - V_shift) * Yb
    Ic = (Vc - V_shift) * Yc
    
    print("a) Correntes na Linha:")
    print(f"   Ia: {rect_to_polar_str(Ia)} A")
    print(f"   Ib: {rect_to_polar_str(Ib)} A")
    print(f"   Ic: {rect_to_polar_str(Ic)} A\n")

    # 5. c) Corrente de Neutro
    In = Ia + Ib + Ic
    print(f"c) Corrente de Neutro de Retorno (In): {rect_to_polar_str(In)} A\n")

    # 6. d) Tensão REAL de Deslocamento do Neutro da Carga
    # Tensão no centro da estrela é a corrente In multiplicada pela impedância real do aterramento
    V_nn = In * Z_At
    print(f"d) Deslocamento do Neutro da Carga (V_N'N): {rect_to_polar_str(V_nn)} V\n")

    # 7. b) Tensões de Fase NA CARGA (V_A'N', V_B'N', V_C'N')
    Van_carga = Ia * Z_C4_A
    Vbn_carga = Ib * Z_C4_B
    Vcn_carga = Ic * Z_C4_C
    
    print("b) Tensões de Fase na Carga (em kV):")
    print(f"   Va'n': {rect_to_polar_str(Van_carga / 1000)} kV")
    print(f"   Vb'n': {rect_to_polar_str(Vbn_carga / 1000)} kV")
    print(f"   Vc'n': {rect_to_polar_str(Vcn_carga / 1000)} kV\n")

    # 8. e) Potências Complexas Fornecidas (S = V_fonte * I*)
    S_FA = Va * Ia.conjugate()
    S_FB = Vb * Ib.conjugate()
    S_FC = Vc * Ic.conjugate()
    S_F_Total = S_FA + S_FB + S_FC

    print("e) Potências Fornecidas pela FONTE:")
    print(f"   Fase A: {format_power_str(S_FA)}")
    print(f"   Fase B: {format_power_str(S_FB)}")
    print(f"   Fase C: {format_power_str(S_FC)}")
    print(f"   TOTAL : {format_power_str(S_F_Total)}\n")

    # 9. f) Potências Complexas Consumidas (S = Z * |I|^2)
    S_CA = Z_C4_A * (abs(Ia)**2)
    S_CB = Z_C4_B * (abs(Ib)**2)
    S_CC = Z_C4_C * (abs(Ic)**2)
    
    # IMPORTANTE: A impedância de aterramento também consome potência dissipada por calor!
    S_CAt = Z_At * (abs(In)**2)
    
    S_C_Total = S_CA + S_CB + S_CC + S_CAt

    print("f) Potências Consumidas pela CARGA + ATERRAMENTO:")
    print(f"   Fase A: {format_power_str(S_CA)}")
    print(f"   Fase B: {format_power_str(S_CB)}")
    print(f"   Fase C: {format_power_str(S_CC)}")
    print(f"   Aterra: {format_power_str(S_CAt)}")
    print(f"   TOTAL : {format_power_str(S_C_Total)}\n")

# ==========================================
# 4. EXECUÇÃO 
# ==========================================
# (I) F3 - L2 - C4
analisar_sistema_c4('F3')

# (II) F2 - L2 - C4
analisar_sistema_c4('F2')