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
MODBUS_TIMEOUT = 1
MODBUS_PARITY = serial.PARITY_EVEN
MODBUS_STOPBITS = serial.STOPBITS_ONE

# Device ID address
MODBUS_ID_ADDRESS = 0x1380

# Scan range (Modbus device addresses are typically 1-247)
SCAN_START = 1
SCAN_END = 247

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
    
    try:
        for device_id in range(SCAN_START, SCAN_END + 1):
            # Progress display (every 10 devices)
            if device_id % 10 == 0:
                print(f"Scanning: {device_id}/{SCAN_END}...", end='\r')
            
            try:
                # Read 2 registers from device ID address
                result = client.read_holding_registers(
                    address=MODBUS_ID_ADDRESS,
                    count=2,
                    slave=device_id
                )
                
                # If response received
                if not result.isError():
                    # Get register values
                    registers = result.registers
                    
                    # Calculate device ID (combine 2 registers into 32-bit value)
                    # High 16 bits + Low 16 bits
                    device_info_value = (registers[0] << 16) | registers[1]
                    
                    found_devices.append({
                        'address': device_id,
                        'registers': registers,
                        'value': device_info_value
                    })
                    
                    print(f"\nDevice found!")
                    print(f"   Modbus address: {device_id}")
                    print(f"   Register values: [0x{registers[0]:04X}, 0x{registers[1]:04X}]")
                    print(f"   Combined value: 0x{device_info_value:08X} ({device_info_value})")
                    print("-" * 70)
                    
                # Wait before scanning next device
                time.sleep(0.05)
                
            except ModbusException as e:
                # Ignore timeout or communication errors (no device)
                pass
            except Exception as e:
                # Other errors
                if device_id % 50 == 0:  # Display error every 50 devices
                    print(f"\nWARNING: Error at address {device_id}: {e}")
    
    finally:
        client.close()
    
    # Result summary
    print("\n")
    print("=" * 70)
    print("Scan Result Summary")
    print("=" * 70)
    
    if found_devices:
        print(f"\nDevices found: {len(found_devices)}")
        print()
        print(f"{'Modbus Addr':<15} {'Register[0]':<15} {'Register[1]':<15} {'Combined (dec)':<20}")
        print("-" * 70)
        
        for device in found_devices:
            print(f"{device['address']:<15} "
                  f"0x{device['registers'][0]:04X} ({device['registers'][0]:<5}) "
                  f"0x{device['registers'][1]:04X} ({device['registers'][1]:<5}) "
                  f"{device['value']:<20}")
    else:
        print("\nWARNING: No devices found")
        print("\nPossible causes:")
        print("  - RS485 wiring issues")
        print("  - Incorrect baudrate, parity, or other settings")
        print("  - Devices not powered on")
        print("  - Devices outside address range")
    
    print("=" * 70)


if __name__ == "__main__":
    try:
        scan_modbus_devices()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
