import tkinter as tk
from pymodbus.client import ModbusSerialClient as ModbusClient
import serial

from setting import *
import time
from util import *

def change_motor_id():
    try:
        current_id = int(entry_current_id.get())
        new_id = int(entry_new_id.get())
        
        # Change ID (Write [0, new_id] to address 1380h)
        client.write_registers(address=0x1380, values=[0, new_id], slave=current_id)
        status_label.config(text="ID change completed. Preparing to restart.", fg="green")
        time.sleep(1)
        
        # Restart command (Write [0, 1] to address 0190h)
        client.write_registers(address=0x0192, values=[0, 1], slave=current_id)
        status_label.config(text="Restart command sent. Please wait for device to restart.", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")

# Modbus connection settings
client = ModbusClient(
    method=MODBUS_METHOD,
    port=MODBUS_PORT,
    baudrate=MODBUS_BAUDRATE,
    timeout=MODBUS_TIMEOUT,
    parity=MODBUS_PARITY,
    stopbits=MODBUS_STOPBITS
)

# Tkinter GUI settings
root = tk.Tk()
root.title("Motor ID Change")

tk.Label(root, text="Current ID:").grid(row=0, column=0)
entry_current_id = tk.Entry(root)
entry_current_id.grid(row=0, column=1)

tk.Label(root, text="New ID:").grid(row=1, column=0)
entry_new_id = tk.Entry(root)
entry_new_id.grid(row=1, column=1)

tk.Button(root, text="Change ID", command=change_motor_id).grid(row=2, column=0, columnspan=2)

status_label = tk.Label(root, text="", fg="blue")
status_label.grid(row=3, column=0, columnspan=2)

root.mainloop()
