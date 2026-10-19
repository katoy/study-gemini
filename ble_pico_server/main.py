import bluetooth
import struct
import time
from machine import Pin
from ble_pico_server.game_adapter import GameAdapter  # Import GameAdapter

# Nordic UART Service (NUS) UUIDs
NUS_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
NUS_RX_CHAR_UUID = bluetooth.UUID(
    "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
)  # Central writes, Peripheral reads
NUS_TX_CHAR_UUID = bluetooth.UUID(
    "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
)  # Peripheral writes, Central reads

# BLE object
ble = bluetooth.BLE()
ble.active(True)

# Global variables for connection state and characteristics
connected = False
nus_service = None
rx_char = None
tx_char = None
target_addr = None  # Stores the address of the NUS peripheral we want to connect to
conn_handle = None  # Global connection handle

# Game Adapter instance
game_adapter = GameAdapter(default_ai_agent="Random")  # Instantiate GameAdapter

# LED for status indication
led = Pin("LED", Pin.OUT)


def hex_to_uuid(hex_str):
    # MicroPython's UUID expects standard hex string, not byte-reversed
    # The adv_decode function in the search result seems to be overly complex for standard UUIDs.
    # Let's simplify and directly use the UUID object.
    return bluetooth.UUID(hex_str)


def adv_decode(payload):
    """
    Decode advertising payload to extract service UUIDs.
    Adjusted to correctly parse 128-bit UUIDs without byte reversal,
    as bluetooth.UUID handles the string representation directly.
    """
    service_uuids = []
    i = 0
    while i + 1 < len(payload):
        length = payload[i]
        type_code = payload[i + 1]

        # Complete List of 128-bit Service Class UUIDs (type_code 0x07)
        if type_code == 0x07 and length == 17:
            # Extract 16 bytes for UUID
            uuid_bytes_le = payload[
                i + 2 : i + 2 + 16
            ]  # Little-endian bytes from advertisement
            # Reconstruct into big-endian hex string for bluetooth.UUID
            uuid_hex = "".join(f"{b:02X}" for b in reversed(uuid_bytes_le))
            service_uuids.append(bluetooth.UUID(uuid_hex))
            i += length + 1
        else:
            i += length + 1
    return service_uuids


def ble_irq(event, data):
    global target_addr, connected, nus_service, rx_char, tx_char, conn_handle

    if event == 5:  # EVT_GAP_ADVERTISE_REPORT
        addr_type, addr, adv_type, rssi, adv_data = data
        services = adv_decode(adv_data)

        # Check if NUS service is advertised (using the correct NUS_SERVICE_UUID object)
        if NUS_SERVICE_UUID in services:
            print(f"Found NUS peripheral: {addr} (RSSI: {rssi})")
            # The original example had `if not connected:`, but we only want to connect if target_addr is None
            # to avoid multiple connection attempts.
            if target_addr is None:  # Only connect to the first NUS device found
                target_addr = addr
                ble.gap_scan(None)  # Stop scanning
                print(f"Stopping scan, attempting to connect to {addr}...")
                ble.gap_connect(addr_type, addr)

    elif event == 7:  # EVT_GAP_CONNECT
        conn_handle_new, addr_type, addr = data
        if conn_handle_new:
            conn_handle = conn_handle_new
            print(f"Connected to {addr}")
            connected = True
            led.value(1)  # Turn on LED to indicate connection
            # Discover services and characteristics
            ble.gattc_discover_services(conn_handle)
        else:
            print(f"Connection to {addr} failed.")
            connected = False
            led.value(0)  # Turn off LED
            target_addr = None  # Allow scanning again for this device
            print("Restarting scan...")
            ble.gap_scan(
                0, 30000, 30000
            )  # Scan for 30 seconds, non-stop until cancelled

    elif event == 8:  # EVT_GAP_DISCONNECT
        _conn_handle, _addr_type, _addr = (
            data  # data contains conn_handle, addr_type, addr
        )
        print(f"Disconnected from {_addr}")
        connected = False
        led.value(0)  # Turn off LED
        conn_handle = None
        nus_service = None
        rx_char = None
        tx_char = None
        target_addr = None  # Reset target address to allow fresh scan
        # Restart scan
        print("Restarting scan...")
        ble.gap_scan(0, 30000, 30000)  # Scan for 30 seconds, non-stop until cancelled

    elif event == 9:  # EVT_GATTC_SERVICE_RESULT
        # data contains conn_handle, start_handle, end_handle, uuid
        _conn_handle, start_handle, end_handle, uuid = data
        if uuid == NUS_SERVICE_UUID:
            nus_service = (_conn_handle, start_handle, end_handle, uuid)
            print(f"Found NUS service: {nus_service[1]} - {nus_service[2]}")
            ble.gattc_discover_characteristics(_conn_handle, start_handle, end_handle)

    elif event == 10:  # EVT_GATTC_CHARACTERISTIC_RESULT
        # data contains conn_handle, start_handle, end_handle, uuid, properties
        _conn_handle, start_handle, end_handle, uuid, properties = data
        if uuid == NUS_RX_CHAR_UUID:
            rx_char = (_conn_handle, start_handle, uuid)
            print(f"Found NUS RX characteristic (Central writes): handle {rx_char[1]}")
        elif uuid == NUS_TX_CHAR_UUID:
            tx_char = (_conn_handle, start_handle, uuid)
            print(
                f"Found NUS TX characteristic (Central reads/notifies): handle {tx_char[1]}"
            )
            # The CCCD (Client Characteristic Configuration Descriptor) for notifications
            # is typically at handle + 1 relative to the characteristic value handle.
            # Value 0x0001 (enable notification), 0x0002 (enable indication)
            # The search result used start_handle + 1, which is common.
            # struct.pack('<h', 1) packs short integer 1 (0x0001) as little-endian.
            ble.gattc_write(
                _conn_handle, start_handle + 1, struct.pack("<h", 1), 1
            )  # 1 for no_response
            print("Enabled notifications for NUS TX characteristic.")

    elif event == 11:  # EVT_GATTC_CHARACTERISTIC_DONE
        # data contains conn_handle, status
        _conn_handle, status = data
        if status == 0:  # Status 0 means success
            if nus_service and rx_char and tx_char:
                print("All NUS characteristics found and notifications enabled.")
            else:
                print("NUS service or essential characteristics not found completely.")
                if connected and conn_handle:
                    print("Disconnecting due to incomplete service discovery.")
                    ble.gap_disconnect(conn_handle)
        else:
            print(f"Characteristic discovery failed with status {status}")
            if connected and conn_handle:
                print("Disconnecting due to characteristic discovery failure.")
                ble.gap_disconnect(conn_handle)

    elif event == 18:  # EVT_GATTC_NOTIFY
        # data contains conn_handle, value_handle, notify_data
        _conn_handle, value_handle, notify_data = data
        if tx_char and value_handle == tx_char[1]:  # Check if it's our TX char
            try:
                message = notify_data.decode("utf-8").strip()
                print(f"Received from peripheral: {message}")

                # Process command via GameAdapter
                response = game_adapter.handle_command(message)

                if isinstance(response, tuple):
                    # Game over: send two separate messages
                    ongoing_response, result_response = response
                    # 1. Send the final board state, marked as ONGOING
                    ble_send_data(ongoing_response)
                    # 2. Wait briefly and send the actual result (no time.sleep in IRQ, send immediately)
                    ble_send_data(result_response)
                else:
                    # Game is ongoing: send a single update
                    ble_send_data(response)

            except UnicodeError:
                print(f"Received non-UTF-8 data: {notify_data}")
            except Exception as e:
                print(f"Error processing received data: {e}")
        else:
            print(
                f"Received unknown notification: handle {value_handle}, data {notify_data}"
            )


ble.irq(ble_irq)


def ble_send_data(data_str):
    """
    Sends data string to the connected NUS peripheral via the RX characteristic.
    """
    global conn_handle, rx_char
    if connected and conn_handle and rx_char:
        try:
            # We use conn_handle from the global scope after connection is established
            _conn_handle_for_send = conn_handle
            _rx_char_handle = rx_char[1]
            ble.gattc_write(
                _conn_handle_for_send, _rx_char_handle, data_str.encode("utf-8"), 1
            )  # 1 for no_response
            print(f"Sent: {data_str}")
        except Exception as e:
            print(f"Error sending data: {e}")
    else:
        print("Not connected or RX characteristic not found for sending data.")


# Start scanning for BLE peripherals
print("Starting BLE scan for NUS peripheral...")
# Scan indefinitely (0 duration) with 30ms interval and 30ms window.
# The scan will be stopped by adv_handler when a device is found.
ble.gap_scan(0, 30000, 30000)

# Main loop
try:
    while True:
        # This loop keeps the script alive.
        # Further game logic integration and command handling will go here.
        time.sleep_ms(100)

except KeyboardInterrupt:
    print("Exiting.")
    ble.active(False)
    led.value(0)
