# EduFace: Automatic Facial Recognition Attendance System

EduFace is a touchless attendance system powered by AI and computer vision. It replaces manual roll calls by recognizing registered faces in real time and logging attendance records instantly into a database.

---

## 🚀 Features

* **Touchless Attendance:** Marks attendance automatically in seconds when a registered user looks into the camera.
* **Proxy Prevention:** Stops "buddy punching" by validating unique facial features.
* **Real-Time Log Updates:** Live dashboard tracking for users and administrators with precise timestamps.
* **Lightweight & Mobile-Friendly:** Runs efficiently on standard hardware, webcams, and mobile environments via Termux.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript
* **Backend:** Python (Flask, OpenCV)
* **Database:** SQLite

---

## 🔄 How It Works

1. **Registration:** Users upload a face photo to generate a unique facial feature representation.
2. **Live Scanning:** The webcam captures frames in real-time while OpenCV isolates facial boundaries.
3. **Instant Matching:** The backend matches live facial vectors against stored database records and logs attendance.

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/AbhinavChauhan67/EduFace.git](https://github.com/AbhinavChauhan67/EduFace.git)
cd EduFace
```

### 2. Running EduFace
```bash
python app.py
```
