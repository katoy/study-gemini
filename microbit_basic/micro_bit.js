/**
 * @file micro_bit.js
 * @brief micro:bit Bluetooth UART通信サンプルスクリプト
 * @details
 *  - Bluetooth接続/切断時にアイコンを表示します。
 *  - Aボタンが押されたら"A"、Bボタンが押されたら"B"をUART経由で送信します。
 *  - 起動時にハートアイコンを表示します。
 * @author Gemini
 * @date 2025年12月4日木曜日
 */
// Bluetooth接続/切断時にアイコンを表示
bluetooth.onBluetoothConnected(function () {
    basic.showIcon(IconNames.Yes)
})
bluetooth.onBluetoothDisconnected(function () {
    basic.showIcon(IconNames.No)
})
// Aボタンが押されたら "A" という文字列を送信
input.onButtonPressed(Button.A, function () {
    bluetooth.uartWriteString("A")
    basic.showString("A")
})
// Bボタンが押されたら "B" という文字列を送信
input.onButtonPressed(Button.B, function () {
    bluetooth.uartWriteString("B")
    basic.showString("B")
})
// Bluetooth UARTサービスを開始
bluetooth.startUartService()
// 起動時にハートアイコンを表示
basic.showIcon(IconNames.Heart)

