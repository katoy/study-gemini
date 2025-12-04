import asyncio
from bleak import BleakScanner


async def main():
    print("周辺のすべてのBLEデバイスを10秒間スキャンします...")
    devices = await BleakScanner.discover(timeout=10.0)

    if not devices:
        print("BLEデバイスが見つかりませんでした。")
        print("MacのBluetoothがオンになっているか確認してください。")
        return

    print(f"見つかったデバイス ({len(devices)}):")
    for device in devices:
        device_name = device.name or "（名前なし）"
        print(f"  - アドレス: {device.address}, 名前: {device_name}")

if __name__ == "__main__":
    asyncio.run(main())
