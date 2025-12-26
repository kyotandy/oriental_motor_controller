#!/usr/bin/env python3
"""
シリアルポート接続テスト
"""

import serial
from pymodbus.client import ModbusSerialClient as ModbusClient

MODBUS_PORT = '/dev/ttyUSB0'

print("=" * 70)
print("シリアルポート接続テスト")
print("=" * 70)

# 1. serialモジュールで直接テスト
print("\n1. serialモジュールでテスト...")
try:
    ser = serial.Serial(
        port=MODBUS_PORT,
        baudrate=115200,
        bytesize=8,
        parity='E',
        stopbits=1,
        timeout=1
    )
    print(f"✅ ポート {MODBUS_PORT} を直接開けました")
    print(f"   設定: {ser}")
    ser.close()
except Exception as e:
    print(f"❌ エラー: {e}")

# 2. pymodbusでテスト
print("\n2. pymodbusでテスト...")
try:
    client = ModbusClient(
        method='rtu',
        port=MODBUS_PORT,
        baudrate=115200,
        bytesize=8,
        parity='E',
        stopbits=1,
        timeout=1,
        strict=False
    )
    
    if client.connect():
        print(f"✅ Modbusクライアントで接続成功")
        client.close()
    else:
        print(f"❌ Modbusクライアントで接続失敗")
        
except Exception as e:
    print(f"❌ エラー: {e}")

print("\n" + "=" * 70)
