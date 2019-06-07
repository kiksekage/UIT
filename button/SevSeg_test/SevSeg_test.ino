#include "SevSeg.h"
SevSeg sevseg; 

const int buttonPin = 10;     // the number of the pushbutton pin
const int ledPin =  13;      // the number of the LED pin

int buttonState = 0;
int intState = 0;
int numTests = 10;
bool pressed = false;

void setup(){
    byte numDigits = 1;
    byte digitPins[] = {};
    byte segmentPins[] = {6, 5, 2, 3, 4, 7, 8, 9};
    bool resistorsOnSegments = true;

    byte hardwareConfig = COMMON_CATHODE; 
    sevseg.begin(hardwareConfig, numDigits, digitPins, segmentPins, resistorsOnSegments);
    sevseg.setBrightness(90);

    // initialize the LED pin as an output:
    pinMode(ledPin, OUTPUT);
    // initialize the pushbutton pin as an input:
    pinMode(buttonPin, INPUT);

    Serial.begin(9600);

    sevseg.setNumber(intState);
    sevseg.refreshDisplay();
}

void loop(){
    // read the state of the pushbutton value:
    buttonState = digitalRead(buttonPin);
    

    // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
    if (buttonState == HIGH and !pressed) {
      pressed = true;
      intState = (intState+1)%numTests;
      sevseg.setNumber(intState);
      sevseg.refreshDisplay();
      // turn LED on:
      digitalWrite(ledPin, HIGH);
    } else {
      // turn LED off:
      digitalWrite(ledPin, LOW);
    }

    if(buttonState == LOW) {
      pressed = false;
    }
}
