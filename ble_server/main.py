import asyncio
import logging
import sys
import os

# Add parent directory to sys.path to find 'server' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bleak import BleakScanner, BleakClient
from ble_server.game_adapter import GameAdapter

# Nordic UART Service (NUS) UUIDs
# Based on microbit_basic/connet_microbit.py
# RX: Central -> Peripheral (Write): ...0003
# TX: Peripheral -> Central (Notify): ...0002
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E" # Write (Mac -> micro:bit)
UART_TX_CHAR_UUID = "6E400002-B5A3-f393-e0a9-e50e24dcca9e" # Notify (micro:bit -> Mac)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

adapter = GameAdapter()

async def notification_handler(sender, data: bytearray):
    """Callback for when data is received from the micro:bit."""
    try:
        text = data.decode('utf-8').strip()
        logger.info(f"Micro:bit sent: {text}")

        # Process command via Adapter
        board_str, result = adapter.handle_command(text)

        # We need to send updates back to micro:bit.
        # But we don't have direct access to 'client' here conveniently unless we pass it or use a global/class.
        # Since this is a callback, we can't await 'send_update' easily if we don't have the client context.
        # However, the 'notification_handler' is synchronous in Bleak (runs in event loop).
        # We can create a task to send the response.

        # Note: sender is the characteristic handle (int), not the client object.
        pass
        # Actually, handling async writes inside this callback can be tricky.
        # A common pattern is to put the received data into a queue,
        # or use a class that holds the client reference.

    except Exception as e:
        logger.error(f"Error handling notification: {e}")

class BLEGameServer:
    def __init__(self, default_ai_agent="Random"):
        self.client = None
        self.adapter = GameAdapter(default_ai_agent=default_ai_agent)
        self.connected = False

    async def run(self):
        while True:
            logger.info("Scanning for micro:bit...")
            try:
                device = await BleakScanner.find_device_by_filter(
                    lambda d, ad: (d.name or "").startswith("BBC micro:bit")
                )

                if not device:
                    logger.warning("Micro:bit not found. Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                    continue

                logger.info(f"Found {device.name} ({device.address}). Connecting...")

                async with BleakClient(device, disconnected_callback=self.on_disconnect) as client:
                    self.client = client
                    self.connected = True
                    logger.info("Connected!")

                    # Start Notifications
                    await client.start_notify(UART_TX_CHAR_UUID, self.on_notification)

                    logger.info("Game Loop Started. Press Ctrl+C to exit.")

                    # Keep alive while connected
                    while self.connected:
                        await asyncio.sleep(1)

                logger.info("Connection lost. Restarting scan...")
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Connection error: {e}")
                logger.info("Retrying in 5 seconds...")
                await asyncio.sleep(5)

    def on_disconnect(self, client):
        logger.info("Disconnected.")
        self.connected = False

    async def on_notification(self, sender, data: bytearray):
        try:
            text = data.decode('utf-8').strip()
            logger.info(f"RX: {text}")

            # Update Game State
            board_str, result = self.adapter.handle_command(text)

            # Send Response
            await self.send_update(board_str, result)

        except Exception as e:
            logger.error(f"Error in RX handler: {e}")

    async def send_update(self, board_str, result):
        if not self.client or not self.connected:
            return

        try:
            # Special case for RESET
            if board_str == "RESET":
                msg = "RESET\n"
                logger.info(f"TX: {msg.strip()}")
                await self.client.write_gatt_char(UART_RX_CHAR_UUID, msg.encode('utf-8'))
                return

            # Send Board
            msg = f"BOARD:{board_str}\n"
            logger.info(f"TX: {msg.strip()}")
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, msg.encode('utf-8'))

            if result:
                msg_res = f"RESULT:{result}\n"
                logger.info(f"TX: {msg_res.strip()}")
                await self.client.write_gatt_char(UART_RX_CHAR_UUID, msg_res.encode('utf-8'))

        except Exception as e:
            logger.error(f"Error sending update: {e}")

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BLE Tic-Tac-Toe Server")
    parser.add_argument("--agent", type=str, default="Random", help="AI Agent to play against (default: Random)")
    args = parser.parse_args()

    server = BLEGameServer(default_ai_agent=args.agent)
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("User stopped server.")
