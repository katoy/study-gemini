bluetooth.startUartService()

// ★ プログラム開始時にハートを表示
basic.showIcon(IconNames.Heart)

// ★ 接続したとき
bluetooth.onBluetoothConnected(function () {
    basic.showIcon(IconNames.Yes)
})

// ★ 切断したとき
bluetooth.onBluetoothDisconnected(function () {
    basic.showIcon(IconNames.No)
})

// Aボタンが押されたら送信
input.onButtonPressed(Button.A, function () {
    // Mac に "A" を送る
    bluetooth.uartWriteString("A\n")
})

// Bボタンが押されたら送信
input.onButtonPressed(Button.B, function () {
    // Mac に "B" を送る
    bluetooth.uartWriteString("B\n")
})

// A+Bボタンが押されたら送信
input.onButtonPressed(Button.AB, function () {
    // Mac に "A+B" を送る
    bluetooth.uartWriteString("A+B\n")
})

// Mac からのデータを受信したら
bluetooth.onUartDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    const receivedString = bluetooth.uartReadUntil(
        serial.delimiters(Delimiters.NewLine)
    )
    // ここで "a" / "b" / "c" が表示される
    basic.showString(receivedString)
})

basic.forever(function () {
    // 何もしないで待機
})
