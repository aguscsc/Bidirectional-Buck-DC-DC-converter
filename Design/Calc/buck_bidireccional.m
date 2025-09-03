%specs
frec=60000;
P_max=5;
%% duty
%buck
vinmin_buck=23;
vomax_buck=14;
dutymax_buck=vomax_buck/vinmin_buck;

%boost
vinmin_boost=12;
vomax_boost=27;
dutymax_boost=1-(vinmin_boost/vomax_boost);

%% inductor
il_max_buck=P_max/vomax_buck;
delta_il_buck=0.3*il_max_buck; %ripple de 30% para no tener un capacitor tan grande ni presentar discontinuidad
%buck
vl_buck=vinmin_buck-vomax_buck;
L_buck=(vl_buck*dutymax_buck)/(delta_il_buck*frec);
%boost
il_max_boost=P_max/vinmin_boost;
delta_il_boost=0.3*il_max_boost;
vl_boost=vinmin_boost;
L_boost=(vl_boost*dutymax_boost)/(delta_il_boost*frec);
%inductor final
inductor = max(L_boost,L_buck)

%Ipk
ipk_buck=il_max_buck+(delta_il_buck/2);
ipk_boost=il_max_boost+(delta_il_boost/2);
Il_satmin= round(2*max(ipk_boost,ipk_buck));
%% capacitor
% 5% de ripple
%buck
C_buck= (delta_il_buck)/(8*frec*0.01)
%buck
iout=5/27;
C_boost= (iout)/(frec*0.01)
%% vpulse
frec=60000;
gap = 200*10^(-9);
periodo = frec^(-1);
%buck
pw_buck=periodo*dutymax_buck-gap;
pw2_buck=periodo-pw_buck-gap;
%boost
pw_boost=periodo*dutymax_boost-gap;
pw2_boost=periodo-pw_boost-gap;

%% MOSFET calc


%% referencias

%   Mohan – Power Electronics, Cap. 7
%   Erickson – Fundamentals of Power Electronics, Cap. 3
%   Power Electronics: Converters, Applications, and Design” – Ned Mohan