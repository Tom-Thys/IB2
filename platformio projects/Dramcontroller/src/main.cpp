#include <Arduino.h>
#include <Wire.h>
#include "Ioexpander.h"
#include "Segmentdriver.h"
#include "LedArray.h"
#include "DramController.h"

#include "HID-Project.h"
#include "Adafruit_MPR121.h"

//test
#ifndef _BV
#define _BV(bit) (1 << (bit))
#endif


DramController *dramController = new DramController();
//test
Adafruit_MPR121 cap = Adafruit_MPR121();
uint16_t lasttouched = 0;
uint16_t currtouched = 0;

char ingelezen;

bool press_e = false;

void reageerKnop1() {
  if (press_e) {press_e = false; digitalWrite(LED_PIN_BUTTON_1,LOW);}
  else {press_e = true; digitalWrite(LED_PIN_BUTTON_1,HIGH);}
}

void setup() {
  // Initialiseren
  SerialUSB.begin(115200);
  Wire.begin();
  dramController->init();
  Keyboard.begin();
  // pinModes
  pinMode(DEBUG_LED_PIN,OUTPUT);
  pinMode(LED_PIN_BUTTON_1, OUTPUT);
  pinMode(INPUT_PIN_BUTTON_1, INPUT_PULLUP);
  pinMode(BUZZER_PIN,OUTPUT);
  pinMode(VIBRATOR_1_PIN,OUTPUT);
  pinMode(VIBRATOR_2_PIN,OUTPUT);
  // Beginwaarden
  SerialUSB.println("Opstarten");
  dramController->segmWriteValue(00);
  dramController->ledArrayTurnAllOff();
  // Interrupts
  attachInterrupt(digitalPinToInterrupt(INPUT_PIN_BUTTON_1),reageerKnop1, CHANGE);
  //test
  if (!cap.begin(0x5A)) {
    while (1) {
      SerialUSB.println("MPR121 not found, check wiring?");
      delay(250);
    }
  } SerialUSB.println("MPR121 found");
}

void loop() {
  //test
  currtouched = cap.touched();
  for (uint8_t i = 0; i < 12; i++) {
    // it if *is* touched and *wasnt* touched before, alert!
    if ((currtouched & _BV(i)) && !(lasttouched & _BV(i)) ) {
      SerialUSB.print(i); SerialUSB.print("  touched");
    }
    // if it *was* touched and now *isnt*, alert!
    if (!(currtouched & _BV(i)) && (lasttouched & _BV(i)) ) {
      SerialUSB.println("         released");
    }
  }
  // reset our state
  lasttouched = currtouched;
  
  // Keyboard handling
  if (press_e){
    Keyboard.press('e');
  } else {
    Keyboard.release('e');
  }

  // read serial input
  while (SerialUSB.available()) {
    ingelezen = SerialUSB.read();
    SerialUSB.write(ingelezen);
    int tijd1 = millis();
    while (ingelezen == '1') {
      digitalWrite(BUZZER_PIN, HIGH);
      if (millis() - tijd1 > 200) {
        digitalWrite(BUZZER_PIN,LOW);
        break;
      }
    }
    while(ingelezen == '2') {
      digitalWrite(VIBRATOR_1_PIN,HIGH);
      digitalWrite(VIBRATOR_2_PIN,HIGH);
      if (millis() - tijd1 > 150) {
        digitalWrite(VIBRATOR_1_PIN,LOW);
        digitalWrite(VIBRATOR_2_PIN,LOW);
        break;
      }
    }
    if (ingelezen == 'S') {
      while (SerialUSB.available()) {
        char ingelezen2 = SerialUSB.read();
        char ingelezen3 = SerialUSB.read();
        int val = ingelezen2 - 48;
        int val2 = ingelezen3 - 48;
        dramController->rightSegmWriteValue(val2);
        dramController->leftSegmWriteValue(val);
      }
    }
  }

}
