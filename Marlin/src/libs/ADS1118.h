/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2024 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

/**
 * A library for the Texas Instruments ADS1118 - 16-Bit Analog-to-Digital 
 * Converter with Internal Reference and Temperature Sensor
 * https://www.ti.com/product/ADS1118
 * 
 * This sensor uses SPI to communicate, 4 pins are required to interface.
 * 
 * ADS1118 Pinout:
 * ------------------------------------------------------
 * | Pin | Function   | Description                     |
 * ------------------------------------------------------
 * |  1  |  SCLK      | Serial clock input              |
 * |  2  |  CS        | Chip select; active low         |
 * |  3  |  GND       | Ground                          |
 * |  4  |  AIN0      | Analog input 0                  |
 * |  5  |  AIN1      | Analog input 1                  |
 * |  6  |  AIN2      | Analog input 2                  |
 * |  7  |  AIN3      | Analog input 3                  |
 * |  8  |  VDD       | Power supply                    |
 * |  9  |  DOUT/DRDY | Serial data output + data ready |
 * | 10  |  DIN       | Serial data input               |
 * ------------------------------------------------------
 * 
 * Written by Trace Bowes (@tracedgod) for Marlin 3D Printer Firmware
 * Copyright (c) 2024, Trace Bowes
 * All rights reserved.
 * 
 */
#pragma once

#define DEBUG_ADS1118

#include "../inc/MarlinConfig.h"
#include "../HAL/shared/Delay.h"
#include HAL_PATH(.., MarlinSPI.h)

/* "Reserved" flags */
#define ADS1118_RESERVED          0x01    // Value is always 1, reserved bit

/* "NOP" flags */
#define ADS1118_NOP_NO_WRITE_CFG  0x00    // Data will not be written to config register
#define ADS1118_NOP_WRITE_CFG     0x01    // Data will be written to config register

/* "PULL_UP_EN" flags */
#define ADS1118_DOUT_NO_PULLUP    0x00    // Internal pull-up resistor disabled
#define ADS1118_DOUT_PULLUP       0x01    // Internal pull-up resistor enabled *DEFAULT*

/* "TS_MODE" flags */
#define ADS1118_TS_MODE_ADC       0x00    // External voltage reading mode
#define ADS1118_TS_MODE_TEMP      0x01    // Internal temp sensor reading mode

/* "DR" flags */
#define ADS1118_DR_RATE_8SPS      0x00    // 8 samples/s, Tconv=125ms
#define ADS1118_DR_RATE_16SPS     0x01    // 16 samples/s, Tconv=62.5ms
#define ADS1118_DR_RATE_32SPS     0x02    // 32 samples/s, Tconv=31.25ms
#define ADS1118_DR_RATE_64SPS     0x03    // 64 samples/s, Tconv=15.625ms
#define ADS1118_DR_RATE_128SPS    0x04    // 128 samples/s, Tconv=7.8125ms
#define ADS1118_DR_RATE_250SPS    0x05    // 250 samples/s, Tconv=4ms
#define ADS1118_DR_RATE_475SPS    0x06    // 475 samples/s, Tconv=2.105ms
#define ADS1118_DR_RATE_860SPS    0x07    // 860 samples/s, Tconv=1.163ms

/* "MODE" flags */
#define ADS1118_MODE_CONTINUOUS   0x00    // Continuous conversion mode
#define ADS1118_MODE_SINGLE_SHOT  0x01    // Single-shot conversion & power down mode

/* "PGA" flags */
#define ADS1118_PGA_FSR_6144      0x00    // Range: ±6.144 v. LSB SIZE = 187.5μV
#define ADS1118_PGA_FSR_4096      0x01    // Range: ±4.096 v. LSB SIZE = 125μV
#define ADS1118_PGA_FSR_2048      0x02    // Range: ±2.048 v. LSB SIZE = 62.5μV *DEFAULT*
#define ADS1118_PGA_FSR_1024      0x03    // Range: ±1.024 v. LSB SIZE = 31.25μV
#define ADS1118_PGA_FSR_0512      0x04    // Range: ±0.512 v. LSB SIZE = 15.625μV
#define ADS1118_PGA_FSR_0256      0x07    // Range: ±0.256 v. LSB SIZE = 7.8125μV

/* "MUX" flags */
#define ADS1118_MUX_DIFF_0_1      0x00    // Differential input: Vin=A0-A1
#define ADS1118_MUX_DIFF_0_3      0x01    // Differential input: Vin=A0-A3
#define ADS1118_MUX_DIFF_1_3      0x02    // Differential input: Vin=A1-A3
#define ADS1118_MUX_DIFF_2_3      0x03    // Differential input: Vin=A2-A3
#define ADS1118_MUX_AIN_0         0x04    // Single ended input: Vin=A0
#define ADS1118_MUX_AIN_1         0x05    // Single ended input: Vin=A1
#define ADS1118_MUX_AIN_2         0x06    // Single ended input: Vin=A2
#define ADS1118_MUX_AIN_3         0x07    // Single ended input: Vin=A3

/* "SS" flags */
#define ADS1118_SS_START_NOW      0x01    // Start conversion in single-shot mode

/* Config Register Union for ADS1118 Sensor */
union ADS1118Config {
  struct {
    uint8_t reserved:1;       // "Reserved" bit
    uint8_t noOperation:2;    // "NOP" bits
    uint8_t pullUp:1;         // "PULL_UP_EN" bit
    uint8_t sensorMode:1;     // "TS_MODE" bit
    uint8_t rate:3;           // "DR" bits
    uint8_t operatingMode:1;  // "MODE" bit
    uint8_t pga:3;            // "PGA" bits
    uint8_t mux:3;            // "MUX" bits
    uint8_t singleStart:1;    // "SS" bit
  } bits;

  uint16_t word;    // Representation in word (16-bits) format

  struct {
    uint8_t lsb;              // "LSB" byte
    uint8_t msb;              // "MSB" byte
  } byte;          // Representation in bytes (8-bits) format
};

/**
 * @brief Class representing the Texas Instruments ADS1118 ADC Sensor chip
 */
class ADS1118 {
private:
  static SPISettings spiConfig;

  uint8_t sclkPin, misoPin, mosiPin, cselPin;

  uint8_t lastSensorMode = 3;   // Last sensor mode selected ("ADC_MODE", "TEMP_MODE" or none)

  const float pgaFSR[8] = {6.144, 4.096, 2.048, 1.024, 0.512, 0.256, 0.256, 0.256};
  const uint8_t CONV_TIME[8]={125, 63, 32, 16, 8, 4, 3, 2}; 	// Array containing the conversions time in ms

  void setSampleRate(uint8_t rate);
  void setFSR(uint8_t fsr);
  void setInputSelected(uint8_t input);
  void setOperatingMode(uint8_t mode);
  void setPullUpMode(uint8_t mode);

  uint16_t getADCValue(uint8_t input);
  bool getADCValueNoWait(uint8_t pin_drdy, uint16_t &value);
  
  double getMilliVolts(uint8_t inputs);
  bool getMilliVoltsNoWait(uint8_t pin_drdy, double &volts);

  void spiBeginTransaction();
  void spiEndTransaction();

public:
  ADS1118(uint8_t spi_cs);
  ADS1118(uint8_t spi_cs, uint8_t spi_mosi, uint8_t spi_miso, 
          uint8_t spi_clk);

  void begin();

  uint16_t readRaw();
  float temperature();

  union ADS1118Config configRegister;
};