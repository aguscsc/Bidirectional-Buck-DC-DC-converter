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
  - \($I_{sat}$\) = Saturation current
  - \($B_{sat}$\) = saturation flux density of the core material
  - \($l$\) = effective magnetic path lenght of the core
  - \($\mu_{0}$\) = permeability of a vacuum
  - \($\mu_{r}$\) = relative permeability of the material
  - \($N$\) = number of turns

Recomendation: use coil64 to check your calculations, research skin effect and how different AWG interact with the frequency you're using (https://en.wikipedia.org/wiki/Skin_effect).
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
This section breaks down the process of prototyping and testing, the pcb in the design directory contains all the mesaures necessary to ensure the converter is working properly (value of components can be adjusted to your needs).
## BOM:
- 2 electrolytic capacitors $6.8\mu F$ and $2.2\mu F$ 50V each. 
- 2 ceramic capacitors (100nF).
- core T106-26 + 9m of AWG 26 cable (higher permeability would also work if the saturation stays sensible).
- 2 IFRZ44N (great for prototyping and testing)
- IR2184 driver (it can generate both MOSFET signals)
- 2 10 ohm gate resistors 1W (it limits the gate current)
- 2 10k ohm pulldown resistor 1W (drains the gate source capacitance)
 ![Prototype](pics/bucksito_labeled-min.jpg)
## Measurements and tests
### Conmutation
First, you ought to make sure the MOSFET are conmutating correctly. For this, turn on the pwm signal and your VCC source, then measure the pins gate-source of each MOSFET with an oscilloscope and make sure the signals are the complement of each other and respond to the change in duty. Aditionally, you should measure the gate current to ensure it is not exceeding the drivers capacity.
<p>
  <img src="pics/conmutate.jpeg" alt="conmutation" width="600"/>
</p>

<p>
  <img src="pics/gcurrent.png" alt="current" width="600"/>
</p>

### Powering the circuit
Check the waveforms of the inductor current and output voltage, ideally you should be looking at two saw-like waves with minimal ripple.
![testing](pics/oscilloscoping-min.jpg)
Once you have ensured the inductor current and the output voltage have satisfied your needs you can proceed to measure the converters effiency for each mode.

Note: if you struggle achieving the voltage ripple required, considering soldering ceramic capacitors paralell to your current ones.
### Efficiency 
**BUCK** R = $39.8$

| Duty | $V_{in}$ | $I_{in}$ | $V_{out}$ | $P_{in}$ | $P_{out}$ | Efficiency |
|:----:|:---------:|:---------:|:----------:|:---------:|:----------:|:-----------:|
| 35%  | 23 V | 0.06 A | 7.26 V | 1.38 W | 1.32 W | 96.4 % |
| 45%  | 23 V | 0.10 A | 9.45 V | 2.30 W | 2.24 W | 97.5 % |
| 55%  | 23 V | 0.16 A | 11.6 V | 3.68 W | 3.38 W | 91.8 % |
| 65%  | 23 V | 0.22 A | 13.78 V | 5.06 W | 4.77 W | 94.3 % |


**BOOST** R = $142.2$

| Duty | $V_{in}$ | $I_{in}$ | $V_{out}$ | $P_{in}$ | $P_{out}$ | Efficiency |
|:----:|:---------:|:---------:|:----------:|:---------:|:----------:|:-----------:|
| 29.5%  | 12 V | 0.16 A | 16.34 V | 1.92 W | 1.87 W | 97.7 % |
| 39.5%  | 12 V | 0.21 A | 18.79 V | 2.52 W | 2.48 W | 98.5 % |
| 49.5%  | 12 V | 0.30 A | 22.11 V | 3.60 W | 3.43 W | 95.4 % |
| 59.5%  | 12 V | 0.46 A | 26.77 V | 5.52 W | 5.04 W | 91.3 % |

# PWM control
Previously, the pwm signal was generated with a waveform generator, for real applications this has to be implemented with a microcontroller, in this case we'll use a PIC32 to generate the pwm signal.
This section will cover the programming and testing of the control system and its integration with the power circuit.

## ✅ TODO   
- [ ] PIC32 control
- [ ] pictures (gate current, under the board)
- [ ] graphic interface
- [ ] Firmware integration (ESP32 control)
- [ ] Final PCB
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
