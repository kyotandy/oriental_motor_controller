import tkinter as tk
import time
from pymodbus.client import ModbusSerialClient as ModbusClient
import serial
from setting import *
from util import *

# pymodbus のバージョンを確認
import pymodbus
import inspect
print(f"pymodbus version: {pymodbus.__version__}")

# write_registers メソッドのシグネチャを確認
try:
    sig = inspect.signature(ModbusClient.write_registers)
    print(f"write_registers signature: {sig}")
except Exception as e:
    print(f"Could not get signature: {e}")

def test_connection():
    """接続テスト用関数"""
    try:
        slave_id = int(entry_slave_id.get())
        print(f"Testing connection with device ID: {slave_id}")
        
        # 複数のレジスタアドレスでテスト
        test_addresses = [0x001e, 0x0000, 0x0001, 0x0601]
        
        for addr in test_addresses:
            try:
                response = client.read_holding_registers(addr, count=1, device_id=slave_id)
                if not response.isError():
                    print(f"Success reading address 0x{addr:04x}: {response.registers}")
                    status_label.config(text=f"Connection test OK - Address 0x{addr:04x}", fg="green")
                    return
                else:
                    print(f"Error reading address 0x{addr:04x}: {response}")
            except Exception as e:
                print(f"Exception reading address 0x{addr:04x}: {e}")
        
        status_label.config(text="Connection test failed - No response from any address", fg="red")
        
    except Exception as e:
        print(f"Connection test error: {e}")
        status_label.config(text=f"Connection test error: {e}", fg="red")
    upper, lower = decimal_to_hex(value)
    # pymodbus 3.11.0では device_id パラメータを使用
    response = client.write_registers(address, [upper, lower], device_id=slave)
    return response

def initialize_motor():
    try:
        slave_id = int(entry_slave_id.get())
        
        # pymodbus 3.11.0では device_id パラメータを使用
        response1 = client.write_registers(0x001e, [0x2000], device_id=slave_id)
        print(f"Initialize response 1: {response1}")
        time.sleep(0.1)
        
        response2 = client.write_registers(0x0601, [0], device_id=slave_id)
        print(f"Initialize response 2: {response2}")
        time.sleep(0.1)
            
        status_label.config(text="Motor initialized successfully", fg="green")
    except Exception as e:
        print(f"Initialize error: {e}")
        status_label.config(text=f"Error: {e}", fg="red")

def send_speed():
    try:
        speed = int(entry_speed.get())
        slave_id = int(entry_slave_id.get())
        
        response = client.write_registers(0x0502, [0, speed], device_id=slave_id)
        print(f"Send speed response: {response}")
        time.sleep(0.1)
            
        status_label.config(text="Speed sent successfully", fg="green")
    except Exception as e:
        print(f"Send speed error: {e}")
        status_label.config(text=f"Error: {e}", fg="red")

def send_step():
    try:
        step = int(entry_step.get())
        slave_id = int(entry_slave_id.get())
        response = modbus_write(0x0402, step, slave_id)
        print(f"Send step response: {response}")
        status_label.config(text="Step sent successfully", fg="green")
    except Exception as e:
        print(f"Send step error: {e}")
        status_label.config(text=f"Error: {e}", fg="red")

def start_motor():
    try:
        slave_id = int(entry_slave_id.get())
        response = client.write_registers(0x001e, [0x2101], device_id=slave_id)
        print(f"Start motor response: {response}")
            
        status_label.config(text="Motor started", fg="green")
    except Exception as e:
        print(f"Start motor error: {e}")
        status_label.config(text=f"Error: {e}", fg="red")

def stop_motor():
    try:
        slave_id = int(entry_slave_id.get())
        response = client.write_registers(0x001e, [0x2001], device_id=slave_id)
        print(f"Stop motor response: {response}")
            
        status_label.config(text="Motor stopped", fg="green")
    except Exception as e:
        print(f"Stop motor error: {e}")
        status_label.config(text=f"Error: {e}", fg="red")

# Modbus接続の設定
try:
    client = ModbusClient(
        port=MODBUS_PORT,
        baudrate=MODBUS_BAUDRATE,
        timeout=MODBUS_TIMEOUT,
        parity=MODBUS_PARITY,
        stopbits=MODBUS_STOPBITS
    )
    
    # 接続を開く
    if client.connect():
        print("Connected to Modbus device successfully")
        print(f"Connection details: port={MODBUS_PORT}, baudrate={MODBUS_BAUDRATE}")
        
        # 接続テスト（デバイスIDが1のデバイスから何かを読み取ってみる）
        try:
            test_response = client.read_holding_registers(0x001e, count=1, device_id=1)
            print(f"Connection test response: {test_response}")
            if test_response.isError():
                print("Connection test failed - device not responding")
            else:
                print("Connection test successful - device is responding")
        except Exception as test_e:
            print(f"Connection test failed: {test_e}")
            # より詳細な接続テスト
            try:
                # シンプルなテスト - レジスタ1つだけ読む
                simple_test = client.read_input_registers(0, count=1, device_id=1)
                print(f"Simple test response: {simple_test}")
            except Exception as simple_e:
                print(f"Simple test also failed: {simple_e}")
                print("Device may not be connected or settings may be incorrect")
    else:
        print("Failed to connect to Modbus device")
        
except Exception as e:
    print(f"Connection setup error: {e}")
    client = None

# Tkinter GUIの設定
root = tk.Tk()
root.title("Motor Controller 2")

# レイアウトの改善
for i in range(3):
    root.grid_columnconfigure(i, weight=1)

tk.Label(root, text="Slave ID:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
entry_slave_id = tk.Entry(root, width=10)
entry_slave_id.grid(row=0, column=1, sticky="w", padx=5, pady=2)
entry_slave_id.insert(0, "1")

tk.Label(root, text="Speed:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
entry_speed = tk.Entry(root, width=10)
entry_speed.grid(row=1, column=1, sticky="w", padx=5, pady=2)
entry_speed.insert(0, "100")

tk.Label(root, text="Step:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
entry_step = tk.Entry(root, width=10)
entry_step.grid(row=2, column=1, sticky="w", padx=5, pady=2)
entry_step.insert(0, "100")

# ボタン配置
button_width = 15
tk.Button(root, text="Test Connection", command=test_connection, width=button_width).grid(row=3, column=0, columnspan=2, pady=2)
tk.Button(root, text="Initialize", command=initialize_motor, width=button_width).grid(row=4, column=0, columnspan=2, pady=2)
tk.Button(root, text="Send Speed", command=send_speed, width=button_width).grid(row=5, column=0, columnspan=2, pady=2)
tk.Button(root, text="Send Step", command=send_step, width=button_width).grid(row=6, column=0, columnspan=2, pady=2)
tk.Button(root, text="Start Motor", command=start_motor, width=button_width).grid(row=7, column=0, columnspan=2, pady=2)
tk.Button(root, text="Stop Motor", command=stop_motor, width=button_width).grid(row=8, column=0, columnspan=2, pady=2)

# ステータスラベル
status_label = tk.Label(root, text="Ready", fg="blue", wraplength=300)
status_label.grid(row=9, column=0, columnspan=2, pady=10)

# 接続状態表示
if client and hasattr(client, 'is_socket_open'):
    connection_status = "Connected" if client.is_socket_open() else "Disconnected"
else:
    connection_status = "Unknown"

connection_label = tk.Label(root, text=f"Connection: {connection_status}", fg="gray")
connection_label.grid(row=10, column=0, columnspan=2)

# アプリケーション終了時の処理
def on_closing():
    try:
        if client and hasattr(client, 'close'):
            client.close()
            print("Modbus connection closed")
    except Exception as e:
        print(f"Error closing connection: {e}")
    finally:
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# メインループ開始
print("Starting GUI...")
root.mainloop()