# Compute power-loss breakdown with reasonable assumptions and save a CSV the user can edit.
import pandas as pd

# Buck mode
Vin = 23.0
Vo = 14.0
fs = 60_000.0
D = 0.609
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
R_L_DCR = 0.30        # Inductor DCR (Ohm) assumption
ESR_out = 0.20        # Output cap ESR (Ohm) assumption (THT electrolytic/small film)
ESR_in = 1.00         # Input cap ESR (Ohm) assumption (small radial electrolytic)
Vf_boot = 0.30        # Bootstrap Schottky forward drop
IQCC = 1.0e-3         # IR2184 quiescent CC
IQBS = 60e-6          # IR2184 bootstrap quiescent
R_g_HS = 10.0         # Gate resistor HS
R_g_LS = 10.0         # Gate resistor LS
R_drv_equiv = 10.0    # Approx driver output resistance, to split gate loss
R_pull = 10_000.0     # R4, R5
V_in_logic = 5.0      # PWM logic level for R6 (approx)

# Helper currents
ICout_rms = diL/(2*(3**0.5))
ICin_rms = Iout*(D*(1-D))**0.5

# MOSFET losses 
P_HS_cond = (D**0.5*IL_rms)**2 * Rds_on_typ
P_LS_cond = ((1-D)**0.5*IL_rms)**2 * Rds_on_typ
P_HS_sw = 0.5*Vin*Iout*tr_tf*fs
P_LS_dt = 2*Iout*Vf_body*t_dead*fs

# Gate-drive total per FET
Pg_per_fet = Qg*Vgs*fs
# Split between resistor and driver using ratio Rg / (Rg + Rdrv)
split_HS_R = R_g_HS/(R_g_HS + R_drv_equiv)
split_LS_R = R_g_LS/(R_g_LS + R_drv_equiv)

P_Rg_HS = Pg_per_fet * split_HS_R
P_Rg_LS = Pg_per_fet * split_LS_R
P_drv_gates = Pg_per_fet*(1-split_HS_R) + Pg_per_fet*(1-split_LS_R)  # both FETs

# Pull-down resistors (gate-to-source 10k)
P_R4 = D * (Vgs**2)/R_pull
P_R5 = (1-D) * (Vgs**2)/R_pull

# Driver quiescent and bootstrap diode
P_drv_iq = Vgs*(IQCC + IQBS)
I_boot_avg = Qg*fs + IQBS
P_boot_diode = Vf_boot * I_boot_avg

# Inductor & capacitors
P_L_cu = IL_rms**2 * R_L_DCR
P_Cout = ICout_rms**2 * ESR_out
P_Cin = ICin_rms**2 * ESR_in

# Small signal resistors (R1 from 12V to ???; R6 to GND on 5V input)
# We will assume R1 is across 12V (worst-case), R6 across 5V.
R1 = 10_000.0
R6 = 10_000.0
P_R1 = (12.0**2)/R1
P_R6 = (V_in_logic**2)/R6

rows = [
    ["HS MOSFET conduction", P_HS_cond],
    ["LS MOSFET conduction", P_LS_cond],
    ["HS MOSFET switching", P_HS_sw],
    ["LS body diode (deadtime)", P_LS_dt],
    ["Gate resistor (HS)", P_Rg_HS],
    ["Gate resistor (LS)", P_Rg_LS],
    ["Driver gate power (split)", P_drv_gates],
    ["Driver quiescent (IQCC+IQBS)", P_drv_iq],
    ["Bootstrap diode D4", P_boot_diode],
    ["Inductor copper (DCR)", P_L_cu],
    ["Output cap ESR (C2)", P_Cout],
    ["Input cap ESR (C1)", P_Cin],
    ["Pull-down R4 (10k)", P_R4],
    ["Pull-down R5 (10k)", P_R5],
    ["R1 (10k @12V)", P_R1],
    ["R6 (10k @5V)", P_R6],
]

df = pd.DataFrame(rows, columns=["Component / Mechanism", "Power_W"])
df["Power_mW"] = 1000*df["Power_W"]
df.loc["TOTAL"] = ["TOTAL", df["Power_W"].sum(), df["Power_mW"].sum()]

print(df.round(3))

efficiency= (5 - df.iloc[-1]["Power_W"])/5
print(efficiency,"efficiency")
# Save CSV
#path = "~/Desktop/buck_loss_breakdown_assumptions.csv"
#df.to_csv(path, index=False)
#path
