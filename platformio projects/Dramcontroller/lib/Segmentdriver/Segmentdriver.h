#ifndef Segmentdriver_h
#define Segmentdriver_h

#include <Arduino.h>
#include "Ioexpander.h"


class Segmentdriver {
    public:
        Segmentdriver(uint8_t adress);
        void init();
        void writeValue(int getal);
        void clear();
    private:
        Ioexpander *io;
};

#endif