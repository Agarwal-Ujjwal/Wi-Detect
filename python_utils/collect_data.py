import serial
import csv
import os
import sys
import tty
import termios
import threading
from datetime import datetime

PORT = "/dev/cu.usbserial-0001"
BAUD = 115200
DATA_DIR = os.path.expanduser("~/esp/Wi-Detect/dataset")
os.makedirs(DATA_DIR, exist_ok=True)

current_label = None
recording = False
writer = None
csv_file = None
frame_count = 0
running = True

def parse_csi_line(line):
    try:
        if not line.startswith("CSI_DATA"):
            return None
        parts = line.split(",")
        if len(parts) < 20:
            return None
        rssi = parts[3]
        timestamp = parts[16]
        bracket_start = line.index("[") + 1
        bracket_end = line.index("]")
        csi_raw = line[bracket_start:bracket_end].strip().split()
        if len(csi_raw) < 110:
            return None
        amplitudes = []
        for i in range(12, 110, 2):
            im = int(csi_raw[i])
            re = int(csi_raw[i+1])
            amplitudes.append(round((im**2 + re**2)**0.5, 4))
        return rssi, timestamp, amplitudes
    except Exception:
        return None

def start_recording(label):
    global writer, csv_file, recording, current_label, frame_count
    if recording:
        stop_recording()
    current_label = label
    frame_count = 0
    fname = os.path.join(DATA_DIR, f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    csv_file = open(fname, "w", newline="")
    cols = ["label", "timestamp", "rssi"] + [f"amp_{i}" for i in range(49)]
    writer = csv.writer(csv_file)
    writer.writerow(cols)
    print(f"\n  [REC] Recording '{label}' → {os.path.basename(fname)}", flush=True)

def stop_recording():
    global writer, csv_file, recording, frame_count
    if csv_file:
        csv_file.flush()
        csv_file.close()
        csv_file = None
    writer = None
    recording = False
    print(f"\n  [STOP] Saved {frame_count} frames.", flush=True)

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def keyboard_listener():
    global recording, running
    print("\n╔══════════════════════════════════╗")
    print("║   Wi-Detect Data Collector       ║")
    print("╠══════════════════════════════════╣")
    print("║  n → record NORMAL               ║")
    print("║  f → record FALL                 ║")
    print("║  a → record ASSAULT/STRUGGLE     ║")
    print("║  s → stop current recording      ║")
    print("║  q → quit                        ║")
    print("╚══════════════════════════════════╝")
    print("\nPress a key (no Enter needed):\n", flush=True)
    while running:
        ch = getch()
        if ch == "n":
            start_recording("normal")
            recording = True
        elif ch == "f":
            start_recording("fall")
            recording = True
        elif ch == "a":
            start_recording("assault")
            recording = True
        elif ch == "s":
            if recording:
                stop_recording()
            else:
                print("\n  Not recording.", flush=True)
        elif ch == "q":
            if recording:
                stop_recording()
            print("\nExiting.\n")
            running = False
            os._exit(0)

def main():
    global frame_count
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to {PORT}", flush=True)
    t = threading.Thread(target=keyboard_listener, daemon=True)
    t.start()
    while running:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            result = parse_csi_line(line)
            if result and recording and writer:
                rssi, timestamp, amplitudes = result
                writer.writerow([current_label, timestamp, rssi] + amplitudes)
                frame_count += 1
                if frame_count % 500 == 0:
                    print(f"  [{current_label}] {frame_count} frames...", flush=True)
        except Exception:
            continue

if __name__ == "__main__":
    main()
