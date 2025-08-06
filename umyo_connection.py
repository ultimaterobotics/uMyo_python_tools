# test_umyo.py - Verify your setup in 30 seconds
import umyo_parser
import serial
from serial.tools import list_ports
import time

# Connect to uMyo sensor
ports = list(list_ports.comports())
print("available ports:")
device = None
for p in ports:
    print(p.device)
    device = p.device
    if "usbserial" in p.device:
        device = p.device
        print(f"{device=}")
print("===")

temp_ser = serial.Serial(device, timeout=1)
temp_ser.close()
time.sleep(0.5)

print(f"{device=}")
ser = serial.Serial(
    port=device,
    baudrate=921600,
    parity=serial.PARITY_NONE,
    stopbits=1,
    bytesize=8,
    timeout=0,
)
print(ser)

print("🔍 Searching for uMyo sensors...")
for _ in range(100):  # 10 seconds at ~10Hz
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        parsed_data = umyo_parser.umyo_parse_preprocessor(data)
        devices = umyo_parser.umyo_get_list()
        if devices:
            device = devices[0]
            print(f"✅ Found sensor {device.unit_id:08X}")
            print(f"🔋 Battery: {device.batt}mV | 📶 RSSI: {device.rssi}")
            print(f"💪 EMG: {device.data_array[-1]} | 🌐 Orientation: {device.Qsg}")
            print("Device attributes:")
            for attr in ["Qsg", "ax", "ay", "az", "yaw", "pitch", "roll"]:
                if hasattr(device, attr):
                    print(f"{attr}: {getattr(device, attr)}")
                else:
                    print(f"{attr}: NOT FOUND")
            if hasattr(device, 'packet_type'):
                print(f"Device {device.unit_id:08X}: packet_type={device.packet_type}, data_count={device.data_count}")
            break
    time.sleep(0.1)

if "ser" in locals() and ser.is_open:
    ser.close()
    print("Serial port closed")
