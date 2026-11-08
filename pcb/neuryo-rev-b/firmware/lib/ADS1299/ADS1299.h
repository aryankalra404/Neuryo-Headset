/*
ADS1299 Library for ESP32-S3
Originally created by: Conor Russomanno (https://github.com/conorrussomanno/ADS1299)
Modified by: Xavier Asghar
Modifications include:
 - Replaces ATmega328P SPI implementation with Arduino's built-in SPI library
 - Changes updateData function to be called from an ISR rather than polled from the main loop
 - updateData now returns a integer long rather than printing to the serial monitor
 - Adds updateDataPacket function that drops data directly into a numbered byte array to be sent over bluetooth
Neuryo rev B changes (2026-11-08):
 - RESET_PIN / START_PIN may be -1 (rev B has no GPIO on them: RESET is pulled up, START is pulled down);
   setup() then uses the RESET command instead of the pin
 - release() returns SCLK, MOSI and CS to high-impedance inputs, for when the ADS1299 is unpowered (USB present)
 - RREG/WREG print only when ADS1299_VERBOSE is defined
*/

#ifndef ADS1299_h
#define ADS1299_h

#include <Arduino.h>
#include <SPI.h>
#include "ADS1299_Definitions.h"

class ADS1299 {
public:
    
    void setup(int _DRDY_PIN, int _CS_PIN, int SCK_PIN, int _MISO_PIN, int _MOSI_PIN, int _RESET_PIN, int _START_PIN);
    
    //ADS1299 SPI Command Definitions (Datasheet, Pg. 35)
    //System Commands
    void WAKEUP();
    void STANDBY();
    void RESET();
    void START();
    void STOP();
    
    //Data Read Commands
    void RDATAC();
    void SDATAC();
    void RDATA();
    
    //Register Read/Write Commands
    uint8_t RREG(byte _address);
    void WREG(byte _address, byte _value); //
    
    void release();      // SCLK, MOSI, CS -> inputs (no drive into an unpowered ADS1299)

    void updateData();
    void updateDataPacket(uint8_t *dataPacket);
    
    float tCLK, tSDECODE, scaleFactorUV;
    int DRDY_PIN, CS_PIN, SCK_PIN, MISO_PIN, MOSI_PIN, RESET_PIN, START_PIN; 
    
    int outputCount;
    
};

#endif