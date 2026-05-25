import cmath

# ==========================================
# 1. PARÂMETROS REAIS
# ==========================================
V_fonte_real = 480.0
Z_fonte_int = complex(0, 0.2)
Z1 = complex(0.2, 0.6)
Z2 = complex(15, 20)

# Cálculo de Z3 (Real)
S3_nom = 12000
cos_phi = 0.85
phi = cmath.acos(cos_phi)
S3 = cmath.rect(S3_nom, phi)
Z3 = (480.0**2) / S3.conjugate()

# ==========================================
# 2. MOTOR DE CÁLCULO
# ==========================================
def resolver_sistema(base_id, Sb, Vb):
    print(f"\n--- BASE {base_id}: Sb={Sb} VA, Vb={Vb} V ---")
    
    # Bases
    Zb = (Vb**2) / Sb
    
    # Conversão para PU
    Zf_pu = Z_fonte_int / Zb
    Z1_pu = Z1 / Zb
    Z2_pu = Z2 / Zb
    Z3_pu = Z3 / Zb
    Vf_pu = (V_fonte_real / Vb) + 0j
    
    # Circuito: Zeq = Zf + Z1 + (Z2 // Z3)
    Z23_pu = (Z2_pu * Z3_pu) / (Z2_pu + Z3_pu)
    Zeq_pu = Zf_pu + Z1_pu + Z23_pu
    
    # a) Corrente na linha (Z1) em p.u.
    I_pu = Vf_pu / Zeq_pu
    print(f"a) Corrente na linha (I_pu): {abs(I_pu):.4f} < {math.degrees(cmath.phase(I_pu)):.2f}° p.u.")
    
    # b) Potência complexa em todos os bipolos
    # S = V*I* ou S = Z*|I|^2
    S_fonte = Vf_pu * I_pu.conjugate()
    S_Zf = Zf_pu * abs(I_pu)**2
    S_Z1 = Z1_pu * abs(I_pu)**2
    S_Z2 = Z2_pu * abs(I_pu * (Z3_pu / (Z2_pu + Z3_pu)))**2 # Divisor de corrente
    S_Z3 = Z3_pu * abs(I_pu * (Z2_pu / (Z2_pu + Z3_pu)))**2
    
    print("b) Potência Complexa em p.u.:")
    print(f"   Fonte: {S_fonte.real:.4f} + j{S_fonte.imag:.4f}")
    print(f"   Z_fonte: {S_Zf.real:.4f} + j{S_Zf.imag:.4f}")
    print(f"   Z1: {S_Z1.real:.4f} + j{S_Z1.imag:.4f}")
    print(f"   Z2: {S_Z2.real:.4f} + j{S_Z2.imag:.4f}")
    print(f"   Z3: {S_Z3.real:.4f} + j{S_Z3.imag:.4f}")

# ==========================================
# 3. EXECUÇÃO
# ==========================================
resolver_sistema("I", 20000, 480)
resolver_sistema("II", 12000, 480)