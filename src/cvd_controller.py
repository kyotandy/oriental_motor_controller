import tkinter as tk
from pymodbus.client import ModbusSerialClient as ModbusClient
import serial

from setting import *
from util import *


def modbus_write(address, value, slave):
    upper, lower = decimal_to_hex(value)
    client.write_registers(address, [upper, lower], slave)

def initialize_motor():
    try:
        slave_id = int(entry_id.get())
        client.write_registers(address=0x0066, values=[0xffff, 0xfffb], slave=slave_id)
        status_label.config(text="Initialization successful", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_speed():
    try:
        slave_id = int(entry_id.get())
        speed = int(entry_speed.get())
        client.write_registers(address=0x005e, values=[0, speed], slave=slave_id)
        status_label.config(text="Speed sent successfully", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_step():
    try:
        slave_id = int(entry_id.get())
        step = int(entry_step.get())
        modbus_write(0x005c, step, slave_id)
        status_label.config(text="Step sent successfully", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

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
root.title("Motor Control GUI")

tk.Label(root, text="Motor ID:").grid(row=0, column=0)
entry_id = tk.Entry(root)
entry_id.grid(row=0, column=1)

tk.Label(root, text="Speed:").grid(row=1, column=0)
entry_speed = tk.Entry(root)
entry_speed.grid(row=1, column=1)

tk.Label(root, text="Step:").grid(row=2, column=0)
entry_step = tk.Entry(root)
entry_step.grid(row=2, column=1)

tk.Button(root, text="Initialize", command=initialize_motor).grid(row=3, column=0, columnspan=2)
tk.Button(root, text="Send Speed", command=send_speed).grid(row=4, column=0, columnspan=2)
tk.Button(root, text="Send Step", command=send_step).grid(row=5, column=0, columnspan=2)

status_label = tk.Label(root, text="", fg="blue")
status_label.grid(row=6, column=0, columnspan=2)

root.mainloop()
