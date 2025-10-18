# Bidirectional Buck DC-DC Converter

This repository documents the design and implementation of a **bidirectional DC-DC converter**.  
The system can operate in both **buck mode** (step-down) and **boost mode** (step-up), enabling power flow in both directions.  

---
## Software used
- **Simulation**
  
   Multisim, Ltspice and MATLAB/Simulink
   coil64
- **PCB**
  
   Kicad
## 📐 Specifications
- **Switching frequency**: 60 kHz  
- **Maximum power**: 5 W  

### Buck Mode
- $V_{in, min} = 23V$  
- $V_{out, max} = 14V$  

### Boost Mode
- $V_{in, min} = 12V$  
- $V_{out, max} = 27V$  

---

## 🔌 Topology
The selected topology is based on a **bidirectional synchronous buck/boost converter**.  
Diagram (preliminary):  

![Topology](pics/topology.png)

---

## 📊 Design Parameters
### Inductor
- To be dimensioned based on:  
 $L = \frac{V_L \cdot D}{\Delta I_L \cdot f_s}$
  where:
  - \( $V_L$ \) = inductor voltage  
  - \( $D$ \) = duty cycle  
  - \( $\Delta I_L$ \) = current ripple (≈ $30$% of \( $I_{L,max}$ \))  
  - \( $f_s$ \) = switching frequency
  
   $I_{sat} = \frac{B_{sat}\cdot l}{\mu_{0}\cdot \mu_{r}\cdot N}$
  Where:
  - \(I_{sat}\) = Saturation current
  - \(B_{sat}\) = saturation flux density of the core material
  - \(l\) = effective magnetic path lenght of the core
  - \(\mu_{0}\) = permeability of a vacuum
  - \(\mu_{r}\) = relative permeability of the material
  - \(N\) = number of turns

### Capacitor
- To be dimensioned from capacitor current balance:
- buck
  $C = \frac{\Delta I_L}{\Delta V \cdot f_s\cdot 8}$
- boost
  $C = \frac{I_{out} \cdot D}{\Delta V \cdot f_s}$
  
  where:
  - \( $\Delta V$ \) = allowed voltage ripple  

## Schematic & PCB layout
<p>
  <img src="pics/kicad_ss.png" alt="schematic" width="600"/>
</p>

<p>
  <img src="pics/pcb_ss.png" alt="PCB" width="600"/>
</p>

---
# Prototyping 
This section breaksdown the process of prototyping and testing, the pcb in the design directory contains all the mesaures necessary to ensure the converter is working properly (value of components can be adjusted to your needs).
## BOM:
- 2 electrolytic capacitors $6.8\mu F$ and $2.2\mu F$ 50V each. 
- 2 ceramic capacitors (100nF).
- core T106-26 + 9m of AWG 26 cable (higher permeability would also work if the saturation stays sensible).
- 2 IFRZ44N (great for prototyping and testing)
- IR2184 driver (it can generate both MOSFET signals)
- 2 10 ohm gate resistors 1W (it limits the gate current)
- 2 10k ohm pulldown resistor 1W (drains the gate source capacitance)

## ✅ TODO   
- [ ] PIC32 control
- [ ] graphic interface
- [ ] Firmware integration (ESP32 control)  
- [ ] Experimental validation
---

## 👥 Collaborators
- **[Agustín Torres](\ https://github.com/aguscsc \)**  
- **[Ignacio Cerda](\ https://github.com/LovesCharlie \)**  
- **[Gian Luca Barbagelata](\ https://github.com/Yian-n \)**  

---

## 📚 References
-   Mohan – Power Electronics, Cap. 7
-   Erickson – Fundamentals of Power Electronics, Cap. 3
-   Power Electronics: Converters, Applications, and Design” – Ned Mohan
-   Electronica de Potencia, 1era edicion - Daniel W.Hart
