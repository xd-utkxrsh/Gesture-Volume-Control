# Gesture Volume Control Using Computer Vision

A real-time hand gesture recognition system that controls system volume using a webcam. The project uses MediaPipe for hand tracking, OpenCV for image processing, and PyCaw for Windows audio control.

---

## Features

- Real-time hand gesture recognition
- Touch-free system volume control
- Hand landmark detection using MediaPipe
- Dynamic volume adjustment based on finger distance
- Visual volume bar and percentage display

---

## Technologies Used

- Python
- OpenCV
- MediaPipe
- PyCaw
- NumPy
- Comtypes

---

## How It Works

1. Captures webcam feed using OpenCV.
2. Detects hand landmarks using MediaPipe.
3. Measures the distance between the thumb and index finger.
4. Maps the distance to the system volume range.
5. Adjusts system audio in real time using PyCaw.

---

## Installation

Install the required packages:

```bash
pip install opencv-python mediapipe numpy pycaw comtypes
```

---

## Run

```bash
python main.py
```

---

## Project Structure

```text
GestureVolumeControl/
│
├── main.py
├── Images/
│   ├── zero.png
│   ├── forty.png
│   └── hundred.png
└── README.md
```

---

## Demo

| Volume 0% | Volume 40% | Volume 100% |
|-----------|------------|-------------|
| ![](Images/zero.png) | ![](Images/forty.png) | ![](Images/hundred.png) |

---

## Future Improvements

- Gesture-based mute/unmute
- Multi-hand support
- Improved visual feedback
- Cross-platform audio control

---

## Author

Utkarsh Srivastav

GitHub: https://github.com/xd-utkxrsh