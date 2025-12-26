#!/usr/bin/env python3
"""
RS485 Modbus RTU Device ID Scanner
Detects device IDs of chain-connected drivers
"""

import serial
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException
import time

# Modbus settings
MODBUS_METHOD = 'rtu'
MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 115200
MODBUS_TIMEOUT = 0.1
MODBUS_PARITY = serial.PARITY_EVEN
MODBUS_STOPBITS = serial.STOPBITS_ONE

# Device ID address
MODBUS_ID_ADDRESS = 0x1380

# Scan range (Modbus device addresses are typically 1-247)
SCAN_START = 1
SCAN_END = 32

def scan_modbus_devices():
    """
    Scan all devices on RS485 chain and detect device IDs
    """
    print("=" * 70)
    print("RS485 Modbus RTU Device ID Scanner")
    print("=" * 70)
    print(f"Port: {MODBUS_PORT}")
    print(f"Baudrate: {MODBUS_BAUDRATE}")
    print(f"Parity: EVEN")
    print(f"Stopbits: 1")
    print(f"Timeout: {MODBUS_TIMEOUT}s")
    print(f"Scan range: {SCAN_START} - {SCAN_END}")
    print("=" * 70)
    print()
    
    # Create Modbus client
    client = ModbusClient(
        port=MODBUS_PORT,
        baudrate=MODBUS_BAUDRATE,
        timeout=MODBUS_TIMEOUT,
        retries=0,
        parity=MODBUS_PARITY,
        stopbits=MODBUS_STOPBITS
    )
    
    # Connect
    if not client.connect():
        print("ERROR: Cannot connect to Modbus port")
        return
    
    print("Connected to Modbus port")
    print()
    print("Scanning devices...")
    print("-" * 70)
    
    found_devices = []
    
    for target_id in range(1, 33):
        try:        
            print(f"Scanning ID: {target_id}...", end="\r")
            res = client.read_holding_registers(address=0x1380, count=2, device_id=target_id)
            time.sleep(1)
            if not res.isError():
                print(f"\nSUCCESS! Found device at ID: {target_id}")
                break
            else:
                print("\nDevice not found.")
        except Exception:
            continue

if __name__ == "__main__":
    try:
        scan_modbus_devices()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
