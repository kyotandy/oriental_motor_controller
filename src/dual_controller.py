import tkinter as tk
from pymodbus.client import ModbusSerialClient as ModbusClient
import serial
from setting import *
from util import *

def modbus_write(address, value, slave):
    upper, lower = decimal_to_hex(value)
    client.write_registers(address, [upper, lower], slave=slave)

def initialize_motors():
    try:
        slave_id1 = int(entry_id1.get())
        client.write_registers(address=0x0066, values=[0xffff, 0xfffb], slave=slave_id1)
        
        if enable_dual_motor.get():
            slave_id2 = int(entry_id2.get())
            client.write_registers(address=0x0066, values=[0xffff, 0xfffb], slave=slave_id2)
            status_label.config(text=f"Motors {slave_id1} and {slave_id2} initialized successfully", fg="green")
        else:
            status_label.config(text=f"Motor {slave_id1} initialized successfully", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_speed():
    try:
        slave_id1 = int(entry_id1.get())
        speed1 = int(entry_speed1.get())
        client.write_registers(address=0x005e, values=[0, speed1], slave=slave_id1)
        
        if enable_dual_motor.get():
            slave_id2 = int(entry_id2.get())
            speed2 = int(entry_speed2.get())
            client.write_registers(address=0x005e, values=[0, speed2], slave=slave_id2)
            status_label.config(text=f"Speed sent successfully to motors {slave_id1} and {slave_id2}", fg="green")
        else:
            status_label.config(text=f"Speed sent successfully to motor {slave_id1}", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_step():
    try:
        slave_id1 = int(entry_id1.get())
        step1 = int(entry_step1.get())
        modbus_write(0x005c, step1, slave_id1)
        
        if enable_dual_motor.get():
            slave_id2 = int(entry_id2.get())
            step2 = int(entry_step2.get())
            modbus_write(0x005c, step2, slave_id2)
            status_label.config(text=f"Step sent successfully to motors {slave_id1} and {slave_id2}", fg="green")
        else:
            status_label.config(text=f"Step sent successfully to motor {slave_id1}", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def toggle_dual_motor():
    if enable_dual_motor.get():
        # 2台目のモーターのコントロールを表示
        label_id2.grid(row=0, column=3)
        entry_id2.grid(row=0, column=4)
        label_speed2.grid(row=1, column=3)
        entry_speed2.grid(row=1, column=4)
        label_step2.grid(row=2, column=3)
        entry_step2.grid(row=2, column=4)
    else:
        # 2台目のモーターのコントロールを非表示
        label_id2.grid_remove()
        entry_id2.grid_remove()
        label_speed2.grid_remove()
        entry_speed2.grid_remove()
        label_step2.grid_remove()
        entry_step2.grid_remove()

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
root.title("Dual Motor Control GUI")

# モーター1のコントロール
tk.Label(root, text="-- Motor 1 --", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, columnspan=2)
label_id1 = tk.Label(root, text="Motor 1 ID:")
label_id1.grid(row=1, column=0)
entry_id1 = tk.Entry(root)
entry_id1.grid(row=1, column=1)

label_speed1 = tk.Label(root, text="Speed 1:")
label_speed1.grid(row=2, column=0)
entry_speed1 = tk.Entry(root)
entry_speed1.grid(row=2, column=1)

label_step1 = tk.Label(root, text="Step 1:")
label_step1.grid(row=3, column=0)
entry_step1 = tk.Entry(root)
entry_step1.grid(row=3, column=1)

# セパレーター
tk.Frame(root, width=2, bg='gray', height=150).grid(row=0, column=2, rowspan=6, padx=10)

# モーター2のコントロール（最初は非表示）
tk.Label(root, text="-- Motor 2 --", font=('Helvetica', 10, 'bold')).grid(row=0, column=3, columnspan=2)
label_id2 = tk.Label(root, text="Motor 2 ID:")
entry_id2 = tk.Entry(root)

label_speed2 = tk.Label(root, text="Speed 2:")
entry_speed2 = tk.Entry(root)

label_step2 = tk.Label(root, text="Step 2:")
entry_step2 = tk.Entry(root)

# デュアルモーター制御の有効化チェックボックス
enable_dual_motor = tk.BooleanVar()
enable_dual_motor.set(False)
cb_dual_motor = tk.Checkbutton(root, text="Enable Dual Motor Control", variable=enable_dual_motor, command=toggle_dual_motor)
cb_dual_motor.grid(row=4, column=0, columnspan=5, pady=10)

# 操作ボタン
button_frame = tk.Frame(root)
button_frame.grid(row=5, column=0, columnspan=5, pady=10)

tk.Button(button_frame, text="Initialize Motors", command=initialize_motors, width=15).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Send Speed", command=send_speed, width=15).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Send Step", command=send_step, width=15).grid(row=0, column=2, padx=5)

# ステータス表示
status_label = tk.Label(root, text="Ready", fg="blue")
status_label.grid(row=6, column=0, columnspan=5, pady=10)

# GUIを起動
root.mainloop()