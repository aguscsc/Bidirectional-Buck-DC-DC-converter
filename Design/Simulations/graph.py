import numpy as np
import matplotlib.pyplot as plt

# Parameters
A = 1.2
k = 15746.4  # 1/s
t = np.linspace(0, 0.001, 1000)  # 0 to 1 ms

# Function
icgs = A * np.exp(-k * t)

# Plot
plt.figure(figsize=(6,4))
plt.plot(t*1e3, icgs)  # convert time to ms for readability
plt.title("Gate-Source Capacitor Current i_CGS(t)")
plt.xlabel("Time [ms]")
plt.ylabel("i_CGS [A]")
plt.grid(True)
plt.show()
