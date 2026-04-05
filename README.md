# Wi-Detect: WiFi-Based Fall & Assault Detection using CSI (No Cameras, No Wearables)

A non-invasive safety system that uses Wi-Fi signals to detect falls, struggles, and violent activity in real time — no cameras, no wearables.

Built for the **Lady Ada Lovelace Challenge** by PClub, IIT Kanpur.

---

## The Idea

There are places where cameras can't go, changing rooms, bathrooms, hostel corridors at night. But Wi-Fi already exists there. When a person moves, their body scatters the Wi-Fi signals in the room in a way that's unique to what they're doing. A fall looks different from walking. A struggle looks different from sitting still.

Wi-Detect captures that scattering (called Channel State Information, or CSI) from a pair of ESP32 microcontrollers and runs it through a classifier to detect dangerous activity, all without recording a single frame of video.

---

## How It Works

```
ESP32 (TX) ──── Wi-Fi signals ────> ESP32 (RX)
                                        │
                                   CSI extracted
                                        │
                                  Python pipeline
                                        │
                              sliding window features
                                        │
                              Random Forest classifier
                                        │
                               normal / fall / assault
                                        │
                            alert if danger is detected
```

The receiver ESP32 pings the transmitter 100 times per second. Each ping comes back with 52 subcarrier amplitude values describing how the signal travelled through the room. We extract statistical features over a rolling window of frames and feed that into a trained classifier.

---

## Hardware

- 2× ESP32 (WROOM-32 or any variant with CSI support)
- USB cable for flashing + serial read
- Power source for the second ESP32 (any 5V USB)

That's it. No special sensors, no extra hardware.

---

## Requirements
 
- Python 3.10+
- ESP-IDF v5.0+
- 2× ESP32 boards
- Python packages: `pyserial numpy pandas scikit-learn scipy matplotlib`
 
---
 
## Quick Start
 
### 1. Clone the repo
```bash
git clone https://github.com/Agarwal-Ujjwal/Wi-Detect.git
cd Wi-Detect
```
 
### 2. Install Python dependencies
```bash
pip install pyserial numpy pandas scikit-learn scipy matplotlib
```
 
### 3. Flash the ESP32s
```bash
# Set up ESP-IDF first
cd ~/esp/esp-idf && . ./export.sh
 
# Flash receiver
cd Wi-Detect/active_sta
idf.py -p /dev/cu.usbserial-0001 build flash
 
# Flash transmitter
cd ../active_ap
idf.py -p /dev/cu.usbserial-XXXX build flash
```
 
### 4. Train the model
```bash
python3 python_utils/train_model.py
```
 
### 5. Run live detection
```bash
python3 python_utils/detect.py
```

---

## Project Structure

```
Wi-Detect/
├── active_ap/          # ESP32 firmware — Access Point (transmitter)
├── active_sta/         # ESP32 firmware — Station (receiver + CSI)
├── passive/            # Passive CSI sniffing mode
├── _components/        # Shared CSI component library
├── python_utils/
│   ├── collect_data.py # Labelled data recorder (keypress interface)
│   ├── train_model.py  # Feature extraction + model training
│   └── detect.py       # Real-time inference + alert
├── dataset/            # Recorded CSI sessions (CSV)
├── model/              # Trained model + evaluation plots
└── docs/               # Project proposal and documentation
```

---

## Current Results

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| normal | 0.89 | 0.97 | 0.93 |
| assault | 0.81 | 0.57 | 0.67 |
| fall | 0.82 | 0.43 | 0.56 |

**Overall accuracy: 88%** on held-out test set. 5-fold CV F1: 0.74.

The low recall on fall and assault is a data volume issue — the normal class has ~23K frames while fall/assault have ~2.7K each. More balanced data will fix this.

---

## Dataset

Recorded in a single indoor room with two ESP32s placed 2–3 meters apart.

| Class | Frames |
|-------|--------|
| normal | 23,551 |
| fall | 2,677 |
| assault | 2,875 |

Data is stored as CSV with columns: `label, timestamp, rssi, amp_0 ... amp_48`

---

## What's Next

- More fall and assault recordings to balance the dataset
- CNN on the raw (window × subcarrier) amplitude matrix
- SMS/webhook alert integration
- Testing across multiple room configurations

---

## Team

We are team **HardCoreCoding** — a group of Y25s at IIT Kanpur.

- Nityam Aditya  
- Krishnam Nuwal  
- Lakshya Pareta  
- Ujjwal Agarwal  

Firmware based on [ESP32-CSI-Tool](https://stevenmhernandez.github.io/ESP32-CSI-Tool/) by Steven Hernandez.
