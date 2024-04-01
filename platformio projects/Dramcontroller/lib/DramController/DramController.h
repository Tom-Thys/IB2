#ifndef DramController_h
#define DramController_h

#include <Arduino.h>
#include "Segmentdriver.h"
#include "LedArray.h"


#define DISP_ADDR_1 0x3A
#define DISP_ADDR_2 0x39
#define LED_ARRAY_ADRESS 0x3B
#define SENSOR_SLOT_GPIO_3 0x38

#define BUZZER_PIN 2
#define VIBRATOR_1_PIN 12
#define VIBRATOR_2_PIN 5
#define DEBUG_LED_PIN 13
#define IO_EXPENDER_INT_PIN 11

#define LED_PIN_BUTTON_1 6
#define INPUT_PIN_BUTTON_1 14

class DramController {
    public:
        DramController();
        void init();
        void ledArrayTurnPatternOn(uint8_t pattern);
        void ledArrayTurnPatternOff(uint8_t pattern);
        void ledArrayTurnAllOff();
        void ledArrayTurnAllOn();
        void ledArrayCycle(uint8_t pattern, int delMs);
        void ledArrayCounter(int delMs);
        void segmWriteValue(int val);
        void leftSegmWriteValue(int val);
        void rightSegmWriteValue(int val);
    private:
        Segmentdriver* leftSegm;
        Segmentdriver* rightSegm;
        LedArray* ledArray;
};

#endif