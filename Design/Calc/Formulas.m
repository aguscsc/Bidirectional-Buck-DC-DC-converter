%% Especificaciones y valores de diseño
fc=60000;
Pmax=5;


%% Modo Buck
V_imax=24;
V_omin=14;
R_carga=(V_omin)^2/Pmax; %39.5 Ohm
I_out=Pmax/V_omin;       % 0.375 A
Rizz_I=100*10^-3;        % rizado de un 28% aproximadamente
% Obtención de Duty cycle

%Analsis transitorio
% Mosfet 1 en conduccion y mosfet 2 abierto
V_inductor = V_imax-V_omin; % Con V_inductor=L*di_L/dt
delta_iL_mosfet1=V_inductor*D*T/L;
%Mosfet 2 en conduccion y mosfet 1 abierto
V_inductor=-V_omin;
delta_iL_mosfet2=-V_omin*(1-DT)/L;

%Analisis estable

delta_iL_mosfet1+delta_iL_mosfet2=0;
%Remplazando con los calculos previos se obtiene

Duty_buck=V_omin/V_imax; % Duty cycle para buck es de 60.8%

% Calculo del inductor en modo buck

L= V_inductor*D*T/delta_iL_mosfet1; % 1mH como valor comercial

%Calculo del capacitor
delta_q=delta_V*C_buck;
delta_q=Rizz_I*T/8; % obtenida de 1/2*base*altura

%Remplazando para obtener el valor del capacitor del modo buck

C_buck=Rizz_I/(8*fc*V_omin)




