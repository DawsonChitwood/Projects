#include <M5StickCPlus.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>

#define SERVICE_UUID "93e62043-efc6-4ccf-b834-0c902de87ec4"
#define CHAR_UUID "121eae50-5f0a-4780-843a-ad2c04997dd8"

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;

bool connected = false;
bool advertising = false;

int num = 0;

class MyServerCallbacks: public BLEServerCallbacks{

  
 void onConnect(BLEServer* pserver, esp_ble_gatts_cb_param_t *param){
   Serial.println("Device connected");
   connected = true;
   advertising = false;
 }
 
 
 void onDisconnect(BLEServer* pServer){
   Serial.println("Device disconnected");
   connected = false;
 }
};

#pragma pack(1);
typedef struct {
  u_int8_t btn;
} Packet;


void setup() {
  M5.begin();
  
 
  int m = M5.IMU.Init();
  


  BLEDevice::init("M5StickCPlus-Dawson");
  
  
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  
  BLEService *pService = pServer->createService(SERVICE_UUID);
  

  pCharacteristic = pService->createCharacteristic(
    CHAR_UUID,BLECharacteristic::PROPERTY_READ  |  
    BLECharacteristic::PROPERTY_NOTIFY
  );
  
  
  pCharacteristic->addDescriptor(new BLE2902());

 
  pService->start();
  
  
  BLEDevice:: startAdvertising();

}
Packet p;



void loop() {
   p.btn = M5.BtnA.read();

    pCharacteristic->setValue((uint8_t*)&p, sizeof(Packet));
    pCharacteristic->notify();
    num++;
    delay(10);

    if(!connected && !advertising){
    BLEDevice::startAdvertising();
    Serial.println("start Advertisting");
    advertising = true;
  }
  
}
