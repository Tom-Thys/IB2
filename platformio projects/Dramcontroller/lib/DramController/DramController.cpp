#include <Arduino.h>
#include "DramController.h"

DramController::DramController() {
    leftSegm = new Segmentdriver(DISP_ADDR_1);
    rightSegm = new Segmentdriver(DISP_ADDR_2);
    ledArray = new LedArray(LED_ARRAY_ADRESS);
}

void DramController::init() {
    ledArray->init();
    leftSegm->init();
    rightSegm->init();
}

void DramController::ledArrayTurnPatternOn(uint8_t pattern) {
    ledArray->turnPatternOn(pattern);
}

void DramController::ledArrayTurnPatternOff(uint8_t pattern) {
    ledArray->turnPatternOff(pattern);
}

void DramController::ledArrayTurnAllOn() {
    ledArray->turnAllOn();
}

void DramController::ledArrayTurnAllOff() {
    ledArray->turnAllOff();
}

void DramController::ledArrayCounter(int delMs) {
    ledArray->counter(delMs);
}

void DramController::segmWriteValue(int val) {
    int val1 = val%10;
    int val2 = floor((val - val1)/10);

    leftSegm->writeValue(val2);
    rightSegm->writeValue(val1);
}

void DramController::leftSegmWriteValue(int val) {
    leftSegm->writeValue(val);
}

void DramController::rightSegmWriteValue(int val) {
    rightSegm->writeValue(val);
}