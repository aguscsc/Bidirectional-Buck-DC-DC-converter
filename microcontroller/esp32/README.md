# ADC
The microcontroller ESP32 integrates a 12-bit SAR ADCs and supports measurements on 18 channels. The ULP-coprocessor in ESP32 is also designed to measure voltage, while operating in the sleep mode, which enables low-power consumptiun. The CPU can be wolen up by a threshold setting and/or via other triggers.

**DNL (differential nonlinearity) & INL (integral nonlinearity):**
The readings of the ESP32 can fluctuate up to 12 LSB from the actual value, this means 12 "steps" (about 10 to 15 milivolts). This can be aid cnnected to an external 100nF capacitor , dropping the fluctuation to only 7 LSB. Adittionally, instead of taking every measure, it is recommended to define a sample size and display the avg value of those readings.

**DIG vs RTC**
The dig controller reffers to the continous mode of the adc, taking up to 2 million samples per second, this fills the buffer incredibly fast, causing some delay when displaying the readings to the monitor.

The RTC operates in a One-shot mode, it captures 200 thousand samples per second, this is still really fast for a voltage sensor.

**Attenuation** 
The trade off to consider while choosing the attenuation value is range for accuracy. In this case, the best option is $Atten = 3$, yielding an effective range of 150 to 2450 milivolts and a max error of 60 milivolts


