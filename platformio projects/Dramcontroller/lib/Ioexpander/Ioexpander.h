#ifndef Ioexpander_h
#define Ioexpander_h

#include <Arduino.h>


class Ioexpander {
    public:
        Ioexpander(uint8_t address);
        void init();
        void set_conf_reg(uint8_t inp);
        void set_out_reg(uint8_t inp);
    private:
        uint8_t _address;
};

#endif