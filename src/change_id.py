#!/usr/bin/env python3
import serial
import time
import sys
from pymodbus.client import ModbusSerialClient as ModbusClient

# 通信設定（環境に合わせて固定）
MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 115200
MODBUS_PARITY = serial.PARITY_EVEN

# オリエンタルモーター パラメータアドレス (AZシリーズ等)
ADDR_SLAVE_ID = 0x1380           # スレーブID設定レジスタ
ADDR_NV_BATCH_WRITE = 0x0192     # NVメモリ一括書き込み（RAM → 不揮発）

def set_new_slave_id(current_id, new_id):
    client = ModbusClient(
        port=MODBUS_PORT,
        baudrate=MODBUS_BAUDRATE,
        parity=MODBUS_PARITY,
        timeout=1,
        retries=3
    )

    if not client.connect():
        print(f"エラー: ポート {MODBUS_PORT} を開けませんでした。")
        return

    try:
        print(f"現在のID({current_id}) への通信を開始します...")
        print(f"新しいID({new_id}) を書き込み中...")

        # 1. 新しいSlave IDを書き込む (32bitレジスタ [上位16bit, 下位16bit])
        # 以前成功したコードに合わせ、引数名は slave (または device_id) を使用
        write_res = client.write_registers(address=ADDR_SLAVE_ID, values=[0, new_id], device_id=current_id)
        
        if write_res.isError():
            print(f"ID書き込みエラー: {write_res}")
            return

        time.sleep(0.5)
        print("NVメモリ一括書き込みを実行中...")

        # 2. NVメモリ一括書き込み（32bit: [0, 1]）。通信パラメータは構成設定不要で、電源再投入で反映
        nv_res = client.write_registers(address=ADDR_NV_BATCH_WRITE, values=[0, 1], device_id=current_id)

        if nv_res.isError():
            print(f"NV書き込みエラー: {nv_res}")
            print("RAM上のみ変更されている可能性があります。電源再投入すると元のIDに戻ります。")
        else:
            print("=" * 60)
            print(f"成功！ ID: {current_id} → {new_id} をNVに保存しました。")
            print(f"電源を再投入すると ID: {new_id} で通信してください。")
            print("=" * 60)

    except Exception as e:
        print(f"通信中にエラーが発生しました: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # 引数のチェック
    if len(sys.argv) != 3:
        print("使用法: python3 src/set_id.py [現在のID] [新しいID]")
        print("例: python3 src/set_id.py 1 2")
        sys.exit(1)

    try:
        arg1 = int(sys.argv[1])
        arg2 = int(sys.argv[2])
        
        # IDの範囲バリデーション (1-31)
        if not (1 <= arg1 <= 31 and 1 <= arg2 <= 31):
            print("エラー: IDは1から31の範囲で指定してください。")
            sys.exit(1)
            
        set_new_slave_id(arg1, arg2)
        
    except ValueError:
        print("エラー: IDには数値を指定してください。")
        sys.exit(1)
