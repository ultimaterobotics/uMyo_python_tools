import csv
import time
import datetime
import umyo_parser
import serial
from serial.tools import list_ports


class uMyoDataLogger:
    def __init__(self, filename=None):
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"umyo_data_{timestamp}.csv"

        self.filename = filename
        self.csv_file = None
        self.csv_writer = None
        self.start_time = time.time()

        # Initialize CSV file with headers
        self.init_csv()

    def init_csv(self):
        """Initialize CSV file with column headers"""
        self.csv_file = open(self.filename, "w", newline="")

        # Define comprehensive column headers
        headers = [
            "timestamp",
            "device_id",
            "data_id",
            "rssi",
            "battery_mv",
            "emg_sample_count",
            # EMG channels (8 channels for most uMyo devices)
            *[f"emg_ch_{i}" for i in range(8)],
            # Spectral data
            "spectrum_0",
            "spectrum_1",
            "spectrum_2",
            "spectrum_3",
            # Quaternion
            "quat_w",
            "quat_x",
            "quat_y",
            "quat_z",
            # Accelerometer
            "accel_x",
            "accel_y",
            "accel_z",
            # Euler angles
            "yaw",
            "pitch",
            "roll",
            # Magnetometer (if available)
            "mag_x",
            "mag_y",
            "mag_z",
            "mag_angle",
        ]

        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(headers)
        self.csv_file.flush()

    def log_device_data(self, device):
        """Log data from a single uMyo device to CSV"""
        current_time = time.time() - self.start_time

        # Prepare EMG data (pad with None if fewer than 8 channels)
        emg_data = (
            device.data_array[: device.data_count]
            if hasattr(device, "data_count")
            else device.data_array
        )
        emg_padded = (emg_data + [None] * 8)[:8]  # Ensure exactly 8 values

        full_spectr = getattr(device, "device_spectr", [None] * 16)
        if len(full_spectr) > 4 and any(x != 0 for x in full_spectr[4:]):
            print(f"Alert: Non-zero spectral data in positions 5-16: {full_spectr[4:]}")

        # Prepare row data
        row_data = [
            current_time,  # timestamp
            f"{device.unit_id:08X}",  # device_id as hex
            getattr(device, "data_id", None),
            getattr(device, "rssi", None),
            getattr(device, "batt", None),
            getattr(device, "data_count", len(emg_data)),
            *emg_padded,  # 8 EMG channels
            # Spectral data
            *getattr(device, "device_spectr", [None] * 16)[:4],
            # Quaternion (Qsg is a list with 4 elements)
            (
                device.Qsg[0]
                if hasattr(device, "Qsg") and len(device.Qsg) > 0
                else None
            ),  # quat_w
            (
                device.Qsg[1]
                if hasattr(device, "Qsg") and len(device.Qsg) > 1
                else None
            ),  # quat_x
            (
                device.Qsg[2]
                if hasattr(device, "Qsg") and len(device.Qsg) > 2
                else None
            ),  # quat_y
            (
                device.Qsg[3]
                if hasattr(device, "Qsg") and len(device.Qsg) > 3
                else None
            ),  # quat_z
            # Accelerometer
            device.ax if hasattr(device, "ax") else None,
            device.ay if hasattr(device, "ay") else None,
            device.az if hasattr(device, "az") else None,
            # Euler angles
            device.yaw if hasattr(device, "yaw") else None,
            device.pitch if hasattr(device, "pitch") else None,
            device.roll if hasattr(device, "roll") else None,
            # Magnetometer (these appear to always be 0 based on parser)
            getattr(device, "mx", 0),
            getattr(device, "my", 0),
            getattr(device, "mz", 0),
            getattr(device, "mag_angle", None),
        ]

        self.csv_writer.writerow(row_data)
        self.csv_file.flush()  # Ensure data is written immediately

    def log_all_devices(self):
        """Log data from all active devices"""
        devices = umyo_parser.umyo_get_list()
        for device in devices:
            self.log_device_data(device)

    def close(self):
        """Close the CSV file"""
        if self.csv_file:
            self.csv_file.close()


# Example usage integrated with your existing script
def main():
    # Setup serial connection (same as your existing code)
    ports = list(list_ports.comports())
    device = None
    for p in ports:
        device = p.device
        if "usbserial" in p.device:
            break

    if not device:
        print("No device found!")
        return

    temp_ser = serial.Serial(device, timeout=1)
    temp_ser.close()
    time.sleep(0.5)

    ser = serial.Serial(
        port=device,
        baudrate=921600,
        parity=serial.PARITY_NONE,
        stopbits=1,
        bytesize=8,
        timeout=0,
    )

    # Initialize data logger
    logger = uMyoDataLogger()
    print(f"Logging data to: {logger.filename}")

    try:
        print("Starting data collection... Press Ctrl+C to stop")
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                umyo_parser.umyo_parse_preprocessor(data)

                # Log data from all active devices
                logger.log_all_devices()

            time.sleep(0.01)  # 100Hz sampling

    except KeyboardInterrupt:
        print("\nStopping data collection...")
    finally:
        logger.close()
        ser.close()
        print(f"Data saved to: {logger.filename}")


if __name__ == "__main__":
    main()
