import tkinter as tk
from pymodbus.client import ModbusSerialClient as ModbusClient
import serial
from setting import *
from util import *

def modbus_write(address, value, slave):
    upper, lower = decimal_to_hex(value)
    client.write_registers(address, [upper, lower], slave=slave)

def initialize_motors():
    """チェックされたモーターを初期化する"""
    initialized_motors = []
    try:
        for i in range(4):
            if motor_enabled[i].get():
                slave_id = int(entry_ids[i].get())
                client.write_registers(address=0x0066, values=[0xffff, 0xfffb], slave=slave_id)
                initialized_motors.append(slave_id)
        
        if initialized_motors:
            status_label.config(text=f"Motors {', '.join(map(str, initialized_motors))} initialized successfully", fg="green")
        else:
            status_label.config(text="No motors selected for initialization", fg="orange")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_speed():
    """チェックされたモーターにスピードを送信する"""
    processed_motors = []
    try:
        for i in range(4):
            if motor_enabled[i].get():
                slave_id = int(entry_ids[i].get())
                speed = int(entry_speeds[i].get())
                client.write_registers(address=0x005e, values=[0, speed], slave=slave_id)
                processed_motors.append(slave_id)
        
        if processed_motors:
            status_label.config(text=f"Speed sent successfully to motors {', '.join(map(str, processed_motors))}", fg="green")
        else:
            status_label.config(text="No motors selected for speed command", fg="orange")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_step():
    """チェックされたモーターにステップを送信する"""
    processed_motors = []
    try:
        for i in range(4):
            if motor_enabled[i].get():
                slave_id = int(entry_ids[i].get())
                step = int(entry_steps[i].get())
                modbus_write(0x005c, step, slave_id)
                processed_motors.append(slave_id)
        
        if processed_motors:
            status_label.config(text=f"Step sent successfully to motors {', '.join(map(str, processed_motors))}", fg="green")
        else:
            status_label.config(text="No motors selected for step command", fg="orange")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_commands():
    """選択されたコマンドを送信する"""
    if initialize_var.get():
        initialize_motors()
    if speed_var.get():
        send_speed()
    if step_var.get():
        send_step()
    if not any([initialize_var.get(), speed_var.get(), step_var.get()]):
        status_label.config(text="No command selected for sending", fg="orange")

# Modbus接続の設定
client = ModbusClient(
    method=MODBUS_METHOD,
    port=MODBUS_PORT,
    baudrate=MODBUS_BAUDRATE,
    timeout=MODBUS_TIMEOUT,
    parity=MODBUS_PARITY,
    stopbits=MODBUS_STOPBITS
)

# Tkinter GUIの設定
root = tk.Tk()
root.title("Quad Motor Control GUI")

# モーターブロックの作成のための配列
motor_frames = []
motor_enabled = []
entry_ids = []
entry_speeds = []
entry_steps = []

# 各モーターブロックの作成
for i in range(4):
    # モーターブロックのフレーム
    motor_frame = tk.LabelFrame(root, text=f"Motor {i+1}", padx=10, pady=10)
    motor_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
    motor_frames.append(motor_frame)
    
    # モーターの有効/無効チェックボックス
    enabled_var = tk.BooleanVar()
    enabled_var.set(False)
    motor_enabled.append(enabled_var)
    cb_enabled = tk.Checkbutton(motor_frame, text="Enable", variable=enabled_var)
    cb_enabled.grid(row=0, column=0, columnspan=2, sticky="w")
    
    # ID
    tk.Label(motor_frame, text=f"ID:").grid(row=1, column=0, sticky="w")
    id_entry = tk.Entry(motor_frame, width=10)
    id_entry.grid(row=1, column=1, sticky="w")
    id_entry.insert(0, f"{i+1}")  # デフォルトIDを設定
    entry_ids.append(id_entry)
    
    # スピード
    tk.Label(motor_frame, text=f"Speed:").grid(row=2, column=0, sticky="w")
    speed_entry = tk.Entry(motor_frame, width=10)
    speed_entry.grid(row=2, column=1, sticky="w")
    speed_entry.insert(0, "1000")  # デフォルト値
    entry_speeds.append(speed_entry)
    
    # ステップ
    tk.Label(motor_frame, text=f"Step:").grid(row=3, column=0, sticky="w")
    step_entry = tk.Entry(motor_frame, width=10)
    step_entry.grid(row=3, column=1, sticky="w")
    step_entry.insert(0, "1000")  # デフォルト値
    entry_steps.append(step_entry)

# コマンド選択部分
command_frame = tk.LabelFrame(root, text="Commands", padx=10, pady=10)
command_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

initialize_var = tk.BooleanVar()
speed_var = tk.BooleanVar()
step_var = tk.BooleanVar()

tk.Checkbutton(command_frame, text="Initialize Motors", variable=initialize_var).grid(row=0, column=0, padx=5, sticky="w")
tk.Checkbutton(command_frame, text="Send Speed", variable=speed_var).grid(row=0, column=1, padx=5, sticky="w")
tk.Checkbutton(command_frame, text="Send Step", variable=step_var).grid(row=0, column=2, padx=5, sticky="w")

# 送信ボタン
send_button = tk.Button(root, text="Send Commands", command=send_commands, width=20, height=2, bg="#4CAF50", fg="white")
send_button.grid(row=2, column=0, columnspan=4, pady=10)

# ステータス表示
status_label = tk.Label(root, text="Ready", fg="blue")
status_label.grid(row=3, column=0, columnspan=4, pady=10)

# 列と行の重み設定
for i in range(4):
    root.columnconfigure(i, weight=1)
root.rowconfigure(0, weight=3)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)

# GUIを起動
if __name__ == "__main__":
    try:
        # Modbusクライアントを接続
        if client.connect():
            status_label.config(text="Connected to Modbus successfully", fg="green")
        else:
            status_label.config(text="Failed to connect to Modbus", fg="red")
        
        root.mainloop()
    finally:
        # 接続を閉じる
        client.close()