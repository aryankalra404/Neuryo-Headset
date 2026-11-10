// Neuryo rev B firmware (Seeed XIAO ESP32-S3).
// Based on the Low-Cost-EEG firmware (X. Asghar, GPL-3.0, upstream commit 3730d31,
// Software/Firmware_Platformio_Project/src/main.cpp). BLE service, characteristic, packet format (28 bytes:
// counter + 3 status + 8 x 3 channel bytes) and batching (8 packets per notify) are unchanged.
// What changes and why is in ../README.md.

#include <Arduino.h>
#include <ADS1299.h>
#include <Wire.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <esp_gap_ble_api.h>
#include "soc/gpio_reg.h"

ADS1299 ADS;

// XIAO ESP32-S3 pins (rev B schematic, U6). Dn -> GPIO from the XIAO_ESP32S3 variant in arduino-esp32.
#define VBAT_SENSE_PIN 1    // D0: battery through 220k/220k, 100 nF
#define DRDY_PIN       2    // D1
#define CS_PIN         3    // D2 (10k pull-up to DVDD on the board, R28)
#define MOSI_PIN       4    // D3 -> ADS1299 DIN
#define SCK_PIN        5    // D4
#define MISO_PIN       6    // D5 <- ADS1299 DOUT
#define I2C_SDA_PIN    7    // D8 -> J6 (MAX30102), J7 (BMI270)
#define I2C_SCL_PIN    44   // D7
#define USB_SENSE_PIN  8    // D9: XIAO 5V through 100k/150k, high = USB present = ADS1299 unpowered (interlock)
#define BOOT_BUTTON_PIN 0
// 4th pass: D10 (GPIO9) -> ADS1299 RESET (R30 10k pull-up to DVDD stays). Driven open-drain only, never high, so it
// cannot back-power the ADS1299 when the analog side is off. Not passed to the library (it would drive it push-pull).
#define ADS_RESET_PIN  9    // D10
static_assert(D10 == ADS_RESET_PIN, "XIAO D10 must be GPIO9 (rev B 4th pass pin map)");
// START has no GPIO: pulled down (R36 10k), START command used. PWDN pulled up (10k).
#define NO_PIN        -1

// Bench build (env xiao_esp32s3_bench, -D BENCH_NO_INTERLOCK): USB_SENSE is ignored and the ADS1299 starts on USB,
// for a bench board with Q1 removed (inputs shorted or on a signal generator). Never on a person.
#ifdef BENCH_NO_INTERLOCK
#define BENCH_NOTE " BENCH BUILD: interlock ignored, not for use on a person"
#else
#define BENCH_NOTE ""
#endif

// BLUETOOTH DEFINITIONS (unchanged)
#define bleServerName "ESP32_EEG_DATA"
#define SERVICE_UUID "91bad492-b950-4226-aa2b-4ede9fa42f59"
#define CHARACTERISTIC_UUID "cba1d466-344c-4be3-ab3f-189f80dd7518"
// New, read/notify, ASCII text: "usb=<0|1> ads=<0|1> id=<hex> vbat=<mV> i2c=<addresses>" (+ BENCH_NOTE on the bench build)
#define STATUS_UUID "5c3a1f2e-8d4b-4f6a-9e21-7b0c6d9a4e13"
BLECharacteristic *pCharacteristic = NULL;
BLECharacteristic *pStatus = NULL;

void IRAM_ATTR dataReadyISR();
void IRAM_ATTR buttonISR();
void IRAM_ATTR usbSenseISR();
void myGapHandler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param);
void readADSDataTask(void * pvParameters);
void sendDataTask(void * pvParameters);
bool adsStart();
void adsStop();
void adsHardwareReset();
void updateStatus();

SemaphoreHandle_t drdySemaphore;
QueueHandle_t packetQueue;
uint8_t sampleCounter = 0;
volatile bool deviceConnected = false;
volatile bool triggerRecordMode = false;
volatile bool adsRunning = false;          // ADS1299 powered, configured and converting
volatile bool usbEvent = false;            // USB_SENSE changed
uint8_t adsId = 0;                         // last ID register read (0x3E expected; 0 = not read yet)
String i2cFound = "none";

// --------------------------------------------------------------------------------------------------------------------------------------

class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer, esp_ble_gatts_cb_param_t *param) {
    deviceConnected = true;
    Serial.println("Device connected!");
    pServer->updateConnParams(param->connect.remote_bda, 6, 12, 0, 400);
    esp_ble_gap_set_pkt_data_len(param->connect.remote_bda, 251);
  };

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    Serial.println("Device disconnected. Restarting advertising...");
    pServer->getAdvertising()->start();
  }
};

// --------------------------------------------------------------------------------------------------------------------------------------

void setup() {
  // Keep every line into the ADS1299 high-impedance until we know it is powered.
  pinMode(SCK_PIN, INPUT);
  pinMode(MOSI_PIN, INPUT);
  pinMode(CS_PIN, INPUT);
  pinMode(DRDY_PIN, INPUT);
  pinMode(ADS_RESET_PIN, INPUT);           // R30 holds RESET high; only ever pulled low (open-drain)
  pinMode(USB_SENSE_PIN, INPUT);           // divider drives it; no internal pull
#ifndef BENCH_NO_INTERLOCK
  attachInterrupt(digitalPinToInterrupt(USB_SENSE_PIN), usbSenseISR, CHANGE);
#endif

  Serial.begin(115200);
  delay(1000);
#ifdef BENCH_NO_INTERLOCK
  Serial.println(BENCH_NOTE);
#endif
  Serial.printf("PSRAM size: %u bytes\n", ESP.getPsramSize());

  pinMode(BOOT_BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BOOT_BUTTON_PIN), buttonISR, FALLING);

  analogReadResolution(12);

  // I2C: earlobe MAX30102 (0x57) and BMI270 (0x68 or 0x69) on J6/J7. 4.7k pull-ups to the XIAO 3V3 on the board (R46, R47).
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 400000);
  i2cFound = "";
  for (uint8_t a = 0x08; a < 0x78; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      char b[6]; snprintf(b, sizeof(b), "%02X ", a); i2cFound += b;
    }
  }
  if (i2cFound.length() == 0) i2cFound = "none";
  Serial.println("I2C devices: " + i2cFound);

  packetQueue = xQueueCreate(256, 28 * sizeof(uint8_t));
  drdySemaphore = xSemaphoreCreateBinary();

  // BLUETOOTH LOW ENERGY SETUP (unchanged, plus the status characteristic)
  BLEDevice::init(bleServerName);
  BLEDevice::setMTU(512);
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID, BLECharacteristic::PROPERTY_NOTIFY);
  pCharacteristic->addDescriptor(new BLE2902());
  pStatus = pService->createCharacteristic(STATUS_UUID, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  pStatus->addDescriptor(new BLE2902());
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pServer->getAdvertising()->start();
  BLEDevice::setCustomGapHandler(myGapHandler);
  delay(1000);

  xTaskCreatePinnedToCore(readADSDataTask, "ReadTask", 4096, NULL, 3, NULL, 1);
  xTaskCreatePinnedToCore(sendDataTask, "SendTask", 4096, NULL, 1, NULL, 0);

#ifdef BENCH_NO_INTERLOCK
  adsStart();
#else
  if (digitalRead(USB_SENSE_PIN) == HIGH) {
    Serial.println("USB present: analog side is off (interlock). Unplug USB to record.");
  } else {
    adsStart();
  }
#endif
  updateStatus();
  Serial.println("Setup complete\n");
}

// --------------------------------------------------------------------------------------------------------------------------------------

void loop() {
  static uint32_t lastStatus = 0;

#ifndef BENCH_NO_INTERLOCK
  if (usbEvent) {
    usbEvent = false;
    delay(20);                                           // let the divider and the EN net settle
    bool usb = digitalRead(USB_SENSE_PIN) == HIGH;
    if (usb && adsRunning) {
      adsStop();
      Serial.println("USB plugged in: ADS1299 stopped, SPI lines released.");
    } else if (!usb && !adsRunning) {
      Serial.println("USB removed: starting the ADS1299.");
      adsStart();
    }
    updateStatus();
  }
#endif

  // BOOT button: turn lead-off detection off (record mode), as upstream
  if (triggerRecordMode) {
    triggerRecordMode = false;
    if (adsRunning) {
      ADS.STOP();
      delay(10);
      ADS.SDATAC();
      uint8_t config3_val = ADS.RREG(CONFIG3);
      Serial.println((config3_val & 0b00000001) ? "Bias Disconnected" : "Bias Connected");
      ADS.WREG(LOFF_SENSP, 0b00000000);
      ADS.WREG(LOFF_SENSN, 0b00000000);
      ADS.WREG(CONFIG3, 0b11111100);
      ADS.RDATAC();
      ADS.START();
      delay(10);
      Serial.println("Lead-off disabled\n");
    }
  }

  if (millis() - lastStatus > 10000) {
    lastStatus = millis();
    updateStatus();
  }
  delay(100);
}

// --------------------------------------------------------------------------------------------------------------------------------------
// ADS1299 bring-up. Register values follow upstream except where rev B's reference wiring differs:
//  - reference electrode (M1) on SRB2 through R27/C31, so MISC1.SRB1 = 0 and CHnSET.SRB2 = 1 on channels 1-7
//  - electrodes on the N inputs of channels 1-7 (as on the OpenBCI Cyton); channel 8 differential (ECG), SRB2 open
//  - bias and lead-off sensing moved from the P to the N inputs to match
//  - START by command (START pin held low by R36, as the datasheet requires when using the command)
//  - RESET: hardware pulse on D10 (open-drain), then the RESET command as before
// Returns false, with adsRunning false and the SPI lines released, if the ID register does not read as an ADS1299.
bool adsStart() {
  ADS.setup(DRDY_PIN, CS_PIN, SCK_PIN, MISO_PIN, MOSI_PIN, NO_PIN, NO_PIN);   // waits tPOR, then RESET command
  adsHardwareReset();
  ADS.RESET();                      // RESET command after the pulse, as before
  delay(1);
  ADS.SDATAC();                     // Stop continuous data mode to allow register configuration
  adsId = ADS.RREG(ID);
  Serial.printf("ADS1299 ID = 0x%02X\n", adsId);
  if ((adsId & 0x1F) != 0x1E) {      // ADS1299-8 reads 0x3E (OpenBCI Cyton library checks the same register); upstream does not check
    Serial.println("ADS1299 not answering: check DVDD/AVDD and the SPI lines. Not started.");
    adsRunning = false;
    ADS.release();
    return false;
  }
  ADS.WREG(GPIO, 0b00000000);
  ADS.WREG(CONFIG1, 0b10010101);    // 500 SPS (as upstream)
  ADS.WREG(CONFIG3, 0b11111110);    // internal reference, bias buffer, BIASREF_INT, bias lead-off (as upstream)
  ADS.WREG(CONFIG4, 0b00000010);    // lead-off comparators on (as upstream)

  ADS.WREG(MISC1, 0b00000000);      // SRB1 open (upstream: 0b00100100, SRB1 to all N inputs)
  ADS.WREG(BIAS_SENSP, 0b00000000);
  ADS.WREG(BIAS_SENSN, 0b01111111); // bias derived from the electrode (N) inputs of channels 1-7

  ADS.WREG(LOFF, 0b00000100);       // as upstream
  ADS.WREG(LOFF_SENSP, 0b10000001); // ch1 P = SRB2 = reference electrode; ch8 P (ECG +)
  ADS.WREG(LOFF_SENSN, 0b11111111); // every electrode input

  for (int i = CH1SET; i <= CH7SET; i++) ADS.WREG(i, 0b01101000);  // gain 24, SRB2 closed, normal input
  ADS.WREG(CH8SET, 0b01100000);                                      // gain 24, SRB2 open: differential (ECG)

  attachInterrupt(digitalPinToInterrupt(DRDY_PIN), dataReadyISR, FALLING);
  adsRunning = true;
  ADS.RDATAC();                     // continuous data mode, then START (command), as the OpenBCI Cyton library does
  ADS.START();
  delay(10);
  return true;
}

// Datasheet: RESET low for at least 2 tCLK (about 1 us at 2.048 MHz); the device is ready 18 tCLK (about 9 us) after
// RESET goes high. 10 us low and 1 ms wait leave a wide margin. Open-drain: the pin only ever sinks; R30 pulls it high.
void adsHardwareReset() {
  digitalWrite(ADS_RESET_PIN, LOW);
  pinMode(ADS_RESET_PIN, OUTPUT_OPEN_DRAIN);
  digitalWrite(ADS_RESET_PIN, LOW);
  delayMicroseconds(10);
  pinMode(ADS_RESET_PIN, INPUT);
  delay(1);
}

void adsStop() {
  adsRunning = false;
  detachInterrupt(digitalPinToInterrupt(DRDY_PIN));
  ADS.release();                    // SCLK, MOSI, CS -> inputs (the ISR already did this in hardware)
  xQueueReset(packetQueue);
}

// USB plugged in: the 2N7002 pulls AEN low and the ADS1299 rails collapse within milliseconds. Stop driving SCLK, MOSI
// and CS at once (register write, safe in an ISR) so the ESP32 never back-powers the ADS1299 through its I/O diodes.
void IRAM_ATTR usbSenseISR() {
  if ((REG_READ(GPIO_IN_REG) >> USB_SENSE_PIN) & 1) {   // register read: no flash access from the ISR
    adsRunning = false;
    REG_WRITE(GPIO_ENABLE_W1TC_REG, (1UL << SCK_PIN) | (1UL << MOSI_PIN) | (1UL << CS_PIN));
  }
  usbEvent = true;
}

void updateStatus() {
  uint32_t mv = analogReadMilliVolts(VBAT_SENSE_PIN) * 2;   // 220k / 220k divider
  char s[192];
  snprintf(s, sizeof(s), "usb=%d ads=%d id=%02X vbat=%lu i2c=%s%s", digitalRead(USB_SENSE_PIN) == HIGH, adsRunning ? 1 : 0,
           adsId, (unsigned long)mv, i2cFound.c_str(), BENCH_NOTE);
  Serial.println(s);
  if (pStatus) {
    pStatus->setValue((uint8_t *)s, strlen(s));
    if (deviceConnected) pStatus->notify();
  }
}

// --------------------------------------------------------------------------------------------------------------------------------------

void IRAM_ATTR buttonISR() {
  triggerRecordMode = true;
}

void IRAM_ATTR dataReadyISR() {
  if (!adsRunning) return;
  BaseType_t xHigherPriorityTaskWoken = pdFALSE;
  xSemaphoreGiveFromISR(drdySemaphore, &xHigherPriorityTaskWoken);
  if (xHigherPriorityTaskWoken) {
    portYIELD_FROM_ISR();
  }
}

void myGapHandler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param) {
  if (event == ESP_GAP_BLE_SET_PKT_LENGTH_COMPLETE_EVT) {
    Serial.printf("DLE: status=%d tx=%d rx=%d\n",
        param->pkt_data_lenth_cmpl.status,
        param->pkt_data_lenth_cmpl.params.tx_len,
        param->pkt_data_lenth_cmpl.params.rx_len);
  }
  if (event == ESP_GAP_BLE_UPDATE_CONN_PARAMS_EVT) {
    Serial.printf("Conn params: interval=%d (%.2f ms), latency=%d, timeout=%d ms\n",
        param->update_conn_params.conn_int,
        param->update_conn_params.conn_int * 1.25,
        param->update_conn_params.latency,
        param->update_conn_params.timeout * 10);
  }
}

// --------------------------------------------------------------------------------------------------------------------------------------

void readADSDataTask(void * pvParameters) {
  uint8_t dataPacket[28];
  for(;;) {
    if (xSemaphoreTake(drdySemaphore, portMAX_DELAY) == pdTRUE) {
      if (!adsRunning) continue;             // USB was plugged in: the ADS1299 is unpowered
      dataPacket[0] = sampleCounter++;
      ADS.updateDataPacket(dataPacket);
      xQueueSend(packetQueue, dataPacket, 0);
    }
  }
}

void sendDataTask(void * pvParameters) {
  uint8_t singlePacket[28];
  uint8_t batchBuffer[224];
  int batchCount = 0;
  for(;;) {
    if (!deviceConnected) {
      xQueueReset(packetQueue);
      batchCount = 0;
      vTaskDelay(pdMS_TO_TICKS(100));
      continue;
    }
    if (xQueueReceive(packetQueue, &singlePacket, pdMS_TO_TICKS(500)) == pdPASS) {
      memcpy(&batchBuffer[batchCount * 28], singlePacket, 28);
      batchCount++;
      if (batchCount == 8) {
        pCharacteristic->setValue(batchBuffer, 224);
        pCharacteristic->notify();
        batchCount = 0;
      }
    }
  }
}
