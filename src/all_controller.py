import tkinter as tk
from pymodbus.client import ModbusSerialClient as ModbusClient
import serial
from setting import *
from util import *

def modbus_write(address, value, slave):
    upper, lower = decimal_to_hex(value)
    client.write_registers(address, [upper, lower], device_id=slave)

def initialize_motors():
    """チェックされたモーターを初期化する"""
    initialized_motors = []
    try:
        for i in range(28):
            if motor_enabled[i].get():
                device_id = int(entry_ids[i].get())
                client.write_registers(address=0x0066, values=[0xffff, 0xfffb], device_id=device_id)
                initialized_motors.append(device_id)
        
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
        for i in range(28):
            if motor_enabled[i].get():
                device_id = int(entry_ids[i].get())
                speed = int(entry_speeds[i].get())
                client.write_registers(address=0x005e, values=[0, speed], device_id=device_id)
                processed_motors.append(device_id)
        
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
        for i in range(28):
            if motor_enabled[i].get():
                device_id = int(entry_ids[i].get())
                step = int(entry_steps[i].get())
                modbus_write(0x005c, step, device_id)
                processed_motors.append(device_id)
        
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

def toggle_all_motors():
    """すべてのモーターの有効/無効を切り替える"""
    new_state = toggle_all_var.get()
    for i in range(28):
        motor_enabled[i].set(new_state)

# Modbus接続の設定
client = ModbusClient(
    port=MODBUS_PORT,
    baudrate=MODBUS_BAUDRATE,
    timeout=MODBUS_TIMEOUT,
    parity=MODBUS_PARITY,
    stopbits=MODBUS_STOPBITS
)

# Tkinter GUIの設定
root = tk.Tk()
root.title("28-Motor Control GUI")

# スクロール可能なキャンバスを作成
canvas_frame = tk.Frame(root)
canvas_frame.grid(row=0, column=0, sticky="nsew")
canvas = tk.Canvas(canvas_frame)
scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# キャンバスとスクロールバーをグリッドに配置
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# モーターブロックの作成のための配列
motor_frames = []
motor_enabled = []
entry_ids = []
entry_speeds = []
entry_steps = []

# モーターグリッドの作成（4行×7列）
for i in range(28):
    row = i // 7
    col = i % 7
    
    # モーターブロックのフレーム
    # 部位名の定義
    motor_names = [
        "Front Drive Wheel", "Rear Drive Wheel", "Front Clamp", "Rear Clamp", "Front Leg UpDown", "Rear Leg UpDown", "Stopper Clamp", "Stopper Slide",
        "Upper UpDown", "Upper Rotation", "Arm Slide", "Shoulder", "Hand Drive Wheel", "Hand Clamp",
        "Front Drive Wheel", "Rear Drive Wheel", "Front Clamp", "Rear Clamp", "Front Leg UpDown", "Rear Leg UpDown", "Stopper Clamp", "Stopper Slide",
        "Upper UpDown", "Upper Rotation", "Arm Slide", "Shoulder", "Hand Drive Wheel", "Hand Clamp"
    ]
    motor_frame = tk.LabelFrame(scrollable_frame, text=motor_names[i], padx=5, pady=5)
    motor_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    motor_frames.append(motor_frame)
    
    # モーターの有効/無効チェックボックス
    enabled_var = tk.BooleanVar()
    enabled_var.set(False)
    motor_enabled.append(enabled_var)
    cb_enabled = tk.Checkbutton(motor_frame, text="Enable", variable=enabled_var)
    cb_enabled.grid(row=0, column=0, columnspan=2, sticky="w")
    
    # ID
    tk.Label(motor_frame, text=f"ID:").grid(row=1, column=0, sticky="w")
    id_entry = tk.Entry(motor_frame, width=6)
    id_entry.grid(row=1, column=1, sticky="w")
    id_entry.insert(0, f"{i+1}")  # デフォルトIDを設定
    entry_ids.append(id_entry)
    
    # スピード
    tk.Label(motor_frame, text=f"Speed:").grid(row=2, column=0, sticky="w")
    speed_entry = tk.Entry(motor_frame, width=6)
    speed_entry.grid(row=2, column=1, sticky="w")
    speed_entry.insert(0, "100")  # デフォルト値
    entry_speeds.append(speed_entry)
    
    # ステップ
    tk.Label(motor_frame, text=f"Step:").grid(row=3, column=0, sticky="w")
    step_entry = tk.Entry(motor_frame, width=6)
    step_entry.grid(row=3, column=1, sticky="w")
    step_entry.insert(0, "100")  # デフォルト値
    entry_steps.append(step_entry)

# 列の重み設定（7列分）
for i in range(7):
    scrollable_frame.columnconfigure(i, weight=1)

# コントロールパネルフレーム
control_panel = tk.Frame(root)
control_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

# 全モーター選択/解除チェックボックス
toggle_all_var = tk.BooleanVar()
toggle_all_var.set(False)
toggle_all_cb = tk.Checkbutton(control_panel, text="Select/Deselect All Motors", variable=toggle_all_var, command=toggle_all_motors)
toggle_all_cb.grid(row=0, column=0, columnspan=3, sticky="w", pady=5)

# コマンド選択部分
command_frame = tk.LabelFrame(control_panel, text="Commands", padx=10, pady=5)
command_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)

initialize_var = tk.BooleanVar()
speed_var = tk.BooleanVar()
step_var = tk.BooleanVar()

tk.Checkbutton(command_frame, text="Initialize Motors", variable=initialize_var).grid(row=0, column=0, padx=5, sticky="w")
tk.Checkbutton(command_frame, text="Send Speed", variable=speed_var).grid(row=0, column=1, padx=5, sticky="w")
tk.Checkbutton(command_frame, text="Send Step", variable=step_var).grid(row=0, column=2, padx=5, sticky="w")

# 送信ボタン
send_button = tk.Button(control_panel, text="Send Commands", command=send_commands, width=20, height=2, bg="#4CAF50", fg="white")
send_button.grid(row=2, column=0, columnspan=3, pady=5)

# ステータス表示
status_label = tk.Label(control_panel, text="Ready", fg="blue")
status_label.grid(row=3, column=0, columnspan=3, pady=5)

# 列と行の重み設定
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=6)  # モーターグリッドには多くのスペースを割り当て
root.rowconfigure(1, weight=1)  # コントロールパネルには少なめのスペース

# ウィンドウサイズの初期設定
root.geometry("1000x700")  # 28個のモーターに対応するためサイズを拡大

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