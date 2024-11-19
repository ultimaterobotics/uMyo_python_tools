import umyo_parser
from data_logger import DataLogger
from serial.tools import list_ports
import serial
import time
import sys
from datetime import datetime
from collections import deque
from statistics import mean


def print_status(message, end='\r'):
    """Print status message with carriage return to update in place"""
    sys.stdout.write(f"\r{message}{' ' * 20}")
    sys.stdout.flush()
    if end == '\n':
        sys.stdout.write('\n')

# Initialize data logger
logger = DataLogger()
logger.start_new_session()

# List and connect to port
port = list(list_ports.comports())
print("Available ports:")
for i, p in enumerate(port):
    print(f"{i}: {p.device}")
    device = p.device
print("===")

# Setup serial connection
ser = serial.Serial(
    port=device,
    baudrate=921600,
    parity=serial.PARITY_NONE,
    stopbits=1,
    bytesize=8,
    timeout=0
)

print(f"\nConnected to: {ser.portstr}")
print("Waiting for device input... (Ctrl+C to exit)")

try:
    last_status_time = time.time()
    last_data_time = time.time()
    packet_count = 0
    show_waiting = True
    data_started = False
    
    while True:
        current_time = time.time()
        cnt = ser.in_waiting
        
        if cnt > 0:
                
            data = ser.read(cnt)

            if not data_started:
                data_started = True
                stats_start_time = time.time()
                print_status("Data collection started!", end='\n')
            
            parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
            devices = umyo_parser.umyo_get_list()
            
            # Log data for each device
            for device in devices:
                 if device is not None:  # Make sure we have a valid device
                    receive_time = time.time() #- logger.session_start_time
                    logger.log_device_data(device, receive_time)
            
            packet_count += 1
            last_data_time = current_time   
            
            # Update receiving status every 2 seconds
            if current_time - last_status_time >= 2.0:
                duration = current_time - stats_start_time
                print_status(f"Receiving data... (Packets: {packet_count//1000}k)")
                last_status_time = current_time
                stats_start_time = current_time
                
        elif not data_started:
            # Blink waiting message every second
            if current_time - last_status_time >= 1.0:
                if show_waiting:
                    print_status("Waiting for device input...")
                else:
                    print_status("                         ")  # Clear the line
                show_waiting = not show_waiting
                last_status_time = current_time

except KeyboardInterrupt:
    print_status("\nClosing gracefully...", end='\n')
    
except Exception as e:
    print(f"\nError occurred: {e}")
    
finally:
    try:
        logger.close()
    except:
        pass
    try:
        ser.close()
    except:
        pass
    print(f"Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")