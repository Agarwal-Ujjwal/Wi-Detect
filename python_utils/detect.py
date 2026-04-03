"""
Wi-Detect — Real-time CSI Inference
Reads ESP32 serial stream → classifies every 0.5s → alerts on danger
"""

import os
import sys
import pickle
import serial
import numpy as np
from scipy import stats
from collections import deque
from datetime import datetime
import threading
import time

# ── Config ────────────────────────────────────────────────────────────────────
PORT       = "/dev/cu.usbserial-0001"
BAUD       = 115200
MODEL_PATH = os.path.expanduser("~/esp/Wi-Detect/model/wi_detect_model.pkl")
AMP_COLS   = [f"amp_{i}" for i in range(49)]
ALERT_CLASSES   = {"fall", "assault"}
CONFIRM_COUNT   = 3   # predict danger N times in a row before alerting
# ─────────────────────────────────────────────────────────────────────────────

# Load model
print("Loading model...", flush=True)
with open(MODEL_PATH, "rb") as f:
    bundle = pickle.load(f)
clf     = bundle["model"]
le      = bundle["label_encoder"]
WINDOW  = bundle["window_size"]
print(f"Model loaded. Window={WINDOW} frames. Classes={list(le.classes_)}", flush=True)

# Rolling buffer
buffer = deque(maxlen=WINDOW)
danger_streak = 0
last_label    = None

def parse_csi(line):
    try:
        if not line.startswith("CSI_DATA"):
            return None
        parts = line.split(",")
        if len(parts) < 20:
            return None
        rssi = float(parts[3])
        bracket_start = line.index("[") + 1
        bracket_end   = line.index("]")
        csi_raw = line[bracket_start:bracket_end].strip().split()
        if len(csi_raw) < 110:
            return None
        amps = []
        for i in range(12, 110, 2):
            im = int(csi_raw[i])
            re = int(csi_raw[i + 1])
            amps.append((im**2 + re**2) ** 0.5)
        return rssi, amps
    except Exception:
        return None

def extract_features(buf):
    arr = np.array(buf, dtype=np.float32)   # shape: (WINDOW, 49)
    feats = []
    for i in range(49):
        s = arr[:, i]
        feats += [
            np.mean(s), np.std(s), np.min(s), np.max(s),
            np.max(s) - np.min(s),
            float(stats.skew(s)),
            float(stats.kurtosis(s)),
        ]
    return np.array(feats, dtype=np.float32).reshape(1, -1)

def alert(label):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'!'*50}", flush=True)
    print(f"  ALERT [{ts}]  ⚠  {label.upper()} DETECTED", flush=True)
    print(f"{'!'*50}\n", flush=True)
    # macOS system sound
    os.system("afplay /System/Library/Sounds/Sosumi.aiff &")

def status_bar(label, proba, danger_streak):
    icons = {"normal": "✓", "fall": "⚠", "assault": "⚠"}
    colors = {"normal": "\033[92m", "fall": "\033[93m", "assault": "\033[91m"}
    reset = "\033[0m"
    icon  = icons.get(label, "?")
    color = colors.get(label, "")
    conf  = int(proba * 100)
    bar   = "█" * (conf // 5) + "░" * (20 - conf // 5)
    streak_info = f"  streak={danger_streak}/{CONFIRM_COUNT}" if label in ALERT_CLASSES else ""
    print(f"\r  {color}{icon} {label.upper():10s}{reset}  [{bar}] {conf:3d}%{streak_info}   ",
          end="", flush=True)

def main():
    global danger_streak, last_label
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to {PORT}", flush=True)
    print(f"Buffering {WINDOW} frames before first prediction...\n", flush=True)

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            result = parse_csi(line)
            if result is None:
                continue

            rssi, amps = result
            buffer.append(amps)

            if len(buffer) < WINDOW:
                continue

            # Run inference
            X    = extract_features(buffer)
            pred = clf.predict(X)[0]
            prob = clf.predict_proba(X)[0].max()
            label = le.inverse_transform([pred])[0]

            status_bar(label, prob, danger_streak)

            # Danger confirmation logic
            if label in ALERT_CLASSES:
                danger_streak += 1
                if danger_streak >= CONFIRM_COUNT:
                    alert(label)
                    danger_streak = 0
            else:
                danger_streak = 0

            last_label = label

        except KeyboardInterrupt:
            print("\n\nStopped.", flush=True)
            break
        except Exception as e:
            continue

if __name__ == "__main__":
    main()
