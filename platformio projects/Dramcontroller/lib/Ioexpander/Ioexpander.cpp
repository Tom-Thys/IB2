#include <Arduino.h>
#include <Wire.h>
#include "Ioexpander.h"


Ioexpander::Ioexpander(uint8_t address){
    _address = address;
}
void Ioexpander::init() {
    Wire.begin();
}
void Ioexpander::set_conf_reg(uint8_t inp) {
    Wire.beginTransmission(_address);
    Wire.write(0x03);
    Wire.write(inp);
    Wire.endTransmission();
    SerialUSB.println("test voor ioexpander");
}
void Ioexpander::set_out_reg(uint8_t inp){
    Wire.beginTransmission(_address);
    Wire.write(0x01);
    Wire.write(inp);
    Wire.endTransmission();
}