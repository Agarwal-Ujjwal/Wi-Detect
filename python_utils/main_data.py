import serial
import numpy as np
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
import re
import csv
import time
import os
from collections import deque


SERIAL_PORT = 'COM3'    
BAUD_RATE = 115200       
SUBCARRIER_INDEX = 44    
SAVE_FOLDER = "dataset" 
FRAMES_TO_CAPTURE = 60  



is_recording = False
record_type = ""
record_buffer = []
file_counters = {"fall": 0, "walk": 0}


if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

def save_to_csv(data, action_type):
    global file_counters
    file_counters[action_type] += 1
    count = file_counters[action_type]
    filename = f"{SAVE_FOLDER}/{action_type}_{count}.csv"
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow(["Label", "CSI_Data_Run"])
    
        for row in data:
            writer.writerow(row)
            
    print(f"\n[SAVED] : {filename} successfully!")
    print("Ready for next action... (Press F or W)")

def on_key(event):
    global is_recording, record_type, record_buffer
    
    if is_recording:
        return 
        
    if event.key == 'f':
        print("\n--- RECORDING FALL (3 Seconds) ---")
        print(">>> GO! DROP NOW! <<<")
        is_recording = True
        record_type = "fall"
        record_buffer = [] 
        
    elif event.key == 'w':
        print("\n--- RECORDING WALK (3 Seconds) ---")
        print(">>> GO! WALK NOW! <<<")
        is_recording = True
        record_type = "walk"
        record_buffer = []

def run_recorder():
    global is_recording, record_buffer
    
 
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}. Waiting for data...")
    except Exception as e:
        print(f"Error: {e}")
        return

    
    plt.ion()
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('key_press_event', on_key) # Listen for keyboard
    ax.set_ylim(0, 60)
    ax.set_title("PRESS 'F' for FALL | PRESS 'W' for WALK")
    
    line, = ax.plot(np.zeros(100))
    plot_data = deque([0]*100, maxlen=100)

    print("-----------------------------------------")
    print("   DATA RECORDER READY")
    print("   1. Click on the White Graph Window")
    print("   2. Press 'F' on keyboard -> Simulate Fall")
    print("   3. Press 'W' on keyboard -> Walk normally")
    print("-----------------------------------------")

    while True:
        try:
            raw = ser.readline()
            try:
                text = raw.decode('utf-8', errors='ignore').strip()
            except:
                continue

            if "CSI_DATA" in text:
                match = re.search(r"\[(.*?)\]", text)
                if match:
                    # Parse the full CSI list
                    csi_raw = [int(x) for x in match.group(1).split()]
                    
                    # 1. Update Live Graph (Visual only)
                    if len(csi_raw) > 100:
                        real = csi_raw[SUBCARRIER_INDEX * 2]
                        imag = csi_raw[SUBCARRIER_INDEX * 2 + 1]
                        amp = np.sqrt(real**2 + imag**2)
                        plot_data.append(amp)
                        line.set_ydata(plot_data)
                        fig.canvas.flush_events()

                    # 2. Record Data (If active)
                    if is_recording:
                        # Save the FULL raw row for AI training
                        record_buffer.append(csi_raw)
                        
                        # Check if we have enough frames
                        if len(record_buffer) >= FRAMES_TO_CAPTURE:
                            save_to_csv(record_buffer, record_type)
                            is_recording = False # Stop recording

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_recorder()


    