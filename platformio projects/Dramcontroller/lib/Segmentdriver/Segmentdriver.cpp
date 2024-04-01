#include <Arduino.h>
#include "Segmentdriver.h"

/*
0bXXXXXXXX: X1=punt, X2 = midden, X3 = linksboven, X4 = linksonder, X5 = onder, X6 = rechtsonder, X7 = rechtsboven, X8 = boven
(X1: actief hoog, X2-X7; actief laag)
actief laag allemaal
*/

Segmentdriver::Segmentdriver(uint8_t adress) {
    io = new Ioexpander(adress);
}

void Segmentdriver::init() {
    io->init();
    io->set_conf_reg(0x00);
}

void Segmentdriver::writeValue(int getal) {
    uint8_t outputByte;
    switch(getal) {
        case 0: outputByte = 0b11000000;break;
        case 1: outputByte = 0b11111001;break;
        case 2: outputByte = 0b10100100;break;
        case 3: outputByte = 0b10110000;break;
        case 4: outputByte = 0b10011001;break;
        case 5: outputByte = 0b10010010;break;
        case 6: outputByte = 0b10000010;break;
        case 7: outputByte = 0b11111000;break;
        case 8: outputByte = 0b10000000;break;
        case 9: outputByte = 0b10010000;break;
        default: outputByte = 0b11111111;break;
    }
    io->set_out_reg(outputByte);
}

void Segmentdriver::clear(){
    io->set_out_reg(0b01111111);
}