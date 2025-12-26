import serial
import time
from pymodbus.client import ModbusSerialClient as ModbusClient

# 通信設定
MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 115200
MODBUS_PARITY = serial.PARITY_EVEN

# 現在のIDと新しく設定したいID
CURRENT_ID = 1   # スキャンで見つかった現在のID
NEW_ID = 2       # 新しく設定したいID（1-31）

# オリエンタルモーター パラメータアドレス (AZシリーズ例)
ADDR_SLAVE_ID = 0x1380        # スレーブID設定レジスタ
NV_MEMORY_WRITE_ADDRESS = 0x0192

def set_new_slave_id():
    client = ModbusClient(
        port=MODBUS_PORT,
        baudrate=MODBUS_BAUDRATE,
        parity=MODBUS_PARITY,
        timeout=1,
        retries=3
    )

    if not client.connect():
        print("ポートを開けませんでした。")
        return

    try:
        print(f"現在のID({CURRENT_ID}) から 新しいID({NEW_ID}) への書き換えを開始します...")

        # 1. 新しい局番号(Slave ID)を書き込む
        # 32bitレジスタのため、count=2で書き込みます
        # [0, NEW_ID] の順で送るのが一般的です
        write_res = client.write_registers(address=ADDR_SLAVE_ID, values=[0, NEW_ID], device_id=CURRENT_ID)
        
        if write_res.isError():
            print(f"IDの書き込みに失敗しました: {write_res}")
            return

        print("IDの書き込み成功。設定を反映させるために『構成設定』コマンドを送信します...")
        time.sleep(0.5)

        # 2. 構成設定(Config)を実行して不揮発メモリに保存・反映
        # 0x007Cに 1 を書き込む
        config_res = client.write_register(address=NV_MEMORY_WRITE_ADDRESS, value=1, device_id=CURRENT_ID)

        if config_res.isError():
            print(f"構成設定コマンドの送信に失敗しました。電源の再投入を行ってください。")
        else:
            print("構成設定完了。")
            print("=" * 50)
            print(f"完了！ 次回の接続からは ID: {NEW_ID} を使用してください。")
            print("※反映されない場合は、一度ドライバの電源を切って再投入してください。")
            print("=" * 50)

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    set_new_slave_id()
