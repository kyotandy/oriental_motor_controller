import serial
import time
import pymodbus
from pymodbus.client import ModbusSerialClient as ModbusClient

# アドレス定数定義
# 指令1：001Eh - 上位Bit5：C-ON、Bit4：STOP、Bit0：START、下位Bit0～Bit5の6ビットで運転データNoの指定
COMMAND_1_ADDR = 0x001E

# 状態1：0020h - 上位Bit5：READY（運転可能かどうか）、Bit2：MOVE（運転中かどうか）、Bit0：STARTの状態、下位Bit7：ALM（アラーム）
STATUS_1_ADDR = 0x0020

# 状態2：0021h - 下位Bit1：ENABLE（モーターが励磁中かどうか）
STATUS_2_ADDR = 0x0021

# 0015h：運転方式
DRIVE_METHOD_ADDR = 0x0015

# 001Ah、001Bh：速度
VELOCITY_H_ADDR = 0x001A
VELOCITY_L_ADDR = 0x001B

# 001Ch、001Dh：位置
POSITION_H_ADDR = 0x001C
POSITION_L_ADDR = 0x001D

# 運転データ領域アドレス
# 位置データ
POSITION_NO1_H_ADDR = 0x0402  # 位置No1上位
POSITION_NO1_L_ADDR = 0x0403  # 位置No1下位
POSITION_NO2_H_ADDR = 0x0404  # 位置No2上位
POSITION_NO2_L_ADDR = 0x0405  # 位置No2下位

# 速度データ
VELOCITY_NO1_H_ADDR = 0x0502  # 速度No1上位
VELOCITY_NO1_L_ADDR = 0x0503  # 速度No1下位
VELOCITY_NO2_H_ADDR = 0x0504  # 速度No2上位
VELOCITY_NO2_L_ADDR = 0x0505  # 速度No2下位

# 運転方式データ
DRIVE_METHOD_NO1_ADDR = 0x0601  # 運転方式No1
DRIVE_METHOD_NO2_ADDR = 0x0602  # 運転方式No2

# ビットマスク定義
C_ON_BIT = 0x20      # Bit5
STOP_BIT = 0x10       # Bit4
START_BIT = 0x01      # Bit0
DATA_NO_MASK = 0x3F   # 下位6ビット（Bit0～Bit5）

READY_BIT = 0x20      # Bit5
MOVE_BIT = 0x04       # Bit2
START_STATUS_BIT = 0x01  # Bit0
ALM_BIT = 0x80        # Bit7

ENABLE_BIT = 0x02     # Bit1

INCREMENT_DRIVE_METHOD = 0x0000
ABSOLUTE_DRIVE_METHOD = 0x0001

DRIVE_NO_UP = 1
DRIVE_NO_DOWN = 2



MODBUS_METHOD = 'rtu'
MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 115200
MODBUS_TIMEOUT = 1
MODBUS_PARITY = serial.PARITY_EVEN
MODBUS_STOPBITS = serial.STOPBITS_ONE


def preset(id, data_no, drive_method, velocity, position):
    """
    運転データをプリセットする関数
    
    Args:
        id (int): デバイスID
        data_no (int): 運転データNo（1または2）
        drive_method (int): 運転方式
        velocity (int): 速度
        position (int): 位置
    
    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        if data_no not in [1, 2]:
            print(f"エラー: 運転データNoは1または2である必要があります。指定値: {data_no}")
            return False
        
        # 運転データNoに応じてアドレスを選択
        if data_no == 1:
            # 運転データNo1の設定
            drive_method_addr = DRIVE_METHOD_NO1_ADDR
            velocity_h_addr = VELOCITY_NO1_H_ADDR
            velocity_l_addr = VELOCITY_NO1_L_ADDR
            position_h_addr = POSITION_NO1_H_ADDR
            position_l_addr = POSITION_NO1_L_ADDR
        else:  # data_no == 2
            # 運転データNo2の設定
            drive_method_addr = DRIVE_METHOD_NO2_ADDR
            velocity_h_addr = VELOCITY_NO2_H_ADDR
            velocity_l_addr = VELOCITY_NO2_L_ADDR
            position_h_addr = POSITION_NO2_H_ADDR
            position_l_addr = POSITION_NO2_L_ADDR
        
        # 運転方式を設定
        client.write_registers(address=drive_method_addr, values=[drive_method], device_id=id)
        
        # 速度を設定（上位・下位に分割）
        velocity_high = (velocity >> 16) & 0xFFFF
        velocity_low = velocity & 0xFFFF
        client.write_registers(address=velocity_h_addr, values=[velocity_high], device_id=id)
        client.write_registers(address=velocity_l_addr, values=[velocity_low], device_id=id)
        
        # 位置を設定（上位・下位に分割）
        position_high = (position >> 16) & 0xFFFF
        position_low = position & 0xFFFF
        client.write_registers(address=position_h_addr, values=[position_high], device_id=id)
        client.write_registers(address=position_l_addr, values=[position_low], device_id=id)
        
        print(f"運転データNo{data_no}を設定しました: 速度={velocity}, 位置={position}, 運転方式={drive_method}")
        
        return True
    except Exception as e:
        print(f"プリセットエラー: {e}")
        return False


def start(id, data_no):
    """
    モーターを起動する関数
    
    Args:
        id (int): デバイスID
        data_no (int): 運転データNo（0-63）
    
    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        # 運転データNoを上位ビット（Bit8-13）に設定し、C-ONとSTARTをON
        command_value = ((data_no & DATA_NO_MASK) << 8) | C_ON_BIT | START_BIT
        print(f"起動コマンド: 0x{command_value:04X}")
        
        # 指令1に設定
        client.write_registers(address=COMMAND_1_ADDR, values=[command_value], device_id=id)
        
        # 少し待機
        time.sleep(0.1)
        
        # STARTをOFFにしてC-ONのみONの状態にする
        command_value = ((data_no & DATA_NO_MASK) << 8) | C_ON_BIT
        print(f"維持コマンド: 0x{command_value:04X}")
        client.write_registers(address=COMMAND_1_ADDR, values=[command_value], device_id=id)
        
        return True
    except Exception as e:
        print(f"起動エラー: {e}")
        return False

def excite(id):
    """
    モーターを励磁する関数
    """
    try:
        # 現在の指令値を読み取り
        command_result = client.read_holding_registers(address=COMMAND_1_ADDR, count=1, device_id=id)
        current_command = command_result.registers[0] if not command_result.isError() else 0
        
        # C-ONビットを追加（運転データNoは保持）
        command_value = (current_command & 0xFF00) | C_ON_BIT
        client.write_registers(address=COMMAND_1_ADDR, values=[command_value], device_id=id)
        return True
    except Exception as e:
        print(f"励磁エラー: {e}")
        return False

def status(id):
    """
    モーターの状態を取得する関数
    
    Args:
        id (int): デバイスID
    
    Returns:
        dict: 状態情報の辞書
    """
    try:
        # 状態1を読み取り
        status1_result = client.read_holding_registers(address=STATUS_1_ADDR, count=1, device_id=id)
        status1 = status1_result.registers[0] if status1_result.isError() == False else 0
        
        # 状態2を読み取り
        status2_result = client.read_holding_registers(address=STATUS_2_ADDR, count=1, device_id=id)
        status2 = status2_result.registers[0] if status2_result.isError() == False else 0
        
        # 状態を解析
        status_info = {
            'ready': bool(status1 & READY_BIT),      # 運転可能かどうか
            'move': bool(status1 & MOVE_BIT),        # 運転中かどうか
            'start_status': bool(status1 & START_STATUS_BIT),  # STARTの状態
            'alarm': bool(status1 & ALM_BIT),        # アラーム
            'enable': bool(status2 & ENABLE_BIT),    # モーター励磁中かどうか
            'status1_raw': status1,
            'status2_raw': status2
        }
        
        return status_info
    except Exception as e:
        print(f"状態取得エラー: {e}")
        return None


def get_drive_data(id, data_no):
    """
    運転データ領域を確認する関数
    
    Args:
        id (int): デバイスID
        data_no (int): 運転データNo（1または2）
    
    Returns:
        dict: 運転データ情報の辞書
    """
    try:
        if data_no not in [1, 2]:
            print(f"エラー: 運転データNoは1または2である必要があります。指定値: {data_no}")
            return None
        
        # アドレスを選択
        if data_no == 1:
            position_h_addr = POSITION_NO1_H_ADDR
            position_l_addr = POSITION_NO1_L_ADDR
            velocity_h_addr = VELOCITY_NO1_H_ADDR
            velocity_l_addr = VELOCITY_NO1_L_ADDR
            drive_method_addr = DRIVE_METHOD_NO1_ADDR
        else:  # data_no == 2
            position_h_addr = POSITION_NO2_H_ADDR
            position_l_addr = POSITION_NO2_L_ADDR
            velocity_h_addr = VELOCITY_NO2_H_ADDR
            velocity_l_addr = VELOCITY_NO2_L_ADDR
            drive_method_addr = DRIVE_METHOD_NO2_ADDR
        
        # 位置データを読み取り
        position_h_result = client.read_holding_registers(address=position_h_addr, count=1, device_id=id)
        position_h = position_h_result.registers[0] if not position_h_result.isError() else 0
        
        position_l_result = client.read_holding_registers(address=position_l_addr, count=1, device_id=id)
        position_l = position_l_result.registers[0] if not position_l_result.isError() else 0
        
        # 32ビット位置値を構築
        position = (position_h << 16) | position_l
        # 負の値の処理（2の補数）
        if position > 0x7FFFFFFF:
            position = position - 0x100000000
        
        # 速度データを読み取り
        velocity_h_result = client.read_holding_registers(address=velocity_h_addr, count=1, device_id=id)
        velocity_h = velocity_h_result.registers[0] if not velocity_h_result.isError() else 0
        
        velocity_l_result = client.read_holding_registers(address=velocity_l_addr, count=1, device_id=id)
        velocity_l = velocity_l_result.registers[0] if not velocity_l_result.isError() else 0
        
        # 32ビット速度値を構築
        velocity = (velocity_h << 16) | velocity_l
        # 負の値の処理（2の補数）
        if velocity > 0x7FFFFFFF:
            velocity = velocity - 0x100000000
        
        # 運転方式を読み取り
        drive_method_result = client.read_holding_registers(address=drive_method_addr, count=1, device_id=id)
        drive_method = drive_method_result.registers[0] if not drive_method_result.isError() else 0
        
        # 運転データ情報を構築
        drive_data = {
            'data_no': data_no,
            'position': position,
            #'position_high': position_h,
            #'position_low': position_l,
            'velocity': velocity,
            #'velocity_high': velocity_h,
            #'velocity_low': velocity_l,
            #'drive_method': drive_method,
            'drive_method_name': 'INCREMENT' if drive_method == INCREMENT_DRIVE_METHOD else 'ABSOLUTE' if drive_method == ABSOLUTE_DRIVE_METHOD else f'UNKNOWN({drive_method})'
        }
        
        return drive_data
    except Exception as e:
        print(f"運転データ取得エラー: {e}")
        return None


def get_all_drive_data(id):
    """
    全ての運転データ領域を確認する関数
    
    Args:
        id (int): デバイスID
    
    Returns:
        dict: 全運転データ情報の辞書
    """
    try:
        drive_data_1 = get_drive_data(id, 1)
        drive_data_2 = get_drive_data(id, 2)
        
        all_data = {
            'device_id': id,
            'drive_data_1': drive_data_1,
            'drive_data_2': drive_data_2
        }
        
        return all_data
    except Exception as e:
        print(f"全運転データ取得エラー: {e}")
        return None


def start_manual(id, data_no):
    """
    手動でモーターを起動する関数（実際に動作したコマンドを使用）
    
    Args:
        id (int): デバイスID
        data_no (int): 運転データNo（1または2）
    
    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        # 実際に動作したコマンドを使用
        if data_no == 1:
            # 0x2101: C-ON + START + 運転データNo1
            start_command = 0x2101
            # 0x2001: C-ON + 運転データNo1
            maintain_command = 0x2001
        elif data_no == 2:
            # 0x2202: C-ON + START + 運転データNo2
            start_command = 0x2102
            # 0x2002: C-ON + 運転データNo2
            maintain_command = 0x2002
        else:
            print(f"エラー: 運転データNoは1または2である必要があります。指定値: {data_no}")
            return False
        
        client.write_registers(address=COMMAND_1_ADDR, values=[0x2000], device_id=id)
        time.sleep(0.1)
        
        print(f"手動起動コマンド: 0x{start_command:04X}")
        client.write_registers(address=COMMAND_1_ADDR, values=[start_command], device_id=id)
        
        # 少し待機
        time.sleep(0.1)
        
        print(f"手動維持コマンド: 0x{maintain_command:04X}")
        client.write_registers(address=COMMAND_1_ADDR, values=[maintain_command], device_id=id)
        
        return True
    except Exception as e:
        print(f"手動起動エラー: {e}")
        return False


client = ModbusClient(
    port=MODBUS_PORT,
    baudrate=MODBUS_BAUDRATE,
    timeout=MODBUS_TIMEOUT,
    parity=MODBUS_PARITY,
    stopbits=MODBUS_STOPBITS
)

client.connect()

preset(2, DRIVE_NO_UP, ABSOLUTE_DRIVE_METHOD, 1000, 0)
time.sleep(0.5)
preset(2, DRIVE_NO_DOWN, ABSOLUTE_DRIVE_METHOD, 1000, 15000)
time.sleep(0.5)
preset(3, DRIVE_NO_UP, ABSOLUTE_DRIVE_METHOD, 1000, 0)
time.sleep(0.5)
preset(3, DRIVE_NO_DOWN, ABSOLUTE_DRIVE_METHOD, 1000, 15000)
time.sleep(0.5)
preset(4, DRIVE_NO_UP, ABSOLUTE_DRIVE_METHOD, 1000, 0)
time.sleep(0.5)
preset(4, DRIVE_NO_DOWN, ABSOLUTE_DRIVE_METHOD, 1000, 15000)
time.sleep(0.5)
preset(5, DRIVE_NO_UP, ABSOLUTE_DRIVE_METHOD, 1000, 0)
time.sleep(0.5)
preset(5, DRIVE_NO_DOWN, ABSOLUTE_DRIVE_METHOD, 1000, 15000)
time.sleep(0.5)
preset(6, DRIVE_NO_UP, ABSOLUTE_DRIVE_METHOD, 1000, 0)
time.sleep(0.5)
preset(6, DRIVE_NO_DOWN, ABSOLUTE_DRIVE_METHOD, 1000, 15000)
time.sleep(0.5)
preset(7, DRIVE_NO_UP, ABSOLUTE_DRIVE_METHOD, 1000, 0)
time.sleep(0.5)
preset(7, DRIVE_NO_DOWN, ABSOLUTE_DRIVE_METHOD, 1000, 15000)


start(2, DRIVE_NO_UP)
start(3, DRIVE_NO_UP)
start(4, DRIVE_NO_UP)
start(5, DRIVE_NO_UP)
start(6, DRIVE_NO_UP)
start(7, DRIVE_NO_UP)

excite(2)
time.sleep(0.1)
excite(3)
time.sleep(0.1)
excite(4)
time.sleep(0.1)
excite(5)
time.sleep(0.1)
excite(6)
time.sleep(0.1)
excite(7)   


status(2)
time.sleep(0.1)
status(3)
time.sleep(0.1)
status(4)
time.sleep(0.1)
status(5)
time.sleep(0.1)
status(6)
time.sleep(0.1)
status(7)

start_manual(2, DRIVE_NO_UP)
start_manual(3, DRIVE_NO_UP)
start_manual(4, DRIVE_NO_UP)
start_manual(5, DRIVE_NO_UP)
start_manual(6, DRIVE_NO_UP)
start_manual(7, DRIVE_NO_UP)


get_all_drive_data(2)
time.sleep(0.5)
get_all_drive_data(3)
time.sleep(0.5)
get_all_drive_data(4)
time.sleep(0.5)
get_all_drive_data(5)
time.sleep(0.5)
get_all_drive_data(6)
time.sleep(0.5)
get_all_drive_data(7)


#=====================
id=5
client.write_registers(address=COMMAND_1_ADDR, values=[0x2000], device_id=id)
client.write_registers(address=COMMAND_1_ADDR, values=[0x2101], device_id=id)
client.write_registers(address=COMMAND_1_ADDR, values=[0x2001], device_id=id)
client.write_registers(address=COMMAND_1_ADDR, values=[0x2102], device_id=id)
client.write_registers(address=COMMAND_1_ADDR, values=[0x2002], device_id=id)

