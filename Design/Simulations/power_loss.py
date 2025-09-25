import pandas as pd

# Buck mode
Vin = 23.0
Vo = 14.0
fs = 60_000.0
D = 0.609
# Boost mode
#Vin = 12.0
#Vo = 27.0
#fs = 60_000.0
#D = 0.555
Iout = 0.357
diL = 0.107
IL_rms = (Iout**2 + (diL**2)/12)**0.5


# Assumptions 
Vgs = 12.0
Qg = 62e-9            # IRFZ44N total gate charge @ ~10V
tr_tf = 115e-9        # combined rise+fall (worst-ish to match user calc)
t_dead = 400e-9       # IR2184 typ
Vf_body = 0.7         # body diode drop (low-side during deadtime)
Rds_on_typ = 0.015    # 15 mΩ (typ at 10V)
Rds_on_hot = 0.025    # rough hot value
R_L_DCR = 0.25       # Inductor DCR (Ohm) assumption
ESR_out = 1.50        # Output cap ESR (Ohm) assumption (THT electrolytic/small film)
ESR_in = 2.00         # Input cap ESR (Ohm) assumption (small radial electrolytic)
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

# pull up & pull down
#R1 = 10_000.0
#R6 = 10_000.0
#P_R1 = (12.0**2)/R1
#P_R6 = (V_in_logic**2)/R6

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
    #["R1 (10k @12V)", P_R1],
    #["R6 (10k @5V)", P_R6],
]

df = pd.DataFrame(rows, columns=["Component / Mechanism", "Power_W"])
df["Power_mW"] = 1000*df["Power_W"]
df.loc["TOTAL"] = ["TOTAL", df["Power_W"].sum(), df["Power_mW"].sum()]

print(df.round(3))

efficiency= (5 - df.iloc[-1]["Power_W"])/5
print(f"{efficiency:.2%}","efficiency")
