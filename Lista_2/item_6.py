import cmath
import math

# ============================================================
# QUESTÕES 06 e 07 — Sistemas de Potência
# Transformador monofásico T1 + linha + carga C5
# ============================================================

#  Dados do transformador T1 
Vnp     = 6300.0          # V  (tensão nominal do primário)
Vns     = 250.0           # V  (tensão nominal do secundário)
Sn_T1   = 1000e3          # VA (potência nominal)
Zcc_pu  = complex(0.01, 0.1)   # p.u. na base própria do trafo

#  Dados da linha (cabo) 
# "dois trechos de cabo (ida e volta)" → 2 cabos em série na Q6
# "3 cabos sem mútuas" na Q7 → 1 cabo por fase
Zp_km = complex(0.2, 0.4)  # Ω/km por cabo
l     = 4.0                 # km

#  Dados da carga C5 
Sn_C5  = 700e3    # VA
fp_C5  = 0.8      # indutivo
Vn_C5  = 230.0    # V (tensão nominal)
phi_C5 = math.acos(fp_C5)
# Impedância real de C5 em seus terminais nominais
Z_C5_real = (Vn_C5**2) / (Sn_C5 * complex(fp_C5, -math.sin(phi_C5)))

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def polar(c, unit=""):
    u = f" {unit}" if unit else ""
    return f"{abs(c):.4f}{u} ∠{math.degrees(cmath.phase(c)):+.2f}°"

def rect(c, unit=""):
    u = f" {unit}" if unit else ""
    return f"({c.real:+.4f} + j{c.imag:+.4f}){u}"

def fmt_z(label, Z, unit="p.u."):
    return f"   {label:<22}: {polar(Z, unit)}   {rect(Z, unit)}"

def fmt_s(label, S, Sb, indent="   "):
    S_kva = S * Sb / 1e3
    return (f"{indent}{label:<22}: "
            f"{polar(S_kva, 'kVA')}   "
            f"P={S_kva.real:+.4f} kW  Q={S_kva.imag:+.4f} kVAr")

def cabecalho(titulo):
    sep = "=" * 70
    print(f"\n{sep}\n  {titulo}\n{sep}")

# ============================================================
# QUESTÃO 06 — Circuito monofásico
# Topologia: Fonte(220V) → T1(elev) → Linha(ida+volta) → T1(abx) → C5
#
# Zonas de base:
#   Zona 1 (fonte):  Vb1 = 220 V  — não usada diretamente no cálculo p.u.
#   Zona 2 (linha):  Vb2 = 6300 V (secundário do T1 elevador = Vnp)
#   Zona 3 (carga):  Vb3 = 250 V  (secundário do T1 abaixador = Vns)
# Base de potência:  Sb = 1000 kVA (= Sn do trafo)
# ============================================================
def questao_06():
    cabecalho("QUESTÃO 06 — Circuito monofásico  (Sb = 1000 kVA)")

    Sb  = Sn_T1          # 1 000 000 VA
    Vb1 = 220.0          # V  (zona fonte)
    Vb2 = Vnp            # V  (zona linha)
    Vb3 = Vns            # V  (zona carga)

    Zb1 = Vb1**2 / Sb
    Zb2 = Vb2**2 / Sb
    Zb3 = Vb3**2 / Sb

    print(f"\n  Bases por zona:")
    print(f"   {'Zona 1 (fonte)':<22}: Vb = {Vb1:.1f} V,  Zb = {Zb1:.6f} Ω")
    print(f"   {'Zona 2 (linha)':<22}: Vb = {Vb2:.1f} V,  Zb = {Zb2:.6f} Ω")
    print(f"   {'Zona 3 (carga)':<22}: Vb = {Vb3:.1f} V,  Zb = {Zb3:.6f} Ω")

    # Impedâncias em p.u.
    # T1 já fornecido em p.u. na sua própria base (Sn, Vnp, Vns) → transfere direto
    # Dois trafos idênticos em série (elevador + abaixador)
    Zt_pu      = Zcc_pu
    # Linha: 2 cabos em série (ida e volta) na zona 2
    Z_linha_pu = (2 * Zp_km * l) / Zb2
    # Carga: convertida para zona 3
    Z_C5_pu    = Z_C5_real / Zb3

    print(f"\n  Impedâncias em p.u.:")
    print(fmt_z("T1 (cada trafo)", Zt_pu))
    print(fmt_z("Z_linha (2 cabos)", Z_linha_pu))
    print(fmt_z("Z_C5", Z_C5_pu))

    # Circuito equivalente série
    # Vf_pu = 220/220 = 1,0 ∠0° (referência)
    Vf_pu  = 1.0 + 0j
    Zeq_pu = 2 * Zt_pu + Z_linha_pu + Z_C5_pu

    # a) Corrente na linha em p.u.
    I_pu = Vf_pu / Zeq_pu

    # Corrente real na zona 2 (linha)
    Ib2      = Sb / Vb2          # corrente de base na zona 2
    I_linha_A = abs(I_pu) * Ib2

    print(f"\n  a) Corrente na linha:")
    print(f"     I = {polar(I_pu, 'p.u.')}")
    print(f"     I = {I_linha_A:.4f} A  (valor real na zona 2, Vb = {Vb2:.0f} V)")

    # b) Queda de tensão e perdas ativas em cada cabo
    Z_cabo_real = Zp_km * l                          # impedância de 1 cabo
    V_queda_V   = I_linha_A * abs(Z_cabo_real)       # |ΔV| por cabo [V]
    P_perda_W   = (I_linha_A**2) * Z_cabo_real.real  # perdas em 1 cabo [W]

    print(f"\n  b) Por cabo (1 cabo = {l:.1f} km):")
    print(f"     Z_cabo_real       = {rect(Z_cabo_real, 'Ω')}")
    print(f"     |ΔV| por cabo     = {V_queda_V:.4f} V")
    print(f"     P_perdas por cabo = {P_perda_W:.4f} W")

    # c) Tensão nos terminais da carga
    V_carga_pu = I_pu * Z_C5_pu
    V_carga_V  = abs(V_carga_pu) * Vb3

    print(f"\n  c) Tensão na carga:")
    print(f"     V_carga = {polar(V_carga_pu, 'p.u.')}")
    print(f"     V_carga = {V_carga_V:.4f} V  (valor real, Vb3 = {Vb3:.0f} V)")

    # d) Potência complexa total na carga
    S_C5_pu = V_carga_pu * I_pu.conjugate()
    S_C5_kVA = S_C5_pu * Sb / 1e3

    print(f"\n  d) Potência complexa na carga C5:")
    print(f"     S = {polar(S_C5_kVA, 'kVA')}")
    print(f"     P = {S_C5_kVA.real:+.4f} kW   Q = {S_C5_kVA.imag:+.4f} kVAr")

    # Balanço global
    S_fonte_pu = Vf_pu * I_pu.conjugate()
    S_2Zt_pu   = 2 * Zt_pu * abs(I_pu)**2
    S_linha_pu = Z_linha_pu * abs(I_pu)**2
    erro = abs(S_fonte_pu - (S_2Zt_pu + S_linha_pu + S_C5_pu))
    print(f"\n  Balanço de potência (verificação):")
    print(fmt_s("Fonte (fornece)",   S_fonte_pu, Sb))
    print(fmt_s("2×T1 (perdas)",     S_2Zt_pu,  Sb))
    print(fmt_s("Linha (perdas)",    S_linha_pu, Sb))
    print(fmt_s("C5 (carga)",        S_C5_pu,   Sb))
    print(f"   {'Erro ΣS':<22}: {erro:.2e} p.u.  "
          f"({'✔ OK' if erro < 1e-10 else '✗ ERRO'})")


# ============================================================
# QUESTÃO 07 — Circuito trifásico
# Topologia: Fonte(3φ, 220V fase) → Banco T1(Y-Y, elev)
#            → Linha(3 cabos, sem mútuas) → Banco T1(Y-Y, abx)
#            → 3×C5 em paralelo (estrela)
#
# Banco Y-Y: cada trafo recebe tensão de fase
#   Vb1_fase = 220 V,  Vb2_fase = 6300 V,  Vb3_fase = 250 V
# Base: Sb = 3000 kVA (3φ)
# Análise monofásica equivalente (por fase)
# ============================================================
def questao_07():
    cabecalho("QUESTÃO 07 — Circuito trifásico  (Sb = 3000 kVA, banco Y-Y)")

    Sb  = 3 * Sn_T1      # 3 000 000 VA
    Vb1 = 220.0          # V fase
    Vb2 = Vnp            # V fase (zona linha)
    Vb3 = Vns            # V fase (zona carga)

    Zb2 = Vb2**2 / Sb    # base por fase (usando Sb 3φ)
    Zb3 = Vb3**2 / Sb

    print(f"\n  Base 3φ: Sb = {Sb/1e3:.0f} kVA")
    print(f"  Arranjo do banco: Y-Y (elevador) e Y-Y (abaixador)")
    print(f"  Análise: monofásica equivalente por fase\n")
    print(f"  Bases por zona:")
    print(f"   {'Zona 2 (linha)':<22}: Vb = {Vb2:.1f} V fase,  Zb = {Zb2:.6f} Ω")
    print(f"   {'Zona 3 (carga)':<22}: Vb = {Vb3:.1f} V fase,  Zb = {Zb3:.6f} Ω")

    #Impedâncias em p.u.
    # Cada trafo T1 no banco: base própria = Sn_T1 = Sb/3 → Zcc_pu válido direto
    Zt_pu      = Zcc_pu
    # Linha: 1 cabo por fase (sistema 3φ, sem ida e volta)
    Z_linha_pu = (Zp_km * l) / Zb2
    # 3 cargas C5 em paralelo → Z_eq = Z_C5 / 3
    Z_3C5_pu   = (Z_C5_real / 3) / Zb3

    print(f"\n  Impedâncias em p.u.:")
    print(fmt_z("T1 (cada trafo)", Zt_pu))
    print(fmt_z("Z_linha (1 cabo/fase)", Z_linha_pu))
    print(fmt_z("3×C5 paralelo", Z_3C5_pu))

    #  Circuito equivalente monofásico
    Vf_pu  = 1.0 + 0j
    Zeq_pu = 2 * Zt_pu + Z_linha_pu + Z_3C5_pu
    I_pu   = Vf_pu / Zeq_pu

    # Corrente real na zona 2
    Ib2       = Sb / (3 * Vb2)     # corrente de base 3φ (Ib = Sb/(√3·VL) = Sb/(3·Vfase))
    I_linha_A = abs(I_pu) * Ib2

    print(f"\n  a) Corrente em um condutor da linha:")
    print(f"     I = {polar(I_pu, 'p.u.')}")
    print(f"     I = {I_linha_A:.4f} A  (valor real na zona 2, Vb_fase = {Vb2:.0f} V)")

    # b) Queda e perdas por cabo
    Z_cabo_real = Zp_km * l
    V_queda_V   = I_linha_A * abs(Z_cabo_real)
    P_perda_W   = (I_linha_A**2) * Z_cabo_real.real

    print(f"\n  b) Por cabo (1 cabo = {l:.1f} km):")
    print(f"     Z_cabo_real       = {rect(Z_cabo_real, 'Ω')}")
    print(f"     |ΔV| por cabo     = {V_queda_V:.4f} V")
    print(f"     P_perdas por cabo = {P_perda_W:.4f} W")

    # c) Tensão na carga
    V_carga_pu = I_pu * Z_3C5_pu
    V_carga_V  = abs(V_carga_pu) * Vb3

    print(f"\n  c) Tensão na carga (por fase):")
    print(f"     V_carga = {polar(V_carga_pu, 'p.u.')}")
    print(f"     V_carga = {V_carga_V:.4f} V fase   "
          f"({V_carga_V * math.sqrt(3):.4f} V linha)")

    # d) Potência complexa total 3φ na carga
    S_fase_pu  = V_carga_pu * I_pu.conjugate()
    S_total_pu = 3 * S_fase_pu
    S_total_kVA = S_total_pu * Sb / 1e3

    print(f"\n  d) Potência complexa total 3φ na carga (3×C5):")
    print(f"     S = {polar(S_total_kVA, 'kVA')}")
    print(f"     P = {S_total_kVA.real:+.4f} kW   Q = {S_total_kVA.imag:+.4f} kVAr")

    # Balanço
    S_fonte_pu  = 3 * Vf_pu * I_pu.conjugate()
    S_2Zt_pu    = 3 * 2 * Zt_pu * abs(I_pu)**2
    S_linha_pu  = 3 * Z_linha_pu * abs(I_pu)**2
    erro = abs(S_fonte_pu - (S_2Zt_pu + S_linha_pu + S_total_pu))
    print(f"\n  Balanço de potência 3φ (verificação):")
    print(fmt_s("Fonte (fornece)",   S_fonte_pu,  Sb))
    print(fmt_s("2×Banco T1 (perd.)",S_2Zt_pu,   Sb))
    print(fmt_s("Linha 3φ (perd.)",  S_linha_pu,  Sb))
    print(fmt_s("3×C5 (carga)",      S_total_pu,  Sb))
    print(f"   {'Erro ΣS':<22}: {erro:.2e} p.u.  "
          f"({'✔ OK' if erro < 1e-10 else '✗ ERRO'})")

# ============================================================
# EXECUÇÃO
# ============================================================
questao_06()
questao_07()