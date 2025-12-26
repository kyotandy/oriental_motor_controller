#!/usr/bin/env python3
"""
RS485 Modbus RTU デバイスID変更ツール
指定したデバイスのIDを変更し、不揮発性メモリに保存します
"""

import serial
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException
import time
import sys

# Modbus設定
MODBUS_METHOD = 'rtu'
MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 115200
MODBUS_TIMEOUT = 1
MODBUS_PARITY = serial.PARITY_EVEN
MODBUS_STOPBITS = serial.STOPBITS_ONE

# デバイスID情報が格納されているアドレス
MODBUS_ID_ADDRESS = 0x1380

# 不揮発性メモリ書き込みアドレス
NV_MEMORY_WRITE_ADDRESS = 0x0192


def read_device_id(client, device_address):
    """
    現在のデバイスIDを読み取る
    
    Args:
        client: Modbusクライアント
        device_address: デバイスのModbusアドレス
    
    Returns:
        tuple: (register0, register1, combined_value) または None
    """
    try:
        result = client.read_holding_registers(
            address=MODBUS_ID_ADDRESS,
            count=2,
            slave=device_address
        )
        
        if not result.isError():
            registers = result.registers
            combined_value = (registers[0] << 16) | registers[1]
            return (registers[0], registers[1], combined_value)
        else:
            return None
    except Exception as e:
        print(f"❌ 読み取りエラー: {e}")
        return None


def write_device_id(client, device_address, new_id_high, new_id_low):
    """
    新しいデバイスIDを書き込む
    
    Args:
        client: Modbusクライアント
        device_address: 現在のデバイスのModbusアドレス
        new_id_high: 新しいID上位16ビット
        new_id_low: 新しいID下位16ビット
    
    Returns:
        bool: 成功したらTrue
    """
    try:
        # デバイスIDを書き込む
        result = client.write_registers(
            address=MODBUS_ID_ADDRESS,
            values=[new_id_high, new_id_low],
            slave=device_address
        )
        
        if result.isError():
            print(f"❌ ID書き込みエラー")
            return False
        
        print(f"✅ ID書き込み成功")
        
        # 少し待機
        time.sleep(0.1)
        
        # 不揮発性メモリに保存
        print(f"💾 不揮発性メモリに保存中...")
        nv_result = client.write_registers(
            address=NV_MEMORY_WRITE_ADDRESS,
            values=[0, 1],
            slave=device_address
        )
        
        if nv_result.isError():
            print(f"❌ 不揮発性メモリ書き込みエラー")
            return False
        
        print(f"✅ 不揮発性メモリ保存成功")
        
        # 保存処理完了を待つ
        time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"❌ 書き込みエラー: {e}")
        return False


def change_device_id_interactive():
    """
    インタラクティブにデバイスIDを変更
    """
    print("=" * 70)
    print("RS485 Modbus RTU デバイスID変更ツール")
    print("=" * 70)
    print(f"ポート: {MODBUS_PORT}")
    print(f"ボーレート: {MODBUS_BAUDRATE}")
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
    
    try:
        # 現在のModbusアドレスを入力
        current_address = int(input("変更するデバイスの現在のModbusアドレスを入力 (1-247): "))
        
        if current_address < 1 or current_address > 247:
            print("❌ 無効なアドレスです")
            return
        
        print()
        print(f"デバイス (Modbusアドレス: {current_address}) の現在のIDを読み取り中...")
        
        # 現在のIDを読み取り
        current_id = read_device_id(client, current_address)
        
        if current_id is None:
            print(f"❌ デバイスが応答しません。アドレスを確認してください。")
            return
        
        reg0, reg1, combined = current_id
        print(f"✅ 現在のID: [0x{reg0:04X}, 0x{reg1:04X}] = 0x{combined:08X} ({combined})")
        print()
        
        # 新しいIDを入力
        print("新しいIDを入力してください:")
        print("  方法1: 2つのレジスタ値を個別に入力")
        print("  方法2: 32ビット値を1つ入力")
        print()
        
        input_method = input("入力方法を選択 (1 または 2): ").strip()
        
        if input_method == "1":
            # 2つのレジスタ値を入力
            new_id_high = int(input("新しいID 上位16ビット (0-65535 または 0x形式): "), 0)
            new_id_low = int(input("新しいID 下位16ビット (0-65535 または 0x形式): "), 0)
            
            if new_id_high < 0 or new_id_high > 0xFFFF or new_id_low < 0 or new_id_low > 0xFFFF:
                print("❌ 無効な値です")
                return
                
        elif input_method == "2":
            # 32ビット値を入力
            new_id_combined = int(input("新しいID 32ビット値 (0-4294967295 または 0x形式): "), 0)
            
            if new_id_combined < 0 or new_id_combined > 0xFFFFFFFF:
                print("❌ 無効な値です")
                return
            
            # 上位16ビットと下位16ビットに分割
            new_id_high = (new_id_combined >> 16) & 0xFFFF
            new_id_low = new_id_combined & 0xFFFF
        else:
            print("❌ 無効な選択です")
            return
        
        new_combined = (new_id_high << 16) | new_id_low
        
        print()
        print("-" * 70)
        print("変更内容の確認:")
        print(f"  現在のID: [0x{reg0:04X}, 0x{reg1:04X}] = 0x{combined:08X} ({combined})")
        print(f"  新しいID: [0x{new_id_high:04X}, 0x{new_id_low:04X}] = 0x{new_combined:08X} ({new_combined})")
        print("-" * 70)
        print()
        
        confirm = input("この内容で変更してよろしいですか? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("キャンセルしました")
            return
        
        print()
        print("デバイスIDを変更中...")
        print("-" * 70)
        
        # IDを変更
        if write_device_id(client, current_address, new_id_high, new_id_low):
            print("-" * 70)
            print()
            print("🎉 デバイスIDの変更が完了しました!")
            print()
            print("⚠️  注意:")
            print("  - デバイスの電源を再投入してください")
            print("  - または、デバイスをリセットしてください")
            print("  - 変更後は新しいIDでアクセスする必要があります")
        else:
            print()
            print("❌ デバイスIDの変更に失敗しました")
    
    except ValueError:
        print("❌ 無効な入力です")
    except KeyboardInterrupt:
        print("\n\nキャンセルしました")
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


def change_device_id_command_line(current_address, new_id_high, new_id_low):
    """
    コマンドラインからデバイスIDを変更
    
    Args:
        current_address: 現在のModbusアドレス
        new_id_high: 新しいID上位16ビット
        new_id_low: 新しいID下位16ビット
    """
    print("=" * 70)
    print("RS485 Modbus RTU デバイスID変更ツール (コマンドラインモード)")
    print("=" * 70)
    
    client = ModbusClient(
        port=MODBUS_PORT,
        baudrate=MODBUS_BAUDRATE,
        timeout=MODBUS_TIMEOUT,
        parity=MODBUS_PARITY,
        stopbits=MODBUS_STOPBITS
    )
    
    if not client.connect():
        print("❌ エラー: Modbusポートに接続できません")
        return False
    
    try:
        # 現在のIDを読み取り
        print(f"現在のIDを読み取り中... (アドレス: {current_address})")
        current_id = read_device_id(client, current_address)
        
        if current_id is None:
            print(f"❌ デバイスが応答しません")
            return False
        
        reg0, reg1, combined = current_id
        new_combined = (new_id_high << 16) | new_id_low
        
        print(f"現在のID: 0x{combined:08X} ({combined})")
        print(f"新しいID: 0x{new_combined:08X} ({new_combined})")
        print()
        
        # IDを変更
        if write_device_id(client, current_address, new_id_high, new_id_low):
            print()
            print("🎉 変更完了!")
            return True
        else:
            return False
            
    finally:
        client.close()


if __name__ == "__main__":
    if len(sys.argv) == 4:
        # コマンドライン引数モード
        # 使用例: python3 change_device_id.py 1 0x0012 0x3456
        try:
            current_addr = int(sys.argv[1])
            new_high = int(sys.argv[2], 0)
            new_low = int(sys.argv[3], 0)
            change_device_id_command_line(current_addr, new_high, new_low)
        except ValueError:
            print("使用法: python3 change_device_id.py <現在のアドレス> <新ID上位> <新ID下位>")
            print("例: python3 change_device_id.py 1 0x0012 0x3456")
    else:
        # インタラクティブモード
        change_device_id_interactive()
