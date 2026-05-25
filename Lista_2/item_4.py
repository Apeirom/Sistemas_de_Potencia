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
# FONTE F4 (Totalmente Desequilibrada)
Va_f4 = polar_to_rect(6000.0, 20.0)
Vb_f4 = polar_to_rect(6000.0, 90.0)
Vc_f4 = polar_to_rect(8000.0, -90.0)

# LINHA L1 (Sem mútuas)
Z_L1 = complex(0.375, 0.50)

# CARGA C3 (Delta convertido para Estrela Equivalente)
Z_C3 = complex(20.0, 0.0) / 3.0

# ==========================================
# 3. MOTOR DE CÁLCULO
# ==========================================
def analisar_sistema_f4():
    print("="*60)
    print(" ANÁLISE DE FONTE DESEQUILIBRADA: F4 - L1 - C3")
    print("="*60)

    # 1. Admitância Total do Ramo (Igual para todas as fases)
    Z_ramo = Z_L1 + Z_C3
    Y_ramo = 1.0 / Z_ramo

    # 2. d) Deslocamento de Neutro (V_N'N)
    # Como Y_A = Y_B = Y_C, a equação simplifica-se para a média das tensões
    V_nn = (Va_f4 + Vb_f4 + Vc_f4) / 3.0

    # 3. a) Correntes de Linha
    Ia = (Va_f4 - V_nn) * Y_ramo
    Ib = (Vb_f4 - V_nn) * Y_ramo
    Ic = (Vc_f4 - V_nn) * Y_ramo
    
    print("a) Correntes na Linha:")
    print(f"   Ia: {rect_to_polar_str(Ia)} A")
    print(f"   Ib: {rect_to_polar_str(Ib)} A")
    print(f"   Ic: {rect_to_polar_str(Ic)} A\n")

    # 4. c) Corrente de Neutro
    # A carga equivalente C3 é isolada, logo a corrente de neutro tem de ser zero.
    In = Ia + Ib + Ic

    # 5. b) Tensões de Fase NA CARGA (V_A'N', V_B'N', V_C'N')
    Van_carga = Ia * Z_C3
    Vbn_carga = Ib * Z_C3
    Vcn_carga = Ic * Z_C3
    
    print("b) Tensões de Fase na Carga (em kV, face ao centro estrela N'):")
    print(f"   Va'n': {rect_to_polar_str(Van_carga / 1000)} kV")
    print(f"   Vb'n': {rect_to_polar_str(Vbn_carga / 1000)} kV")
    print(f"   Vc'n': {rect_to_polar_str(Vcn_carga / 1000)} kV\n")

    # 6. e) Potências Complexas Fornecidas pela FONTE
    S_FA = Va_f4 * Ia.conjugate()
    S_FB = Vb_f4 * Ib.conjugate()
    S_FC = Vc_f4 * Ic.conjugate()
    S_F_Total = S_FA + S_FB + S_FC

    print(f"c) Corrente de Neutro de Retorno (In): {abs(In):.4f} A (Nula, sistema isolado)\n")

    print(f"d) Deslocamento do Neutro da Carga (V_N'N): {rect_to_polar_str(V_nn)} V\n")

    print("e) Potências Fornecidas pela FONTE:")
    print(f"   Fase A: {format_power_str(S_FA)}")
    print(f"   Fase B: {format_power_str(S_FB)}")
    print(f"   Fase C: {format_power_str(S_FC)}")
    print(f"   TOTAL : {format_power_str(S_F_Total)}\n")

    # 7. f) Potências Complexas Consumidas pela CARGA
    S_CA = Z_C3 * (abs(Ia)**2)
    S_CB = Z_C3 * (abs(Ib)**2)
    S_CC = Z_C3 * (abs(Ic)**2)
    S_C_Total = S_CA + S_CB + S_CC

    print("f) Potências Consumidas pela CARGA:")
    print(f"   Fase A: {format_power_str(S_CA)}")
    print(f"   Fase B: {format_power_str(S_CB)}")
    print(f"   Fase C: {format_power_str(S_CC)}")
    print(f"   TOTAL : {format_power_str(S_C_Total)}\n")

# ==========================================
# 4. EXECUÇÃO 
# ==========================================
analisar_sistema_f4()