# ESP32 CSI-Based Human Activity Recognition  

# Project Phase 1: Hardware Setup & System Integration

## Goal
Establish a stable **Connection State Information (CSI)** link between two **ESP32 microcontrollers** (Transmitter and Receiver) to capture Wi-Fi signal variations for **Human Activity Recognition (HAR)**.

---

## Project Progress

### 1. Selection of Development Framework: ESP-IDF
We chose to use the **Espressif IoT Development Framework (ESP-IDF)** instead of the simpler Arduino IDE.

Arduino hides many low-level hardware details. To capture **CSI**, which represents raw electromagnetic (EM) wave data, we required:
- Direct access to the **Wi-Fi chip’s Physical Layer**
- Support for **FreeRTOS**

These features are not fully available in the Arduino IDE, making ESP-IDF essential.

---

### 2. Flash Code Upload
During flashing:
- Existing flash memory is erased
- Custom firmware is uploaded

The uploaded code enables detection and monitoring of Wi-Fi waves.

---

### 3. Connecting the Transmitter (Tx)
The **Transmitter (Tx)** detects Wi-Fi signals in its surrounding environment.

Steps performed:
- Flash code uploaded to the Tx ESP32
- Initially powered via laptop (USB)
- Later powered using an **external power source** (USB adapter)

---

### 4. Setting Up the Receiver (Rx)
The **Receiver (Rx)** captures Wi-Fi signals and calculates wave disturbances caused by motion.

Implementation details:
- Development focused on the `active_sta` (Active Station) directory
- Receiver initially outputs CSI data as a **matrix of numerical values**
- Python script **`main_data.py`** is used for data processing

This script:
1. Reads CSI data from CSV files
2. Generates signal graphs for analysis

---

## Graph Interpretation

- **Y-axis**: Amplitude-like magnitude of received signals  
- **High Peaks**: Waves are *in phase*  
- **Troughs**: Waves are *out of phase*  
![Graph]()
When a person waves their hand:
- Wi-Fi signals reflect differently
- Path lengths change
- Interference patterns shift

This results in **wobble or ripple-like wave patterns**, which are the features learned by the **LSTM model**.

---

## 5. CSV File Generation
We generated:
- `Fall_n.csv`
- `Walk_n.csv`

A total of **10 CSV files** were created for training the model to classify different **human motions**.

---

## Bugs and Challenges Faced

---

### Challenge 1: Graph Visualization Failed
Issues encountered:
- Graph window froze or became unresponsive
- Program crashed with:`ImportError: Failed to import Qt binding`

The code defaulted to Qt5Agg which we modified it to use the TkAgg

---

### Challenge 2:The Data Break(fragmented)
Initially the data we received was not the complete just recieveing the closing bracket of matrix

---

### Challenge 3:Baud rate synchronize:
The graph remained flat/blank even after fixing the code. It shows the raw data consisted of "Garbage Characters" (e.g., \x80\x00).

---

### Challenge 4: Settings Change:
The system was stable but printed CSI will not be collected.
We located the specific feature in the CSI Tool Config menu and
manually checked the box to **Enable CSI Collection**.

---

### THe main Challenge 5:Priority Error:
The error popped up assert `failed: prvInitialiseNewTask (uxPriority < 25)`. This error took max time to get solved …we set priority<20 .
Tilized Boot (Holding BOOT button before powering on) to force the crashing chip into Download Mode, bypassing the boot loop to allow re-flashing. 
And Identified the specific line in the (`main/main.cc`) requesting Priority 100.

Here a small clip of error [LINK](https://drive.google.com/file/d/1A8OPYophXZulWxV3fLxsJDpoBn2jWs7h/view)

---

## Current Achievement Status
- **Hardware State:** ESP32 Transceiver pair is fully functional.
- **Software State:** We are building LSTM model to train over those csv files . and the roadmap is in our [Main_Doc](https://drive.google.com/file/d/1wGrFJE2-akHcZTiFLCfy2ZXJ1K0hqhLB/view)

---
