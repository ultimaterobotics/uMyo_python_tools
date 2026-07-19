
# umyo_testing — the main script for testing/calibrating uMyos: connects to the
# USB receiver, feeds its serial stream through umyo_parser, and shows the live
# pygame GUI (EMG traces, orientation, compass). This is the one you run.

import umyo_parser
import display_stuff
from serial.tools import list_ports
import serial
import pygame
import sys
import time

# USB id of the CP210x serial bridge on the uMyo receiver — used to auto-find its port
VID_PID = "10C4:EA60"


def find_umyo_receiver():
    # scan USB serial ports, pick the receiver by its VID:PID (no hardcoded port)
    ports = list_ports.comports()
    for port in ports:
        if VID_PID.lower() in (port.hwid or "").lower():
            print(f"Auto-selected port: {port.device}")
            return port.device
    raise IOError(f"No USB receiver with VID:PID {VID_PID} found!")


# Windows-safe serial reconnect with retries
def connect_serial(device):
    for attempt in range(3):
        try:
            return serial.Serial(
                port=device,
                baudrate=921600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0,
            )
        except Exception as e:
            print(f"Retrying serial connect... attempt {attempt + 1}")
            time.sleep(0.3)
    raise IOError("Failed to reconnect serial after retries.")


# Optional: add this to your parser if not present
if not hasattr(umyo_parser, "umyo_clear_buffer"):

    def dummy_clear():
        umyo_parser.internal_data = []

    umyo_parser.umyo_clear_buffer = dummy_clear

# Optional fallback: implement if not present in display_stuff
if not hasattr(display_stuff, "plot_blank"):

    def plot_blank():
        screen = pygame.display.get_surface()
        if screen:
            screen.fill((0, 0, 0))
            pygame.display.flip()

    display_stuff.plot_blank = plot_blank


def reconnect_serial(old_ser):
    # Serial died (receiver unplugged, or a reconnect attempt failed). Close it,
    # then wait — rescanning for the receiver each try, since it can re-enumerate
    # to a different port name on replug — until it comes back or the window is
    # closed. Pumps pygame events so the GUI stays responsive while you replug.
    # Returns (serial, still_running).
    try:
        old_ser.close()
    except Exception:
        pass
    print("Receiver lost — waiting for it to come back (unplug/replug is fine)...")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                return old_ser, False
        try:
            new_ser = connect_serial(find_umyo_receiver())
            print("Reconnected to:", new_ser.portstr)
            umyo_parser.umyo_clear_buffer()
            return new_ser, True
        except Exception:
            display_stuff.plot_blank()
            time.sleep(0.3)


device = find_umyo_receiver()
ser = connect_serial(device)
print("Connected to:", ser.portstr)
display_stuff.plot_init()

last_data_upd = 0
parse_unproc_cnt = 0
running = True
received_once = False
auto_reconnected = False
last_recv_time = time.time()

try:
    while running:
        try:
            cnt = ser.in_waiting
            if cnt > 0:
                data = ser.read(cnt)
                parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
                parsed_list = umyo_parser.umyo_get_list()

                if parsed_list:
                    # Check for required attributes before drawing
                    valid = all(
                        hasattr(dev, "ax") and hasattr(dev, "ay") and hasattr(dev, "az")
                        for dev in parsed_list
                    )
                    if valid:
                        received_once = True
                        auto_reconnected = False
                        last_recv_time = time.time()
                        dat_id = display_stuff.plot_prepare(parsed_list)
                        if dat_id is not None:
                            d_diff = dat_id - last_data_upd
                            if d_diff > 2 + (parse_unproc_cnt / 200):
                                display_stuff.plot_cycle_tester()
                                last_data_upd = dat_id
            else:
                if not received_once:
                    display_stuff.plot_blank()
                elif not auto_reconnected and (time.time() - last_recv_time) > 2:
                    print("No new data for 2s, auto-reconnecting serial...")
                    try:
                        ser.close()
                    except:
                        pass
                    ser = connect_serial(device)
                    umyo_parser.umyo_clear_buffer()
                    received_once = False
                    auto_reconnected = True
                    last_data_upd = 0
        except (serial.SerialException, OSError):
            # receiver physically unplugged: in_waiting/read (or the soft-stall
            # reconnect above) threw. Rescan, wait for it to come back, keep the
            # window alive — instead of crashing out to pygame.quit().
            ser, running = reconnect_serial(ser)
            received_once = False
            last_data_upd = 0
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    print("Manual serial reconnect (R key)...")
                    try:
                        ser.close()
                    except:
                        pass
                    ser = connect_serial(device)
                    umyo_parser.umyo_clear_buffer()
                    received_once = False
                    auto_reconnected = False
                    last_recv_time = time.time()
                    last_data_upd = 0

except KeyboardInterrupt:
    print("\nKeyboard interrupt detected. Closing...")

finally:
    pygame.quit()
    if ser:
        ser.close()
    print("Closed gracefully.")
