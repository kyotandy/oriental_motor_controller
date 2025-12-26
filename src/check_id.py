#!/usr/bin/env python3
"""
RS485 Modbus RTU デバイスIDスキャナー
チェーン接続されたドライバのデバイスIDを検出します
"""

import serial
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException
import time

# Modbus設定
MODBUS_METHOD = 'rtu'
MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 115200
MODBUS_TIMEOUT = 1
MODBUS_PARITY = serial.PARITY_EVEN
MODBUS_STOPBITS = serial.STOPBITS_ONE

# デバイスID情報が格納されているアドレス
MODBUS_ID_ADDRESS = 0x1380

# スキャン範囲（Modbusデバイスアドレスは通常1-247）
SCAN_START = 1
SCAN_END = 247

def scan_modbus_devices():
    """
    RS485チェーン上の全デバイスをスキャンしてデバイスIDを検出
    """
    print("=" * 70)
    print("RS485 Modbus RTU デバイスIDスキャナー")
    print("=" * 70)
    print(f"ポート: {MODBUS_PORT}")
    print(f"ボーレート: {MODBUS_BAUDRATE}")
    print(f"パリティ: EVEN")
    print(f"ストップビット: 1")
    print(f"タイムアウト: {MODBUS_TIMEOUT}秒")
    print(f"スキャン範囲: {SCAN_START} - {SCAN_END}")
    print("=" * 70)
    print()
    
    # Modbusクライアント作成
    client = ModbusClient(
        port=MODBUS_PORT,
        baudrate=MODBUS_BAUDRATE,
        timeout=MODBUS_TIMEOUT,
        parity=MODBUS_PARITY,
        stopbits=MODBUS_STOPBITS
    )
    
    # 接続
    if not client.connect():
        print("❌ エラー: Modbusポートに接続できません")
        return
    
    print("✅ Modbusポートに接続しました")
    print()
    print("デバイスをスキャン中...")
    print("-" * 70)
    
    found_devices = []
    
    try:
        for device_id in range(SCAN_START, SCAN_END + 1):
            # プログレス表示（10個ごと）
            if device_id % 10 == 0:
                print(f"スキャン中: {device_id}/{SCAN_END}...", end='\r')
            
            try:
                # デバイスIDアドレスから2レジスタ読み取り
                result = client.read_holding_registers(
                    address=MODBUS_ID_ADDRESS,
                    count=2,
                    slave=device_id  # pymodbusでは'slave'パラメータを使用
                )
                
                # 応答があった場合
                if not result.isError():
                    # レジスタ値を取得
                    registers = result.registers
                    
                    # デバイスIDを計算（2つのレジスタから32ビット値を構成）
                    # 上位16ビット + 下位16ビット
                    device_info_value = (registers[0] << 16) | registers[1]
                    
                    found_devices.append({
                        'address': device_id,
                        'registers': registers,
                        'value': device_info_value
                    })
                    
                    print(f"\n✅ デバイス発見!")
                    print(f"   Modbusアドレス: {device_id}")
                    print(f"   レジスタ値: [{registers[0]:04X}h, {registers[1]:04X}h]")
                    print(f"   結合値: 0x{device_info_value:08X} ({device_info_value})")
                    print("-" * 70)
                    
                # 次のデバイスをスキャンする前に少し待機
                time.sleep(0.05)
                
            except ModbusException as e:
                # タイムアウトや通信エラーは無視（デバイスなし）
                pass
            except Exception as e:
                # その他のエラー
                if device_id % 50 == 0:  # 50個ごとにエラー表示
                    print(f"\n⚠️  アドレス {device_id} でエラー: {e}")
    
    finally:
        client.close()
    
    # 結果サマリー
    print("\n")
    print("=" * 70)
    print("スキャン結果サマリー")
    print("=" * 70)
    
    if found_devices:
        print(f"\n見つかったデバイス数: {len(found_devices)}")
        print()
        print(f"{'Modbusアドレス':<15} {'レジスタ[0]':<15} {'レジスタ[1]':<15} {'結合値(10進)':<20}")
        print("-" * 70)
        
        for device in found_devices:
            print(f"{device['address']:<15} "
                  f"0x{device['registers'][0]:04X} ({device['registers'][0]:<5}) "
                  f"0x{device['registers'][1]:04X} ({device['registers'][1]:<5}) "
                  f"{device['value']:<20}")
    else:
        print("\n⚠️  デバイスが見つかりませんでした")
        print("\n考えられる原因:")
        print("  - RS485配線の問題")
        print("  - ボーレート、パリティなどの設定ミス")
        print("  - デバイスの電源が入っていない")
        print("  - アドレス範囲外にデバイスがある")
    
    print("=" * 70)


if __name__ == "__main__":
    try:
        scan_modbus_devices()
    except KeyboardInterrupt:
        print("\n\n中断されました")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
