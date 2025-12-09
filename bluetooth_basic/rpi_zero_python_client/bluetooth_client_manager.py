import bluetooth
import threading
import time
import sys

# SPP UUID (Standard for Serial Port Profile)
SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"
PORT = 1 # RFCOMM port

# List of ESP32 device MAC addresses to connect to
# IMPORTANT: Replace these with the actual MAC addresses of your ESP32 boards
# You can find the MAC address of your ESP32 in its Arduino Serial Monitor output
# when running the esp32_bluetooth_spp.ino sketch.
# Example: ESP32_DEVICES_TO_CONNECT = ["XX:XX:XX:XX:XX:XX", "YY:YY:YY:YY:YY:YY"]
ESP32_DEVICES_TO_CONNECT = [] # Placeholder: User must fill this in

def connect_and_communicate(device_mac_address):
    """
    Connects to a single ESP32 device and handles communication.
    """
    print(f"Attempting to connect to ESP32: {device_mac_address}")
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        # For simplicity, we directly connect to port 1.
        # In some cases, service discovery might be needed to find the correct port.
        # For SPP, port 1 is common.
        sock.connect((device_mac_address, PORT))
        print(f"Successfully connected to ESP32: {device_mac_address}")

        # Send a request and receive a response
        message_counter = 0
        while True:
            message_counter += 1
            request_message = f"request_time_{message_counter}"
            print(f"[{device_mac_address}] Sending: {request_message}")
            sock.send((request_message + '\n').encode('utf-8')) # Add newline for ESP32 readStringUntil

            data = sock.recv(1024)
            if not data:
                print(f"[{device_mac_address}] No data received, connection might be closed.")
                break

            response = data.decode('utf-8').strip()
            print(f"[{device_mac_address}] Received: {response}")

            time.sleep(5) # Send a message every 5 seconds

    except bluetooth.BluetoothError as e:
        print(f"[{device_mac_address}] Bluetooth error: {e}")
    except Exception as e:
        print(f"[{device_mac_address}] An unexpected error occurred: {e}")
    finally:
        print(f"[{device_mac_address}] Disconnecting from ESP32.")
        sock.close()

def main():
    if not ESP32_DEVICES_TO_CONNECT:
        print("ERROR: No ESP32 device MAC addresses specified.")
        print("Please edit 'bluetooth_client_manager.py' and fill in 'ESP32_DEVICES_TO_CONNECT'.")
        sys.exit(1)

    threads = []
    for device_mac in ESP32_DEVICES_TO_CONNECT:
        thread = threading.Thread(target=connect_and_communicate, args=(device_mac,))
        threads.append(thread)
        thread.start()
        time.sleep(1) # Stagger connection attempts

    # Keep the main thread alive until all client threads finish
    for thread.is_alive():
      time.sleep(1)
    # for thread in threads:
    #     thread.join() # This will wait indefinitely if threads run forever

    print("All ESP32 communication threads have finished.")

if __name__ == "__main__":
    print("Starting Raspberry Pi Zero Bluetooth SPP Client Manager...")
    main()
