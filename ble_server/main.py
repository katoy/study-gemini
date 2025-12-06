import asyncio
import logging
import sys
import os

# Add parent directory to sys.path to find 'server' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bleak import BleakScanner, BleakClient
from ble_server.game_adapter import GameAdapter

# Nordic UART Service (NUS) UUIDs
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
                self.client = None
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Connection error: {e}")
                logger.info("Retrying in 5 seconds...")
                await asyncio.sleep(5)

    def on_disconnect(self, client):
        logger.info("Disconnected.")
        self.connected = False

    async def on_notification(self, sender, data: bytearray):
        """Callback for when data is received from the micro:bit."""
        try:
            text = data.decode('utf-8').strip()
            if not text:
                return
            logger.info(f"RX: {text}")

            # Process command via Adapter. It may return a single string or a tuple of two.
            response = self.adapter.handle_command(text)

            if isinstance(response, tuple):
                # Game over: send two separate messages
                ongoing_response, result_response = response
                # 1. Send the final board state, marked as ONGOING
                await self.send_update(ongoing_response)
                # 2. Wait briefly and send the actual result
                await asyncio.sleep(0.1)
                await self.send_update(result_response)
            else:
                # Game is ongoing: send a single update
                await self.send_update(response)

        except Exception as e:
            logger.error(f"Error in RX handler: {e}")

    async def send_update(self, response: str):
        """Sends a string response to the connected client."""
        if not self.client or not self.connected:
            logger.warning("Cannot send update, not connected.")
            return

        try:
            message = f"{response}\n"
            logger.info(f"TX: {message.strip()}")
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, message.encode('utf-8'))
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