22222222222222222// This variable will hold the duty cycle sent from Python
float dutyCycle = 0.0;
// This variable will hold the mode (1 = BUCK, 0 = BOOST)
int mode = 1;

void setup() {
  // Start the serial port.
  // This baud rate MUST match the one in your Python script (115200).
  Serial.begin(115200);
  
  // Send a "ready" message back to the computer's log.
  Serial.println("Arduino Nano is ready. Send commands.");
}

void loop() {
  // Check if any data has arrived in the serial buffer
  if (Serial.available() > 0) {
    
    // 1. Read all bytes until a newline ('\n') is found
    // This matches the '\n' you send from Python.
    String command = Serial.readStringUntil('\n');
    command.trim(); // Clean up any extra whitespace

    // 2. Check if the command starts with our "D:" prefix
    if (command.startsWith("D:")) {
      
      // 3. Get the value part of the string
      // Example: "D:50.5" -> substring(2) -> "50.5"
      String valueString = command.substring(2);
      
      // 4. Convert the value string to a floating-point number
      dutyCycle = valueString.toFloat();

      // --- This is where you would use the value ---
      // For an Arduino Nano, the PWM pins are 0-255
      // To convert 0-100% to 0-255, we multiply by 2.55
      int pwmValue = (int)(dutyCycle * 2.55);
      analogWrite(3, pwmValue); // Example: Send to pin D3
      
      // 5. Send an "Acknowledgment" message back to Python
      Serial.print("ACK: Duty cycle set to ");
      Serial.println(dutyCycle);
    }
    } 
}