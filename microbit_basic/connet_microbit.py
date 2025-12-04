import asyncio
from bleak import BleakScanner, BleakClient

# micro:bit UART (Nordic UART Service)
# TX: micro:bit -> Mac (notify)
# RX: Mac -> micro:bit (write)
UART_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # ← start_notify はこちら
UART_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # ← write_gatt_char で使う


def notification_handler(sender, data: bytearray):
    try:
        print(f"[{sender}] {data.decode().rstrip()}")
    except UnicodeDecodeError:
        print(f"[{sender}] (binary) {data!r}")


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

        # ★ ここを TX(002) に変更
        await client.start_notify(UART_TX, notification_handler)
        print("Waiting for data... (micro:bit のボタン A を押してみてください)")

        # 60秒待つ（必要に応じて変更）
        await asyncio.sleep(60)

        await client.stop_notify(UART_TX)

if __name__ == "__main__":
    asyncio.run(main())
