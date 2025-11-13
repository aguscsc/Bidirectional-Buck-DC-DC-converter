
// PIC32MZ2048EFM144 Configuration Bit Settings

// 'C' source line config statements

// DEVCFG3
#pragma config USERID = 0xFFFF          // Enter Hexadecimal value (Enter Hexadecimal value)
#pragma config FMIIEN = ON              // Ethernet RMII/MII Enable (MII Enabled)
#pragma config FETHIO = ON              // Ethernet I/O Pin Select (Default Ethernet I/O)
#pragma config PGL1WAY = ON             // Permission Group Lock One Way Configuration (Allow only one reconfiguration)
#pragma config PMDL1WAY = ON            // Peripheral Module Disable Configuration (Allow only one reconfiguration)
#pragma config IOL1WAY = ON             // Peripheral Pin Select Configuration (Allow only one reconfiguration)
#pragma config FUSBIDIO = ON            // USB USBID Selection (Controlled by the USB Module)

// DEVCFG2
#pragma config FPLLIDIV = DIV_1         // System PLL Input Divider (1x Divider)
#pragma config FPLLRNG = RANGE_8_16_MHZ // System PLL Input Range (8-16 MHz Input)
#pragma config FPLLICLK = PLL_POSC      // System PLL Input Clock Selection (POSC is input to the System PLL)
#pragma config FPLLMULT = MUL_30        // System PLL Multiplier (PLL Multiply by 30)
#pragma config FPLLODIV = DIV_2         // System PLL Output Clock Divider (2x Divider)
#pragma config UPLLFSEL = FREQ_24MHZ    // USB PLL Input Frequency Selection (USB PLL input is 24 MHz)

// DEVCFG1
#pragma config FNOSC = SPLL             // Oscillator Selection Bits (System PLL)
#pragma config DMTINTV = WIN_127_128    // DMT Count Window Interval (Window/Interval value is 127/128 counter value)
#pragma config FSOSCEN = OFF            // Secondary Oscillator Enable (Disable SOSC)
#pragma config IESO = OFF               // Internal/External Switch Over (Disabled)
#pragma config POSCMOD = EC             // Primary Oscillator Configuration (External clock mode)
#pragma config OSCIOFNC = OFF           // CLKO Output Signal Active on the OSCO Pin (Disabled)
#pragma config FCKSM = CSECME           // Clock Switching and Monitor Selection (Clock Switch Enabled, FSCM Enabled)
#pragma config WDTPS = PS1048576        // Watchdog Timer Postscaler (1:1048576)
#pragma config WDTSPGM = STOP           // Watchdog Timer Stop During Flash Programming (WDT stops during Flash programming)
#pragma config WINDIS = NORMAL          // Watchdog Timer Window Mode (Watchdog Timer is in non-Window mode)
#pragma config FWDTEN = OFF             // Watchdog Timer Enable (WDT Disabled)
#pragma config FWDTWINSZ = WINSZ_25     // Watchdog Timer Window Size (Window size is 25%)
#pragma config DMTCNT = DMT31           // Deadman Timer Count Selection (2^31 (2147483648))
#pragma config FDMTEN = OFF             // Deadman Timer Enable (Deadman Timer is disabled)

// DEVCFG0
#pragma config DEBUG = OFF              // Background Debugger Enable (Debugger is disabled)
#pragma config JTAGEN = ON              // JTAG Enable (JTAG Port Enabled)
#pragma config ICESEL = ICS_PGx1        // ICE/ICD Comm Channel Select (Communicate on PGEC1/PGED1)
#pragma config TRCEN = ON               // Trace Enable (Trace features in the CPU are enabled)
#pragma config BOOTISA = MIPS32         // Boot ISA Selection (Boot code and Exception code is MIPS32)
#pragma config FECCCON = OFF_UNLOCKED   // Dynamic Flash ECC Configuration (ECC and Dynamic ECC are disabled (ECCCON bits are writable))
#pragma config FSLEEP = OFF             // Flash Sleep Mode (Flash is powered down when the device is in Sleep mode)
#pragma config DBGPER = PG_ALL          // Debug Mode CPU Access Permission (Allow CPU access to all permission regions)
#pragma config SMCLR = MCLR_NORM        // Soft Master Clear Enable bit (MCLR pin generates a normal system Reset)
#pragma config SOSCGAIN = GAIN_2X       // Secondary Oscillator Gain Control bits (2x gain setting)
#pragma config SOSCBOOST = ON           // Secondary Oscillator Boost Kick Start Enable bit (Boost the kick start of the oscillator)
#pragma config POSCGAIN = GAIN_2X       // Primary Oscillator Gain Control bits (2x gain setting)
#pragma config POSCBOOST = ON           // Primary Oscillator Boost Kick Start Enable bit (Boost the kick start of the oscillator)
#pragma config EJTAGBEN = NORMAL        // EJTAG Boot (Normal EJTAG functionality)

// DEVCP0
#pragma config CP = OFF                 // Code Protect (Protection Disabled)

// SEQ3
#pragma config TSEQ = 0xFFFF            // Boot Flash True Sequence Number (Enter Hexadecimal value)
#pragma config CSEQ = 0xFFFF            // Boot Flash Complement Sequence Number (Enter Hexadecimal value)

// #pragma config statements should precede project file includes.
// Use project enums instead of #define for ON and OFF.

#include <xc.h>
#include <math.h>

/*the lines above is the code genereted for the configuration bits, most of them are the default ones, the ones to note 
 * are the FNOSC and all of the DEVCFG2 register, FNOSC selects our system clock, in this case we want it to be the output
 * of the PLL cause we want the highest clock possible for the best performance, since we can go up to 200Mhz, we decided
 * on 180MHz since its divisible by 60KHz target frecuency, therefore our input divider is 1, our mult is 30 and our output
 * divider is 2, certain restriccions have to be followed for the PLL to work properly like the output of the mult cant be 
 * higher than 700MHz for example.
 * PIC32MZ Embedded Connectivity with Floating Point Unit (EF) - pag 640 
*/



void PB3_setup(){
//setup for the peripheral bus clock 3, which is the one that the timers and OC use.
    
//unlock sequence to change de divisor of the clk for better resolution of our PWM, 
    
//Section 42. Oscillators with Enhanced PLL-pag 29 
       
SYSKEY = 0xAA996655;
SYSKEY = 0x556699AA;

PB3DIVbits.PBDIV = 0b0000000;

// closing of system unlock

SYSKEY = 0x33333333;       
}

void Timer2and3_setup(){
//setup for the timer 2, that will be used by our output compare module
//Section 14. Timers - pag 11
    
    T2CONbits.ON = 1;
    T2CONbits.TCKPS = 0b000;
    
//setup of the period register, the value is obtained via the formula to obtain the maximum resolution for our PWM
//the formula treated PR as x, FPWM as 60Khz, TPB as 1/180MHz and the prescale value as 1, therefore 2999 was obtained     
//PIC32 FRM Section 16. Output Compare - pag 28    
    
    PR2 = 2999;

    
//setup for the timer 3 that will be used by our ADC module
    
    T3CONbits.ON = 0;
    T3CONbits.TCKPS = 0b000;
    PR3 = 0xFFFF;
    T3CONbits.ON = 1;

}

void OC4_setup(){
//setup for the Output compare 4 module, it has to be either this one or the number 7, cause down the line we
//will have to map it to the pwm pin of the curiosity board
 
//setup the OCxR register before pwm mode pag 26
    // should be 1% duty cycle with our PR
    OC4R = 30;
    
//PIC32 FRM Section 16. Output Compare - pag 4
    
    OC4CONbits.ON = 1;
    //select timer 2 as source since timer 3 might be used for the ADC
    OC4CONbits.OCTSEL = 0;
    //select pwm mode without fault pin
    OC4CONbits.OCM = 0b110;
      
 // test
    OC4RS = 1500;

}

void ADC_setup(){
//setup for the ADC module, most of it is taken directly from code example of the datasheet
//12-bit High-Speed Successive Approximation Register (SAR) Analog-to-Digital Converter (ADC) - pag 66
//since we want to use a dedicated module ADC for class 1 (mainly because it seems easier to setup), we have to choose between
//AN0 to AN4, therefore we choose AN2 since its readily available on the cuirosity board without having to setup for of this god dam forsaken module 
//Curiosity PIC32MZ EF 2.0 Development Board Users Guide - pag 15 
    
    
    
//also we have to follow the activation sequence steps 
//PIC32MZ Embedded Connectivity with Floating Point Unit (EF) - pag 441    
    
    
//step 1 we initialize the calibration form de DEV registers
    
//PIC32MZ Embedded Connectivity with Floating Point Unit (EF) - pag 442
 ADC0CFG = DEVADC0;
 ADC1CFG = DEVADC1;
 ADC2CFG = DEVADC2;
 ADC3CFG = DEVADC3;
 ADC4CFG = DEVADC4;
 ADC7CFG = DEVADC7;    

 
//step 2 essential ADC configuration SFRs
 
 ADCCON1 = 0;
 ADCCON2 = 0; 

 ADCANCON = 0;
 ADCANCONbits.WKUPCLKCNT = 0xA; 

 ADCCON3 = 0;
 ADCCON3bits.ADCSEL = 0b00; // PB3CLK
 ADCCON3bits.CONCLKDIV = 0b000000; //idk why would we should or should not divide the input clock
 ADCCON3bits.VREFSEL = 0; // AVDD and AVSS wich are 3.3V and GND respectivly Curiosity PIC32MZ EF 2.0 Development Board Users Guide - pag 27

 ADC2TIMEbits.ADCDIV = 0b0000010; // divide the clock by 4 since the max TAD is 50Mhz, with this we get 45Mhz
 ADC2TIMEbits.SAMC = 0b0000000011; // ADC2 sampling time = 5 * TAD2, recomended for 1k resistance, honestly no clue what this value should be
 ADC2TIMEbits.SELRES = 0b11; // ADC2 resolution is 12 bits


 ADCTRGMODEbits.SH2ALT = 0; // ADC2 = AN2
 
 // AN2 will give unsiged bits, and since the medition will be against gnd we use single ended
 ADCIMCON1bits.SIGN2 = 0; // unsigned data format
 ADCIMCON1bits.DIFF2 = 0; // Single ended mode
 
 
 
 // No interrupts are used
 ADCGIRQEN1 = 0; 
 ADCGIRQEN2 = 0;
 // No scanning is used
 ADCCSS1 = 0; 
 ADCCSS2 = 0;
 // No digital comparators are used. Setting the ADCCMPCONx, register to '0' ensures that the comparator is disabled.
 ADCCMPCON1 = 0; 
 ADCCMPCON2 = 0; 
 ADCCMPCON3 = 0; 
 ADCCMPCON4 = 0;
 ADCCMPCON5 = 0;
 ADCCMPCON6 = 0;

 // No oversampling filters are used.
 ADCFLTR1 = 0; 
 ADCFLTR2 = 0;
 ADCFLTR3 = 0;
 ADCFLTR4 = 0;
 ADCFLTR5 = 0;
 ADCFLTR6 = 0;
 
 // No early interrupt
 ADCEIEN1 = 0; 
 ADCEIEN2 = 0;
 
 //The trigger source and how it triggers
 ADCTRGSNSbits.LVL0 = 0; // only on the positive edge of the trigger
 ADCTRG1bits.TRGSRC2= 0b00110; // we use timer 3 

 
 
 //step 3 turn on the adc
 ADCCON1bits.ON = 1;
 
 //step 4
 
 //Wait for voltage reference to be stable
 while(!ADCCON2bits.BGVRRDY); // Wait until the reference voltage is ready
 while(ADCCON2bits.REFFLT); // Wait if there is a fault with the reference voltage
 
 
 //step 5
 ADCANCONbits.ANEN2 = 1; // Enable the clock to analog bias
 
 
 //step 6
 while(!ADCANCONbits.WKRDY2); // Wait until ADC2 is ready
 
 //step 7 FINAL STEP FINALLY OMG
 //Digen bit is the one that enables the data conversion for the ADC
 ADCCON3bits.DIGEN2 = 1; // Enable ADC2
 
 
}

void IO_setup(){
//setup for the output of our OC module, since the board has RPD15 coneccted to the PWM pin of the mikrobus 1 and 2,
//we will map that pin to the output of a corresponding OC, therefore our only options were OC4 or OC7
//Curiosity PIC32MZ EF 2.0 Development Board Users Guide - pag 13
//PIC32MZ Embedded Connectivity with Floating Point Unit (EF) - pag 266

//set pin as output    
 TRISDbits.TRISD15 = 0;
// 1011 = OC4 
 RPD15Rbits.RPD15R = 0b1011;
 
//setup for the AN2 pin which is RB2 
 
 TRISBbits.TRISB2 = 1;
 ANSELBbits.ANSB2 = 1;

}

long map(long x, long in_min, long in_max, long out_min, long out_max) {
//this map functioin will be used to map the output of the adc to the available value range for the OCxRS register
//it was taken directly from arduino https://docs.arduino.cc/language-reference/en/functions/math/map/ 
    
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

//Author: Gian Luca Barbagelata, si esto funciona me vuelvo loco
int main(void) {
 
    PB3_setup();
    Timer2and3_setup();
    OC4_setup();
    ADC_setup();
    IO_setup();
    

    while(1){
        
    while (ADCDSTAT1bits.ARDY2 == 0);
      OC4RS = round(map(ADCDATA2,0,4096,0,2999));
      
     }  
        
    

    return (EXIT_SUCCESS);
    }