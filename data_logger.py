import csv
import time
from datetime import datetime
import os
import numpy as np
from zmq import device

import umyo_class
from umyo_parser import DeviceData

class DataLogger:
    def __init__(self, base_path="logs"):
        self.base_path = base_path
        self.current_file = None
        self.csv_writer = None
        self.session_start_time = None
        self.rows_since_flush = 0
        self._ensure_log_directory()
        
    def _ensure_log_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
    
    def start_new_session(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.base_path, f"umyo_session_{timestamp}.csv")
        self.current_file = open(filename, 'w', newline='')
        self.csv_writer = csv.writer(self.current_file)
        self.session_start_time = time.time()
        
        # Write header - one column per value
        self.csv_writer.writerow([
            'timestamp',
            'device_id',
            # EMG data columns (8 values)
            *[f'emg_{i}' for i in range(8)],
            # Spectrogram columns (4 bands)
            *[f'spg_band_{i}' for i in range(4)],
            'ax', 'ay', 'az',
            'quat_w', 'quat_x', 'quat_y', 'quat_z',
            'mag_angle',
            'rssi',
            'battery'
        ])
        
    def log_device_data(self, packet: DeviceData, timestamp: float):
        """Log packet data with provided timestamp
        
        Args:
            packet: DeviceData object containing device data
            timestamp: float, timestamp of the data
        """
        if self.csv_writer is None:
            return
        
        try:
            # Extract data from DeviceData packet
            row = [
                f"{timestamp:.6f}",  # Explicitly format with 6 decimal places
                packet.device_id,
                *packet.data['data_array'][:8],  # EMG data
                *packet.data['device_spectr'][:4],  # Spectrogram
                packet.data['ax'],
                packet.data['ay'],
                packet.data['az'],
                *packet.data['Qsg'][:4],  # Quaternions
                packet.data['mag_angle'],
                packet.data['rssi'],
                packet.data['batt']
            ]
            
            self.csv_writer.writerow(row)
            
            # Flush every N rows
            if self.rows_since_flush >= 100:
                self.current_file.flush()
                self.rows_since_flush = 0
            else:
                self.rows_since_flush += 1
                
        except Exception as e:
            print(f"\nError logging data for device {packet.device_id}: {e}")

    def close(self):
        """Close the current logging session"""
        if self.current_file is not None:
            self.current_file.close()
            self.current_file = None
            self.csv_writer = None    