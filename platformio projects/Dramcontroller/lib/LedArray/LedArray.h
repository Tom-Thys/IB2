#ifndef LedArray_h
#define LedArray_h

#include <Arduino.h>
#include "Ioexpander.h"

#define TCA9554A_REG_3_OUTPUT 0b00000000

class LedArray {
    public:
        LedArray(uint8_t adress);
        void init();
        void turnPatternOn(uint8_t pattern);
        void turnPatternOff(uint8_t pattern);
        void turnAllOff();
        void turnAllOn();
        void cycle(uint8_t pattern, int delMs);
        void counter(int delMs);
    private:
        Ioexpander *io;
};



#endif