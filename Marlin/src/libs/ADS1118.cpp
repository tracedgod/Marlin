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

#if HAS_ADS1118

#include "ADS1118.h"

#define DEBUG_OUT ENABLED(DEBUG_ADS1118)
#include "../core/debug_out.h"

// Todo: Maximum speed the ADS1118 can do is 4 MHz, change to TERN for flexibility of supported HALs
SPISettings ADS1118::spiConfig = SPISettings(
  400000,
  MSBFIRST,
  SPI_MODE1 // CPOL0 CPHA1
);

#define ADS1118_CS_H() OUT_WRITE(ADS1118_CS_PIN, HIGH)
#define ADS1118_CS_L() OUT_WRITE(ADS1118_CS_PIN, LOW)

/**
 * @brief Construct a new ADS1118 interface object using software SPI
 * 
 * @param spi_cs    the SPI CS pin to use
 * @param spi_mosi  the SPI MOSI pin to use
 * @param spi_miso  the SPI MISO pin to use
 * @param spi_clk   the SPI clock pin to use
 */
ADS1118::ADS1118(uint8_t spi_cs, uint8_t spi_mosi, uint8_t spi_miso, uint8_t spi_clk) {
  cselPin = spi_cs;
  mosiPin = spi_mosi;
  misoPin = spi_miso;
  sclkPin = spi_clk;
}

/**
 * @brief Construct a new ADS1118 interface object using hardware SPI
 * 
 * @param spi_cs  the SPI CS pin to use along with the default SPI device
 */
ADS1118::ADS1118(uint8_t spi_cs) {
  cselPin = spi_cs;
  sclkPin = misoPin = mosiPin = -1;
}

/**
 * @brief Initialize the SPI interface for ADS1118 object
 * 
 */
void ADS1118::begin() {
  ADS1118_CS_H();

  DEBUG_ECHOLNPGM("Init ADS1118 SPI");
  SPI.begin();

  configRegister.bits = {
            ADS1118_RESERVED, 
            ADS1118_NOP_WRITE_CFG,
            ADS1118_DOUT_PULLUP,
            ADS1118_TS_MODE_ADC,
            ADS1118_DR_RATE_8SPS,
            ADS1118_MODE_SINGLE_SHOT,
            ADS1118_PGA_FSR_0256,
            ADS1118_MUX_DIFF_0_1,
            ADS1118_SS_START_NOW 
  };
  DEBUG_ECHOLNPGM("ADS1118: Config regs: ", configRegister.bits);
}

/**
 * @brief 
 * 
 * @return uint16_t 
 */
uint16_t ADS1118::readRaw() {
  // todo
}

/**
 * @brief 
 * 
 * @return float 
 */
float ADS1118::temperature() {

}

/**
 * @brief Set the sample rate in config register
 * 
 * @param rate  Desired sample rate value
 */
void ADS1118::setSampleRate(uint8_t rate) {
  configRegister.bits.rate = rate;
  DEBUG_ECHOLNPGM("ADS1118: DR reg change: ", configRegister.bits.rate);
}

/**
 * @brief Set the Full Scale Range in config register
 * 
 * @param fsr Desired FSR value
 */
void ADS1118::setFSR(uint8_t fsr) {
  configRegister.bits.pga = fsr;
  DEBUG_ECHOLNPGM("ADS1118: PGA reg change: ", configRegister.bits.pga);
}

/**
 * @brief Set the Inputs to be acquired in config register
 * 
 * @param input 
 */
void ADS1118::setInputSelected(uint8_t input) {
  configRegister.bits.mux = input;
  DEBUG_ECHOLNPGM("ADS1118: MUX reg change: ", configRegister.bits.mux);
}

/**
 * @brief Sets the Operating Mode to Continuous or Single Shot in config register
 * 
 * @param mode  Desired Operating Mode value
 */
void ADS1118::setOperatingMode(uint8_t mode) {
  switch(mode) {
    case ADS1118_MODE_CONTINUOUS:
      configRegister.bits.operatingMode = ADS1118_MODE_CONTINUOUS;
    case ADS1118_MODE_SINGLE_SHOT:
      configRegister.bits.operatingMode = ADS1118_MODE_SINGLE_SHOT;
  }

  DEBUG_ECHOLNPGM("ADS1118: MODE reg change: ", configRegister.bits.operatingMode);
}

/**
 * @brief Sets the Pull Up Resistor to Enabled or Disabled in config register
 * 
 * @param mode  Desired Pull Up Resistor mode value
 */
void ADS1118::setPullUpMode(uint8_t mode) {
  switch(mode) {
    case ADS1118_DOUT_NO_PULLUP:
      configRegister.bits.pullUp = ADS1118_DOUT_NO_PULLUP;
    case ADS1118_DOUT_PULLUP:
      configRegister.bits.pullUp = ADS1118_DOUT_PULLUP;
  }

  DEBUG_ECHOLNPGM("ADS1118: PULL_UP_EN reg change: ", configRegister.bits.pullUp);
}

/**
 * @brief Gets a sample from specified input
 * 
 * @param input   The desired input of the ADC
 * @return ADC value
 */
uint16_t ADS1118::getADCValue(uint8_t input) {
  uint16_t value;
  byte dataMSB, dataLSB, configMSB, configLSB, count = 0;
  if (lastSensorMode == ADS1118_TS_MODE_ADC) {
    count = 1;
  } else {
    configRegister.bits.sensorMode = ADS1118_TS_MODE_ADC;
    configRegister.bits.mux = input;
  }

    spiBeginTransaction();

    dataMSB = SPI.transfer(configRegister.byte.msb);
    dataLSB = SPI.transfer(configRegister.byte.lsb);
    configMSB = SPI.transfer(configRegister.byte.msb);
    configLSB = SPI.transfer(configRegister.byte.lsb);

    spiEndTransaction();

    for (int i=0;i<CONV_TIME[configRegister.bits.rate];i++) {
      DELAY_US(1000);
      count++;
    } 
    while (count <= 1) {
      value = (dataMSB << 8) | (dataLSB);
    }
    
    return value;
}

/**
 * @brief 
 * 
 * @param pin_drdy  IO pin connected to ADS1118 DOUT/DRDY
 * @param value     Reference of ADC value to be fetched
 * @return true     ADC data is ready
 * @return false    ADC data is not ready
 */
bool ADS1118::getADCValueNoWait(uint8_t pin_drdy, uint16_t &value) {
  byte dataMSB, dataLSB;
  spiBeginTransaction();

  if (extDigitalRead(pin_drdy)) {
    spiEndTransaction();
    return false;
  }

  dataMSB = SPI.transfer(configRegister.byte.msb);
  dataLSB = SPI.transfer(configRegister.byte.lsb);
  
  spiEndTransaction();

  value = (dataMSB << 8) | (dataLSB);

  return true; 
}

/**
 * @brief Gets mV from specified inputs
 * 
 * @param inputs  The inputs to be acquired
 * @return ADC value in mV
 */
double ADS1118::getMilliVolts(uint8_t inputs) {
  // todo
}

/**
 * @brief Gets mV from settled inputs
 * 
 * @param pin_drdy  IO pin connected to ADS1118 DOUT/DRDY
 * @param volts     Reference of ADC value to be fetched
 * @return double containing ADC value in mV
 */
bool ADS1118::getMilliVoltsNoWait(uint8_t pin_drdy, double &volts) {
  // todo
}

/**
 * @brief Begin SPI interface transaction for ADS1118
 * 
 */
void ADS1118::spiBeginTransaction() {
  ADS1118_CS_L();
  SPI.beginTransaction(spiConfig);
  DEBUG_ECHOLNPGM("ADS1118: SPI transaction begin");
}

/**
 * @brief End SPI interface transaction for ADS1118
 * 
 */
void ADS1118::spiEndTransaction() {
  ADS1118_CS_H();
  SPI.endTransaction();
  DEBUG_ECHOLNPGM("ADS1118: SPI transaction end");
}

#endif  /* HAS_ADS1118 */