# Wi-Detect: Non-Invasive Safety Guardian

> **Team:** HardCoreCoding | **Event:** Lady Ada Hackathon
>
> **Members:** Ujjwal Agarwal | Krishnam Nuwal | Nityam Aditya | Lakshya Pareta | Lokendra

## 📖 Project Overview
**Wi-Detect** is a privacy-first safety system designed to detect violence, struggles, and falls in real-time without the use of invasive cameras.

Built at the intersection of **Physics (Wave Theory)** and **Machine Learning**, our solution leverages the Wi-Fi signals already present in a room to act as an invisible guardian. By analysing the scattering patterns of Electromagnetic (EM) waves, we can distinguish between routine movements and critical safety threats while maintaining 100% user anonymity.

---

## ⚙️ How It Works

Our system transforms standard Wi-Fi hardware into a sensing radar using **Channel State Information (CSI)**.

### 1. The Physics (Hardware Layer)
* **Device Setup:** We utilize two **ESP32 Microcontrollers**—one acting as a *Transmitter (Tx)* and the other as a *Receiver (Rx)*.
* **Multipath Propagation:** Wi-Fi signals are Electromagnetic waves. When a person moves through the field between the Tx and Rx, they induce specific scattering and reflection patterns known as **multipath fading**.
* **The Sensing Zone:** The system establishes an invisible Fresnel zone (elliptical sensing area). Specific human actions (walking vs. falling) disturb the carrier waves in unique, repeatable ways.

### 2. The Intelligence (ML Layer)
* **Data Extraction:** The Receiver ESP32 extracts raw **CSI (Channel State Information)** data, which captures the amplitude and phase variations of the Wi-Fi signal at a sub-carrier level.
* **Pattern Recognition:** This data is fed into a **Python-based Machine Learning model**.
* **Classification:** The model is trained to recognise the specific "wave interference signatures" of dangerous events. It can distinguish a **normal walk** from a **violent fall** or struggle with high precision.

---

## 🚀 Key Features

* **Privacy-Centric:** No cameras or microphones. The system sees waves, not faces, making it ideal for sensitive areas like washrooms or dorms.
* **Real-Time Detection:** Instant analysis of CSI data allows for immediate alerting capabilities.
* **Low Cost:** Built on affordable ESP32 hardware rather than expensive radar equipment.
* **Interdisciplinary:** A practical application of Wave Physics applied to Deep Learning.

---

## 🛠️ Tech Stack

* **Hardware:** ESP32 Microcontrollers (Tx/Rx Pair)
* **Firmware:** Custom CSI collection firmware (C++)
* **Software:** Python, Scipy (Signal Processing), PyTorch/TensorFlow (LSTM/CNN Models)
