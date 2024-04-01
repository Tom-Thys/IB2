#include <Arduino.h>
#include "LedArray.h"

uint8_t count = 0b00000000;

LedArray::LedArray(uint8_t adress) {
    io = new Ioexpander(adress);
}

void LedArray::init() {
    io->init();
    io->set_conf_reg(TCA9554A_REG_3_OUTPUT);
}

void LedArray::turnPatternOn(uint8_t pattern) {
    //pattern: enkel de 5 MSB stellen voor van links naar rechts welke LEDs branden
    io->set_out_reg(pattern);
}

void LedArray::turnPatternOff(uint8_t pattern) {
    io->set_out_reg(~pattern);
}

void LedArray::turnAllOn() {
    io->set_out_reg(0b11111000);
}

void LedArray::turnAllOff() {
    io->set_out_reg(0b00000000);
}

void LedArray::cycle(uint8_t pattern, int delMs) {
    this->turnPatternOn(pattern);
    delay(delMs);
    this->turnPatternOff(pattern);
    delay(delMs);
}

void LedArray::counter(int delMs) {
    io->set_out_reg(count);
    delay(delMs);
    count += 0b00001000;
    if (count == 0b00000001) count = 0b00000000;
}