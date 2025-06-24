# Motor Controller GUI Collection

A comprehensive collection of Python GUI applications for controlling stepper motors via Modbus RTU communication. This project provides various interfaces for controlling single, dual, quad, octa, and up to 28 motors simultaneously.

## Features

- **Multiple Motor Control Options**: Support for 1, 2, 4, 6, and 28 motor configurations
- **Modbus RTU Communication**: Serial communication with motor controllers
- **Intuitive GUI Interface**: Tkinter-based graphical user interfaces
- **Motor ID Configuration**: Change motor IDs dynamically
- **Batch Operations**: Send commands to multiple motors simultaneously
- **Real-time Status Feedback**: Visual status indicators for operations

## Project Structure

```
src/
├── all_controller.py      # 28-motor control interface
├── cvd_change_config.py   # Motor ID configuration tool
├── cvd_controller.py      # Single motor control interface
├── dual_controller.py     # Dual motor control interface
├── lrd_controller.py      # Alternative single motor controller
├── manual.py              # Manual Modbus operations
├── octa_controller.py     # Six motor control interface
├── quad_controller.py     # Quad motor control interface
├── requirements.txt       # Python dependencies
├── setting.py             # Modbus configuration settings
└── util.py                # Utility functions
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd motor-controller
```

2. Install required dependencies:
```bash
pip install -r src/requirements.txt
```

3. Ensure your system has access to the serial port (typically `/dev/ttyUSB0` on Linux).

## Hardware Requirements

- **Serial Interface**: USB-to-RS485 converter or similar
- **Motor Controllers**: Modbus RTU compatible stepper motor controllers
- **Connection**: RS485 bus connecting all motor controllers

## Configuration

### Modbus Settings

Edit `src/setting.py` to match your hardware configuration:

```python
MODBUS_METHOD = 'rtu'
MODBUS_PORT = '/dev/ttyUSB0'    # Adjust for your system
MODBUS_BAUDRATE = 115200
MODBUS_TIMEOUT = 1
MODBUS_PARITY = serial.PARITY_EVEN
MODBUS_STOPBITS = serial.STOPBITS_ONE
```

### Motor IDs

Each motor controller must have a unique Modbus slave ID (1-31). Use `cvd_change_config.py` to configure motor IDs.

## Usage

### Single Motor Control

```bash
python src/cvd_controller.py
```

Features:
- Motor initialization
- Speed control
- Step positioning
- Real-time status feedback

### Dual Motor Control

```bash
python src/dual_controller.py
```

Features:
- Control up to 2 motors
- Toggle between single and dual motor mode
- Independent parameter settings for each motor

### Quad Motor Control

```bash
python src/quad_controller.py
```

Features:
- Control up to 4 motors in a 1×4 grid layout
- Checkbox-based motor selection
- Batch command execution

### Six Motor Control

```bash
python src/octa_controller.py
```

Features:
- Control up to 6 motors in a 2×3 grid layout
- Individual motor enable/disable
- Coordinated movement commands

### 28-Motor Control

```bash
python src/all_controller.py
```

Features:
- Control up to 28 motors in a 4×7 grid layout
- Scrollable interface for large motor arrays
- Select all/deselect all functionality
- Batch operations with status reporting

### Motor ID Configuration

```bash
python src/cvd_change_config.py
```

Use this tool to:
- Change motor Modbus slave IDs
- Restart motors after configuration changes
- Verify motor connectivity

## Motor Operations

### Initialization
Prepares motors for operation by writing initialization commands to Modbus registers.

### Speed Control
Sets the rotation speed for selected motors (units depend on motor controller specification).

### Step Control
Commands motors to move a specific number of steps (positive or negative for direction).

## Modbus Register Map

| Function | Address | Description |
|----------|---------|-------------|
| Initialize | 0x0066 | Motor initialization command |
| Speed | 0x005E | Motor speed setting |
| Step | 0x005C | Step count for positioning |
| ID Change | 0x1380 | Change motor slave ID |
| Restart | 0x0192 | Restart motor controller |

## Error Handling

All applications include comprehensive error handling with:
- Visual status indicators (green/red/orange)
- Detailed error messages
- Connection status monitoring
- Input validation

## Troubleshooting

### Connection Issues
- Verify serial port permissions: `sudo usermod -a -G dialout $USER`
- Check cable connections and RS485 termination
- Confirm baud rate and parity settings match motor controllers

### Motor Not Responding
- Verify motor slave ID matches GUI setting
- Check motor power supply
- Use `manual.py` for low-level debugging

### Multiple Motor Control
- Ensure all motor IDs are unique
- Check bus termination for multi-drop RS485
- Verify adequate power supply for all motors

## Development

### Adding New Controllers

1. Create new controller file following the existing pattern
2. Import required modules: `tkinter`, `pymodbus`, `setting`, `util`
3. Implement motor control functions using the Modbus register map
4. Add appropriate GUI layout for your motor configuration

### Utility Functions

`util.py` provides helper functions:
- `decimal_to_hex()`: Converts decimal values to high/low register pairs

## Dependencies

- `pymodbus`: Modbus communication library
- `pyserial`: Serial port communication
- `tkinter`: GUI framework (included with Python)

## License

This project is provided as-is for educational and development purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with actual hardware
5. Submit a pull request

## Support

For issues related to:
- **Hardware connectivity**: Check motor controller documentation
- **Software bugs**: Open an issue with detailed error information
- **Feature requests**: Describe the use case and proposed implementation
