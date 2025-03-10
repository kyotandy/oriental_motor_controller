import tkinter as tk
import time
from pymodbus.client import ModbusSerialClient as ModbusClient
import serial

from setting import *
from util import *


def modbus_write(address, value, slave):
    upper, lower = decimal_to_hex(value)
    client.write_registers(address, [upper, lower], slave)

def initialize_motor():
    try:
        slave_id = int(entry_slave_id.get())
        client.write_registers(address=0x001e, values=[0x2000], slave=slave_id)
        time.sleep(0.1)
        client.write_registers(address=0x0601, values=[0], slave=slave_id)
        time.sleep(0.1)
        status_label.config(text="Motor initialized successfully", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_speed():
    try:
        speed = int(entry_speed.get())
        slave_id = int(entry_slave_id.get())
        client.write_registers(address=0x0502, values=[0, speed], slave=slave_id)
        time.sleep(0.1)
        status_label.config(text="Speed sent successfully", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def send_step():
    try:
        step = int(entry_step.get())
        slave_id = int(entry_slave_id.get())
        modbus_write(0x0402, step, slave_id)
        status_label.config(text="Step sent successfully", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def start_motor():
    try:
        slave_id = int(entry_slave_id.get())
        client.write_registers(address=0x001e, values=[0x2101], slave=slave_id)
        status_label.config(text="Motor started", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

def stop_motor():
    try:
        slave_id = int(entry_slave_id.get())
        client.write_registers(address=0x001e, values=[0x2001], slave=slave_id)
        status_label.config(text="Motor stopped", fg="green")
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
root.title("Motor Controller 2")

tk.Label(root, text="Slave ID:").grid(row=0, column=0)
entry_slave_id = tk.Entry(root)
entry_slave_id.grid(row=0, column=1)

tk.Label(root, text="Speed:").grid(row=1, column=0)
entry_speed = tk.Entry(root)
entry_speed.grid(row=1, column=1)

tk.Label(root, text="Step:").grid(row=2, column=0)
entry_step = tk.Entry(root)
entry_step.grid(row=2, column=1)

tk.Button(root, text="Initialize", command=initialize_motor).grid(row=3, column=0, columnspan=2)
tk.Button(root, text="Send Speed", command=send_speed).grid(row=4, column=0, columnspan=2)
tk.Button(root, text="Send Step", command=send_step).grid(row=5, column=0, columnspan=2)
tk.Button(root, text="Start Motor", command=start_motor).grid(row=6, column=0, columnspan=2)
tk.Button(root, text="Stop Motor", command=stop_motor).grid(row=7, column=0, columnspan=2)

status_label = tk.Label(root, text="", fg="blue")
status_label.grid(row=8, column=0, columnspan=2)

root.mainloop()
