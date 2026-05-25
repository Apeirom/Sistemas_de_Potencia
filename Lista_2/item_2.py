import cmath
import math

# ==========================================
# 1. FUNÇÕES AUXILIARES
# ==========================================
def polar_to_rect(modulo, angulo_graus):
    return cmath.rect(modulo, math.radians(angulo_graus))

def rect_to_polar_str(numero_complexo):
    modulo, angulo_rad = cmath.polar(numero_complexo)
    return f"{modulo:>8.2f} < {math.degrees(angulo_rad):>6.2f}°"

def format_power_str(S_VA):
    P_kW = S_VA.real / 1000
    Q_kVAr = S_VA.imag / 1000
    S_kVA_mod = abs(S_VA) / 1000
    angulo = math.degrees(cmath.phase(S_VA))
    return f"{P_kW:>7.2f} kW + j {Q_kVAr:>7.2f} kVAr  |  {S_kVA_mod:>7.2f} < {angulo:>6.2f}° kVA"

# ==========================================
# 2. DEFINIÇÃO DA FONTE E MALHA
# ==========================================
# Fonte 1: 6350 < 10°
Van = polar_to_rect(6350.0, 10.0)
alfa = polar_to_rect(1.0, 120.0)
Vbn = Van * (alfa ** 2)  # Defasagem de -120°
Vcn = Van * alfa         # Defasagem de +120°

linhas = {
    'L1': complex(0.375, 0.50), # Sem mútua
    'L2': complex(0.80, 1.40) - complex(0.0, 0.36) # Zp - Zm
}

# Adicionamos uma flag 'ligacao' para saber se o neutro desloca ou não
cargas = {
    'C1': {'Z': complex(18.0, 6.0),     'ligacao': 'isolada'},
    'C2': {'Z': complex(12.0, -4.0),    'ligacao': 'aterrada'},
    'C3': {'Z': complex(20.0, 0.0)/3.0, 'ligacao': 'isolada'} # Delta -> Estrela Eq.
}

# ==========================================
# 3. MOTOR DE CÁLCULO (FALTA NA FASE B)
# ==========================================
def simular_falta_faseB(id_linha, id_carga):
    print("="*70)
    print(f" ANÁLISE DE DEFEITO (Fase B Aberta): F1_Def - {id_linha} - {id_carga}")
    print("="*70)

    Z_linha = linhas[id_linha]
    Z_carga = cargas[id_carga]['Z']
    ligacao = cargas[id_carga]['ligacao']

    # 1. Impedâncias e Admitâncias Totais dos ramos A e C
    Z_ramo = Z_linha + Z_carga
    Y_ramo = 1.0 / Z_ramo
    # Ramo B está aberto na fonte, portanto Y_B = 0
    
    # 2. d) Tensão de Deslocamento de Neutro (V_N'N)
    if ligacao == 'isolada':
        # V_N'N = (Van*Ya + Vcn*Yc) / (Ya + Yc)
        # Como Ya = Yc, a equação simplifica para a média das duas tensões ativas
        V_nn = (Van * Y_ramo + Vcn * Y_ramo) / (Y_ramo + Y_ramo)
    else:
        # Se for aterrada, o neutro da carga está cravado no terra da fonte
        V_nn = complex(0, 0)
    
    # 3. a) Correntes de Linha (Ia, Ib, Ic)
    Ia = (Van - V_nn) * Y_ramo
    Ib = complex(0, 0) # Fase B rompida!
    Ic = (Vcn - V_nn) * Y_ramo
    
    print("a) Correntes na Linha:")
    print(f"   Ia: {rect_to_polar_str(Ia)} A")
    print(f"   Ib: {rect_to_polar_str(Ib)} A")
    print(f"   Ic: {rect_to_polar_str(Ic)} A\n")

    # 4. c) Corrente de Neutro na Fonte (In)
    In = Ia + Ib + Ic

    # 5. b) Tensões de Fase na Carga (V_A'N', V_B'N', V_C'N')
    # Tensão é a corrente que passa pela carga multiplicada pela sua impedância
    Van_carga = Ia * Z_carga
    Vcn_carga = Ic * Z_carga
    
    # A fase B não tem corrente, logo não tem queda de tensão na impedância da carga.
    # Toda a tensão do ponto N' aparece no terminal B' da carga.
    Vbn_carga = complex(0, 0) 

    print("b) Tensões de Fase na Carga (em kV, relativas ao neutro da carga N'):")
    print(f"   Va'n': {rect_to_polar_str(Van_carga / 1000)} kV")
    print(f"   Vb'n': {rect_to_polar_str(Vbn_carga / 1000)} kV")
    print(f"   Vc'n': {rect_to_polar_str(Vcn_carga / 1000)} kV\n")

    print(f"c) Corrente de Neutro de Retorno:  {rect_to_polar_str(In)} A")
    if ligacao == 'isolada':
        print("   (Note que é 0 A porque o sistema é isolado e I_c = -I_a)\n")
    else:
        print("   (Note que a corrente flui pelo terra pois o sistema é aterrado)\n")


    print(f"d) Deslocamento de Neutro (V_N'N): {rect_to_polar_str(V_nn)} V\n")


    # 6. e) Potências Complexas na Fonte (S = V * I*)
    S_FA = Van * Ia.conjugate()
    S_FB = complex(0,0)
    S_FC = Vcn * Ic.conjugate()
    S_F_Total = S_FA + S_FB + S_FC

    print("e) Potências Fornecidas pela FONTE:")
    print(f"   Fase A: {format_power_str(S_FA)}")
    print(f"   Fase B: {format_power_str(S_FB)}")
    print(f"   Fase C: {format_power_str(S_FC)}")
    print(f"   TOTAL : {format_power_str(S_F_Total)}\n")

    # 7. f) Potências Complexas na Carga (S = Z * |I|^2)
    S_CA = Z_carga * (abs(Ia)**2)
    S_CB = complex(0,0)
    S_CC = Z_carga * (abs(Ic)**2)
    S_C_Total = S_CA + S_CB + S_CC

    print("f) Potências Consumidas pela CARGA:")
    print(f"   Fase A: {format_power_str(S_CA)}")
    print(f"   Fase B: {format_power_str(S_CB)}")
    print(f"   Fase C: {format_power_str(S_CC)}")
    print(f"   TOTAL : {format_power_str(S_C_Total)}\n")


# ==========================================
# 4. EXECUÇÃO DAS TOPOLOGIAS (Lista 2 - Q2)
# ==========================================
# (I) F1 Defeituosa - L2 - C1
simular_falta_faseB('L2', 'C1')

# (II) F1 Defeituosa - L2 - C3
simular_falta_faseB('L2', 'C3')

# (III) F1 Defeituosa - L1 - C2
simular_falta_faseB('L1', 'C2')