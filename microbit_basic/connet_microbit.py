import asyncio
from bleak import BleakScanner, BleakClient

# micro:bit UART (Nordic UART Service)
# TX: micro:bit -> Mac (notify)
# RX: Mac -> micro:bit (write)
UART_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # micro:bit -> Mac
UART_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # Mac -> micro:bit


async def main():
    print("Scanning for micro:bit...")

    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: (d.name or "").startswith("BBC micro:bit")
    )

    if device is None:
        print("micro:bit が見つかりませんでした。")
        return

    print(f"Found micro:bit: name={device.name}, address={device.address}")

    async with BleakClient(device) as client:
        print("Connected:", client.is_connected)

        # micro:bit からの UART 通知を受け取るコールバック
        async def notification_handler(sender, data: bytearray):
            try:
                received_data = data.decode().rstrip()
                print(f"[{sender}] Received: {received_data!r}")

                # micro:bit からの文字に応じて返信を決める
                if received_data == "A":
                    response_message = "a"
                elif received_data == "B":
                    response_message = "b"
                elif received_data == "A+B":
                    response_message = "c"
                else:
                    response_message = ""

                if response_message:
                    # micro:bit 側は改行区切りで受信しているので、末尾に "\n" を付ける
                    payload = (response_message + "\n").encode()
                    print(f"Sending response: {response_message!r}")
                    await client.write_gatt_char(UART_RX, payload)

            except UnicodeDecodeError:
                print(f"[{sender}] (binary) {data!r}")
            except Exception as e:
                print(f"Error in notification_handler: {e}")

        # micro:bit -> Mac の通知を有効化
        await client.start_notify(UART_TX, notification_handler)
        print(
            "Waiting for data... "
            "(micro:bit の A/B/A+B ボタンを押すと応答します)"
        )

        # イベントループを維持
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
