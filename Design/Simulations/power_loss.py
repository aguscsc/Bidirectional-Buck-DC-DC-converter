import pandas as pd

# Buck mode
Vin = 23.0
Vo = 14.0
fs = 60_000.0
D = 0.609
D2 = 0.555
Iout = 0.357
diL = 0.107
IL_rms = (Iout**2 + (diL**2)/12)**0.5
# Boost mode
Vin2 = 12.0
Vo2 = 27.0
fs2 = 60_000.0
D2 = 0.555
Iout2 = 5.0/27.0
diL = 0.107
IL_rms2 = (Iout2**2 + (diL**2)/12)**0.5


# Assumptions 
Vgs = 12.0
Qg = 62e-9            # IRFZ44N total gate charge @ ~10V
tr_tf = 115e-9        # combined rise+fall (worst-ish to match user calc)
t_dead = 400e-9       # IR2184 typ
Vf_body = 0.7         # body diode drop (low-side during deadtime)
Rds_on_typ = 0.015    # 15 mΩ (typ at 10V)
Rds_on_hot = 0.025    # rough hot value
R_L_DCR = 0.25        # Inductor DCR (Ohm) assumption
ESR_out = 0.144        # Output cap ESR (Ohm) 
ESR_in = 0.046810     # Input cap ESR (Ohm) 
R_g_HS = 10.0         # Gate resistor HS
R_g_LS = 10.0         # Gate resistor LS
R_pull = 10_000.0     # R4, R5
V_in_logic = 5.0      # PWM logic level for R6 (approx)

# Helper currents
ICout_rms = diL/(2*(3**0.5))
ICin_rms = Iout*(D*(1-D))**0.5

# MOSFET losses 
P_HS_cond = D*(IL_rms)**2 * Rds_on_typ
P_LS_cond = (1-D)*(IL_rms)**2 * Rds_on_typ
P_HS_sw = 0.5*Vin*Iout*tr_tf*fs
P_LS_dt = 2*Iout*Vf_body*t_dead*fs

# Gate-drive total per FET
P_drv_gates = 2*Qg*Vgs*fs

# Pull-down resistors (gate-to-source 10k)
P_R4 = D * (Vgs**2)/R_pull
P_R5 = (1-D) * (Vgs**2)/R_pull

# Inductor & capacitors
P_L_cu = IL_rms**2 * R_L_DCR
P_Cout = ICout_rms**2 * ESR_out
P_Cin = ICin_rms**2 * ESR_in    


rows = [
    ["HS MOSFET conduction", P_HS_cond],
    ["LS MOSFET conduction", P_LS_cond],
    ["HS MOSFET switching", P_HS_sw],
    ["LS body diode (deadtime)", P_LS_dt],
    ["Gate resistors", P_drv_gates],
    ["Inductor copper (DCR)", P_L_cu],
    ["Output cap ESR (C2)", P_Cout],
    ["Input cap ESR (C1)", P_Cin],
    ["Pull-down R4 (10k)", P_R4],
    ["Pull-down R5 (10k)", P_R5],
]

df = pd.DataFrame(rows, columns=["Component / Mechanism", "Power_W"])
df["Power_mW"] = 1000*df["Power_W"]
df.loc["TOTAL"] = ["TOTAL", df["Power_W"].sum(), df["Power_mW"].sum()]

print(df.round(3))

efficiency= (5 - df.iloc[-1]["Power_W"])/5
print(f"{efficiency:.2%}","efficiency")

# ---------- BOOST MODE BLOCK ----------
# Use your existing variables: Vin, Vo, fs, D, Iout, diL, etc.

# 1) Inductor average & RMS in boost
IL_avg_boost = (Vo2/Vin2) * Iout2         # = Iin
IL_rms_boost = (IL_avg_boost**2 + (diL**2)/12.0)**0.5

# 2) Device RMS currents (LS = main switch, HS = synchronous)
I_LS_rms_boost = (D2**0.5) * IL_rms_boost
I_HS_rms_boost = ((1-D2)**0.5) * IL_rms_boost

# 3) Conduction losses (use your Rds_on_typ or hot)
P_LS_cond_boost = I_LS_rms_boost**2 * Rds_on_typ
P_HS_cond_boost = I_HS_rms_boost**2 * Rds_on_typ

# 4) Switching losses
# Main switch (LS) switches ~Vo
P_LS_sw_boost = 0.5 * Vo2 * IL_avg_boost * tr_tf * fs
# Sync (HS) switching is usually small; set to 0 or estimate with (Vo - Vin)
P_HS_sw_boost = 0.0  # or: 0.5 * (Vo - Vin) * IL_avg_boost * tr_tf * fs

# 5) Deadtime diode on HS device
P_HS_dt_boost = 2 * IL_avg_boost * Vf_body * t_dead * fs

# 6) Gate-drive (same Qg·Vgs·fs per FET)
P_gates_boost = 2 * Qg * Vgs * fs

# 7) Capacitors & inductor copper (boost-side approximations)
ICout_rms_boost = Iout2 * (D2/(1-D2))**0.5
ICin_rms_boost = diL/(2*(3**0.5))  # conservative
P_L_cu_boost = IL_rms_boost**2 * R_L_DCR
P_Cout_boost = ICout_rms_boost**2 * ESR_in
P_Cin_boost = ICin_rms_boost**2 * ESR_out

rows_boost = [
    ["[BOOST] LS MOSFET conduction", P_LS_cond_boost],
    ["[BOOST] HS MOSFET conduction", P_HS_cond_boost],
    ["[BOOST] LS MOSFET switching", P_LS_sw_boost],
    ["[BOOST] HS body diode (deadtime)", P_HS_dt_boost],
    ["[BOOST] Gate drive (both)", P_gates_boost],
    ["[BOOST] Inductor copper (DCR)", P_L_cu_boost],
    ["[BOOST] Output cap ESR", P_Cout_boost],
    ["[BOOST] Input cap ESR", P_Cin_boost],
    ["Pull-down R4 (10k)", P_R4],
    ["Pull-down R5 (10k)", P_R5]
]

df_boost = pd.DataFrame(rows_boost, columns=["Component / Mechanism", "Power_W"])
df_boost["Power_mW"] = 1000*df_boost["Power_W"]
df_boost.loc["TOTAL"] = ["[BOOST] TOTAL", df_boost["Power_W"].sum(), df_boost["Power_mW"].sum()]

print(df_boost.round(3))

# Efficiency in boost at the same 5 W output:
eff_boost = (5 - df_boost.iloc[-1]["Power_W"]) / 5
print(f"{eff_boost:.2%}", "efficiency (boost)")
