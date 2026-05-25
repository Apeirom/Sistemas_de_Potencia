import cmath
import math

# ==========================================
# 1. PARÂMETROS REAIS
# ==========================================
V_fonte_real = 480.0
Z_fonte_int  = complex(0, 0.2)
Z1           = complex(0.2, 0.6)
Z2           = complex(15, 20)

# Z3: carga 12 kVA, fp=0,85 ind, Vn=480 V
S3_nom = 12000
cos_phi = 0.85
phi    = math.acos(cos_phi)         # ← math.acos (retorna float, não complexo)
S3     = cmath.rect(S3_nom, phi)    # S3 = P + jQ
Z3     = (480.0**2) / S3.conjugate()

# ==========================================
# 2. FUNÇÕES AUXILIARES
# ==========================================
def polar(c):
    return f"{abs(c):.4f} ∠{math.degrees(cmath.phase(c)):+.2f}°"

def fmt_s(label, S, indent="   "):
    return (f"{indent}{label:<18}: "
            f"{polar(S)} p.u.    "
            f"({S.real:+.4f} + j{S.imag:+.4f}) p.u.")

# ==========================================
# 3. MOTOR DE CÁLCULO
# ==========================================
def resolver(base_id, Sb, Vb):
    Zb = (Vb**2) / Sb

    # Conversão para p.u.
    Zf_pu = Z_fonte_int / Zb
    Z1_pu = Z1 / Zb
    Z2_pu = Z2 / Zb
    Z3_pu = Z3 / Zb
    Vf_pu = (V_fonte_real / Vb) + 0j   # referência angular

    # Paralelo Z2 // Z3
    Z23_pu = (Z2_pu * Z3_pu) / (Z2_pu + Z3_pu)
    Zeq_pu = Zf_pu + Z1_pu + Z23_pu

    # Tensões nos nós
    I_linha = Vf_pu / Zeq_pu
    V_A     = Vf_pu - I_linha * Zf_pu
    V_B     = V_A   - I_linha * Z1_pu

    # Correntes nos ramos paralelos
    I_Z2 = V_B / Z2_pu
    I_Z3 = V_B / Z3_pu

    # Potências complexas
    S_fonte = Vf_pu * I_linha.conjugate()
    S_Zf    = Zf_pu * abs(I_linha)**2
    S_Z1    = Z1_pu * abs(I_linha)**2
    S_Z2    = Z2_pu * abs(I_Z2)**2
    S_Z3    = Z3_pu * abs(I_Z3)**2

    erro = abs(S_fonte - (S_Zf + S_Z1 + S_Z2 + S_Z3))

    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  QUESTÃO 05 — BASE {base_id}:  Sb = {Sb} VA,  Vb = {Vb} V")
    print(f"  Zb = {Zb:.4f} Ω")
    print(sep)

    print(f"\n  Impedâncias em p.u.:")
    for nome, Z in [("Z_fonte_int", Zf_pu), ("Z1", Z1_pu),
                    ("Z2", Z2_pu),          ("Z3", Z3_pu)]:
        print(f"   {nome:<14}: {polar(Z)}")

    print(f"\n  a) Corrente na linha (Z1):")
    print(f"     I_linha = {polar(I_linha)} p.u.")

    print(f"\n  Tensões nos nós (p.u.):")
    print(f"   V_fonte (Vf)   = {polar(Vf_pu)}")
    print(f"   V_A (após Zf)  = {polar(V_A)}")
    print(f"   V_B (na carga) = {polar(V_B)}")

    print(f"\n  b) Potências complexas em p.u.  [módulo∠fase  |  P + jQ]:")
    print(fmt_s("Fonte (fornece)", S_fonte))
    print(fmt_s("Z_fonte_int",     S_Zf))
    print(fmt_s("Z1 (linha)",      S_Z1))
    print(fmt_s("Z2",              S_Z2))
    print(fmt_s("Z3 (carga ind.)", S_Z3))
    print(f"\n   {'Balanço ΣS':<18}: erro = {erro:.2e} p.u.  "
          f"({'✔ OK' if erro < 1e-10 else '✗ ERRO'})")

# ==========================================
# 4. EXECUÇÃO
# ==========================================
resolver("I",  Sb=20000, Vb=480)
resolver("II", Sb=12000, Vb=480)