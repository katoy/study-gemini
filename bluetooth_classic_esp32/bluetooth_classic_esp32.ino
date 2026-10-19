#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

// ESP32のチップIDを取得し、ユニークなBluetooth名を作成
uint64_t chipId = ESP.getEfuseMac(); // チップのMACアドレスを取得
char bt_name[30];
// MACアドレスの最後のバイトを使用してユニークな名前を作成
sprintf(bt_name, "ESP32_SPP_SERVER_%02X", (uint8_t)(chipId & 0xFF));

void setup() {
  Serial.begin(115200);
  SerialBT.begin(bt_name); // Bluetooth Classicを初期化し、名前を設定
  Serial.printf("Bluetooth SPP Server '%s' started.\n", bt_name);
}

void loop() {
  // Macからデータを受信した場合
  if (SerialBT.available()) {
    String request = SerialBT.readStringUntil('\n'); // 改行まで読み込み
    request.trim(); // 前後の空白を削除

    if (request.length() > 0) {
      Serial.printf("Received from Mac: %s\n", request.c_str());

      // リクエストに対する簡単なレスポンスを生成 (例: 大文字にして返す)
      String response = "ECHO: " + request.toUpperCase();
      SerialBT.println(response); // Macにレスポンスを送信
      Serial.printf("Sent to Mac: %s\n", response.c_str());
    }
  }

  // シリアルモニターからデータを受信した場合 (デバッグ用)
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    SerialBT.println(input); // 受信したデータをMacに送信
  }

  delay(20);
}
