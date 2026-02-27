# 🔐 AI-Powered Intelligent Security System (IoT + Facial Recognition)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![IoT](https://img.shields.io/badge/IoT-ESP32-green)
![Deep Learning](https://img.shields.io/badge/DeepLearning-MobileNet+FaceNet-orange)
![Status](https://img.shields.io/badge/Status-Completed-success)

End-to-end intelligent security system integrating computer vision, IoT sensors and cloud connectivity.

---

## 📌 Project Overview

This project presents the development of a **real-time intelligent security system** combining:

- Facial recognition using deep learning  
- Gas detection monitoring  
- Door/window opening detection  
- Fingerprint access control  
- Cloud-based real-time monitoring (Arduino IoT Cloud)  

The system integrates hardware (ESP32), edge AI processing and cloud synchronization into a unified architecture.

---

## 🎯 Objectives

- Identify authorized individuals via facial recognition  
- Detect hazardous gas concentrations (MQ-2 sensor)  
- Monitor door/window status using magnetic sensors (433 MHz RF)  
- Control access via fingerprint reader (AS608)  
- Send real-time alerts and system states to the cloud  

---

## 🧠 Facial Recognition Pipeline

The facial recognition module is based on:

- **MobileNet** → Face detection  
- **FaceNet** → Feature embedding extraction  
- Euclidean distance comparison for identity validation  

### Performance

- ~80–115 ms processing time per frame  
- Real-time operation  
- Threshold-based identification  

---

## 🌐 IoT Architecture

### Hardware Components

- ESP32 (Main controller)  
- ESP32 (Secondary controller)  
- MQ-2 gas sensor  
- Magnetic door sensor (RF 433 MHz)  
- Optical fingerprint reader (AS608)  
- Wansview Y1 IP Camera (RTSP stream)  

### Cloud Integration

- Arduino IoT Cloud  
- REST API communication  
- Real-time variable synchronization  
- Trigger-based notifications  

---

## ⚙️ System Workflow

1. Camera stream processed for face detection  
2. Face embeddings generated and compared against known database  
3. Identified name (or “unknown”) sent to Arduino Cloud  
4. Sensors monitored continuously  
5. Alerts triggered when:  
   - Gas concentration exceeds threshold  
   - Unauthorized door opening detected  
   - Unknown face recognized  

---

## 📁 Repository Contents

### 🧠 Facial Recognition

Code for:
- Face detection (MobileNet)  
- Embedding extraction (FaceNet)  
- Identity matching  
- Cloud synchronization (`Send_face_data_to_cloud`)  

### 🖐️ Fingerprint Enrollment

Code to register fingerprints in the AS608 module.

### 🔐 Fingerprint Access Control

Code to:
- Read and compare stored fingerprints  
- Manage access logic  
- Update system state  

### ☁️ Arduino Cloud Security Control

Arduino IoT Cloud code managing:
- Sensor states  
- Alarm activation  
- Notifications  
- System orchestration  

### 🧩 Models

- MobileNet: `frozen_inference_graph_face`  
- FaceNet: `keras-facenet`  

---

## 📊 Results

- Stable real-time monitoring  
- Integrated multi-sensor system  
- Automated cloud-based notifications  
- Functional edge + cloud architecture  

---

## 🚀 Key Challenges Solved

- CPU overload mitigation (frame skipping strategy)  
- Embedding threshold calibration  
- RF signal redundancy handling  
- MQ-2 sensor warm-up stabilization  
- False notification mitigation  

---

## 📎 Documentation

📄 Project presentation available in:

`/documentation/TFM_Presentation.pdf`

This document summarizes architecture, implementation and results.

---

## 🙏 Credits & References

Parts of this implementation were adapted from:

- Facial recognition tutorial: [Reconocimiento Facial con Machine Learning en Python]((https://www.codificandobits.com/blog/tutorial-reconocimiento-facial-python/). 
- AS608 fingerprint reference: [Fingerprint sensor AS608 with UNO] (https://forum.arduino.cc/t/fingerprint-sensor-as608-with-uno/1118222).
- FaceNet embeddings library: [`keras-facenet`] (https://pypi.org/project/keras-facenet/).

---

## 👤 Author

**Javier Piay**  
Industrial Engineer | AI & IoT Systems  

🔗 Connect with me on [LinkedIn](https://www.linkedin.com/in/javier4piay)
