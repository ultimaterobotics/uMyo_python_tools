import umyo_parser
from data_logger import DataLogger
from serial.tools import list_ports
import serial
import time
import sys
from datetime import datetime
from datetime import datetime
from collections import deque
from statistics import mean


def print_status(message, end='\r'):
    """Print status message with carriage return to update in place"""
    sys.stdout.write(f"\r{message}{' ' * 20}")
    sys.stdout.flush()
    if end == '\n':
        sys.stdout.write('\n')

def log_timing_stats(read_times, interval_times, packet_count, duration):
    """Log detailed timing statistics"""
    if not read_times:
        return
        
    avg_read = mean(read_times)
    avg_interval = mean(interval_times)
    max_interval = max(interval_times)
    packets_per_sec = packet_count / duration if duration > 0 else 0
    
    print_status(
        f"\nTiming stats:"
        f"\n  Avg read time: {avg_read*1000:.3f}ms"
        f"\n  Avg interval: {avg_interval*1000:.3f}ms"
        f"\n  Max interval: {max_interval*1000:.3f}ms"
        f"\n  Packets/sec: {packets_per_sec:.1f}"
        f"\n", 
        end='\n'
    )

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

#ser.set_buffer_size(rx_size=131072)  # 128KB receive buffer

#ser.setRTS(False)
#ser.setDTR(False)

print(f"\nConnected to: {ser.portstr}")
print("Waiting for device input... (Ctrl+C to exit)")

try:
    # Timing tracking
    read_times = deque(maxlen=100)  # Track last 100 read times
    interval_times = deque(maxlen=100)  # Track last 100 intervals
    last_read_time = time.time()
    stats_start_time = time.time()
    stats_packet_count = 0

    last_status_time = time.time()
    last_data_time = time.time()
    packet_count = 0
    show_waiting = True
    data_started = False
    
    while True:
        current_time = time.time()
        cnt = ser.in_waiting
        
        if cnt > 0:
                
             # Timing measurement
            read_start = time.time()
            data = ser.read(cnt)
            read_end = time.time()

            # Track timing
            read_duration = read_end - read_start
            interval = read_start - last_read_time
            read_times.append(read_duration)
            interval_times.append(interval)
            last_read_time = read_start

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
            stats_packet_count += 1
            last_data_time = current_time
            
            # Update receiving status every 2 seconds
            if current_time - last_status_time >= 2.0:
                duration = current_time - stats_start_time
                log_timing_stats(read_times, interval_times, stats_packet_count, duration)
                print_status(f"Receiving data... (Packets: {packet_count//1000}k)")
                last_status_time = current_time
                stats_packet_count = 0
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