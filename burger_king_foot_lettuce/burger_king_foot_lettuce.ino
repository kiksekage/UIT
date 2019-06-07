#include "SevSeg.h"
SevSeg sevseg; 

const int buttonPin = 10;
int buttonState = 0;
int intState = 0;
int numTests = 10;
bool pressed = false;

const int FSR_PIN = A0; // Pin connected to FSR/resistor divider
const int FSR_PIN1 = A1;
const int FSR_PIN2 = A2;
const int FSR_PIN3 = A3;
const int FSR_PIN4 = A4;
const int FSR_PIN5 = A5;
const int APINS [6] = { A0, A1, A2, A3, A4, A5 };

const int LED_PIN = 13;
const float VCC = 4.98; // Measured voltage of Ardunio 5V line
const float R_DIV = 4700.0; // Measured resistance of 3.3k resistor

void setup() 
{
  Serial.begin(9600);
  pinMode(FSR_PIN, INPUT);
  pinMode(FSR_PIN1, INPUT);
  pinMode(FSR_PIN2, INPUT);
  pinMode(FSR_PIN3, INPUT);
  pinMode(FSR_PIN4, INPUT);
  pinMode(FSR_PIN5, INPUT);
  pinMode(LED_PIN, OUTPUT);

  byte numDigits = 1;
  byte digitPins[] = {};
  byte segmentPins[] = {6, 5, 2, 3, 4, 7, 8, 9};
  bool resistorsOnSegments = true;

  byte hardwareConfig = COMMON_CATHODE; 
  sevseg.begin(hardwareConfig, numDigits, digitPins, segmentPins, resistorsOnSegments);
  sevseg.setBrightness(90);

  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT);

  sevseg.setNumber(0);
  sevseg.refreshDisplay();
}

void loop() 
{
  int fsrADC;
  bool _blink = false;
  
  for (int pin : APINS) {
    fsrADC = analogRead(pin);
    float force = 0.0;
    
    // If the FSR has no pressure, the resistance will be
    // near infinite. So the voltage should be near 0.
    if (fsrADC != 0) // If the analog reading is non-zero
    {
      // Use ADC reading to calculate voltage:
      float fsrV = fsrADC * VCC / 1023.0;
      
      // Use voltage and static resistor value to 
      // calculate FSR resistance:
      float fsrR = R_DIV * (VCC / fsrV - 1.0);
      //Serial.println("Resistance on sensor 0: " + String(fsrR) + " ohms");
      
      // Guesstimate force based on slopes in figure 3 of
      // FSR datasheet:
      float fsrG = 1.0 / fsrR; // Calculate conductance
      
      // Break parabolic curve down into two linear slopes:
      if (fsrR <= 600) 
        force = (fsrG - 0.00075) / 0.00000032639;
      else
        force =  fsrG / 0.000000642857;

      //digitalWrite(LED_PIN,HIGH);
    }

    Serial.print(pin); Serial.print(": "); Serial.print(force); Serial.print(" ");  
    _blink = true;
  }

  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);
    

  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == HIGH and !pressed) {
    pressed = true;
    intState = (intState+1)%numTests;
    sevseg.setNumber(intState);
    sevseg.refreshDisplay();
  }

  if(buttonState == LOW) {
    pressed = false;
  }
  
  if (_blink) {
    Serial.print("state: "); Serial.print(intState); Serial.print(" ");
    Serial.println("uT");
    //digitalWrite(LED_PIN,LOW);
  }
  delay(200);
}
