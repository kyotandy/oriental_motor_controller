import serial
import time
import pymodbus
from pymodbus.client import ModbusSerialClient as ModbusClient


MODBUS_METHOD = 'rtu'
MODBUS_PORT = '/dev/ttyUSB0'
MODBUS_BAUDRATE = 115200
MODBUS_TIMEOUT = 1
MODBUS_PARITY = serial.PARITY_EVEN
MODBUS_STOPBITS = serial.STOPBITS_ONE
ID = 16

ROTATION_DIRECTION_ADDRESS = 0x0384
ROTATION_DIRECTION = {
    'CW': 1,
    'CCW': 0
}
MODBUS_ID_ADDRESS = 0x1380
NV_MEMORY_WRITE_ADDRESS = 0x0192
CONFIGURATION_EXECUTE_ADDRESS = 0x018c

DIRECT_DRIVE_METHOD_ADDRESS = 0x005a
DIRECT_DRIVE_STEP_ADDRESS = 0x005c
DIRECT_DRIVE_SPEED_ADDRESS = 0x005e
DIRECT_DRIVE_TRIGGER_ADDRESS = 0x0066


client = ModbusClient(
    method=MODBUS_METHOD,
    port=MODBUS_PORT,
    baudrate=MODBUS_BAUDRATE,
    timeout=MODBUS_TIMEOUT,
    parity=MODBUS_PARITY,
    stopbits=MODBUS_STOPBITS
)

client.connect()

client.write_registers(ROTATION_DIRECTION_ADDRESS, [0, 1], 18)
client.write_registers(NV_MEMORY_WRITE_ADDRESS, [0, 1], 18)
res = client.read_holding_registers(MODBUS_ID_ADDRESS, 2, 18)
res.registers


client.write_registers(CONFIGURATION_EXECUTE_ADDRESS, [0, 1], 18)

client.write_registers(0x0192, [0, 1], 16)

# chaange id
def search_modbus_id():
    for i in range(1, 32):
        res = client.read_holding_registers(MODBUS_ID_ADDRESS, 2, i)
        time.sleep(1)
        if type(res) == pymodbus.exceptions.ModbusIOException:
            print(f'id: {i} is not target id')
        else:
            print(res.registers)

    
client.write_registers(MODBUS_ID_ADDRESS, [0, 18], 17)
client.write_registers(NV_MEMORY_WRITE_ADDRESS, [0, 1], 17)