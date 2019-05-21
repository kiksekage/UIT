const int FSR_PIN = A0; // Pin connected to FSR/resistor divider
const int FSR_PIN1 = A1;
const int FSR_PIN2 = A2;
const int LED_PIN1 = 13;
const float VCC = 4.98; // Measured voltage of Ardunio 5V line
const float R_DIV = 4700.0; // Measured resistance of 3.3k resistor

void setup() 
{
  Serial.begin(9600);
  pinMode(FSR_PIN, INPUT);
  pinMode(FSR_PIN1, INPUT);
  pinMode(FSR_PIN2, INPUT);
  pinMode(LED_PIN1, OUTPUT);
}

void loop() 
{
  int fsrADC = analogRead(FSR_PIN);
  int fsrADC1 = analogRead(FSR_PIN1);
  int fsrADC2 = analogRead(FSR_PIN2);
  
  // If the FSR has no pressure, the resistance will be
  // near infinite. So the voltage should be near 0.
  if (fsrADC != 0) // If the analog reading is non-zero
  {
    // Use ADC reading to calculate voltage:
    float fsrV = fsrADC * VCC / 1023.0;
    // Use voltage and static resistor value to 
    // calculate FSR resistance:
    float fsrR = R_DIV * (VCC / fsrV - 1.0);
    Serial.println("Resistance on sensor 0: " + String(fsrR) + " ohms");
    // Guesstimate force based on slopes in figure 3 of
    // FSR datasheet:
    float force;
    float fsrG = 1.0 / fsrR; // Calculate conductance
    // Break parabolic curve down into two linear slopes:
    if (fsrR <= 600) 
      force = (fsrG - 0.00075) / 0.00000032639;
    else
      force =  fsrG / 0.000000642857;
    if(force > 100) {
      Serial.println("Force on sensor 0: " + String(force) + " g");
      Serial.println();
      digitalWrite(LED_PIN1,HIGH);  
    }
  }
  if (fsrADC1 != 0)
  {
   // Use ADC reading to calculate voltage:
    float fsrV1 = fsrADC1 * VCC / 1023.0;
    // Use voltage and static resistor value to 
    // calculate FSR resistance:
    float fsrR1 = R_DIV * (VCC / fsrV1 - 1.0);
    Serial.println("Resistance on sensor 1: " + String(fsrR1) + " ohms");
    // Guesstimate force based on slopes in figure 3 of
    // FSR datasheet:
    float force1;
    float fsrG1 = 1.0 / fsrR1; // Calculate conductance
    // Break parabolic curve down into two linear slopes:
    if (fsrR1 <= 600) 
      force1 = (fsrG1 - 0.00075) / 0.00000032639;
    else
      force1 =  fsrG1 / 0.000000642857;
    if(force1 > 100) {
      Serial.println("Force on sensor 1: " + String(force1) + " g");
      Serial.println();
      digitalWrite(LED_PIN1,HIGH);  
    }
      
  }

  if (fsrADC2 != 0)
  {
   // Use ADC reading to calculate voltage:
    float fsrV2 = fsrADC2 * VCC / 1023.0;
    // Use voltage and static resistor value to 
    // calculate FSR resistance:
    float fsrR2 = R_DIV * (VCC / fsrV2 - 1.0);
    Serial.println("Resistance on sensor 2: " + String(fsrR2) + " ohms");
    // Guesstimate force based on slopes in figure 3 of
    // FSR datasheet:
    float force2;
    float fsrG2 = 1.0 / fsrR2; // Calculate conductance
    // Break parabolic curve down into two linear slopes:
    if (fsrR2 <= 600) 
      force2 = (fsrG2 - 0.00075) / 0.00000032639;
    else
      force2 =  fsrG2 / 0.000000642857;
    if(force2 > 100) {
      Serial.println("Force on sensor 2: " + String(force2) + " g");
      Serial.println();
      digitalWrite(LED_PIN1,HIGH);  
    }
    
      
  }

  if (fsrADC != 0 or fsrADC1 != 1 or fsrADC2 != 0) {
    delay(500);
    digitalWrite(LED_PIN1,LOW);
  }
}
