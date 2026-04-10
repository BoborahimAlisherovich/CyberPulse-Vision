# 🚀 CyberPulse Vision | Virtual Mouse & AR Hand Tracker

CyberPulse Vision is a futuristic, highly-optimized Computer Vision project built natively in Python. It tracks your hands in real-time using AI and overlays a gorgeous **Neon AR Effect**. More importantly, it turns your hand into a fully functional **Virtual Mouse** to completely control your computer without touching it!

## ✨ Features

- 🖱️ **Virtual Mouse Control:** Move your cursor across the entire computer screen.
- 👆 **Click & Double-Click:** Effortlessly snap your fingers to Left Click. Snap twice rapidly (thanks to the `0-delay` state logic) to Double-Click and open applications in Windows.
- 🎨 **Holographic Neon Bloom:** Realistic, vibrant glowing AR overlays that dynamically change color and track the exact skeletal frame of your hands.
- ⚡ **Zero-Lag Input Engine:** Completely bypasses standard PyAutoGUI input chunking delays using `PAUSE = 0` and an optimized Gaussian Blur core to deliver silky-smooth desktop-grade FPS.
- 🔧 **Modern AI Backend:** Defeats Python 3.13 deprecation limitations; runs exclusively onto MediaPipe's cutting-edge edge AI `Tasks API` (`vision.HandLandmarker`).
- 🧑‍💻 **Gesture HUD:** A dark translucent gaming-style Heads Up Display (HUD) tracks your exact hand states (Move mode, Click ready, FPS metrics) dynamically over your webcam feed.

## 🤲 How to Use Gestures (Qo'llanma)

1. **Move Cursor (`Kursor harakati`)**: 
   Release **only your Index Finger** (Ko'rsatkich barmoq). Keep everything else folded. Just point at the screen and move your hand; your computer's mouse will follow!

2. **Prepare to Click (`Tayyorgarlik`)**: 
   Raise your **Middle Finger** alongside your Index Finger (simulating a 'Peace ✌️' sign). The mouse will pause briefly for precision, and the screen will announce `MOUSE: READY/CLICK`.

3. **Click & Double Click (`Bosish`)**:
   Pinch your **Index and Middle fingers** together! A glowing green line will bridge your fingertips, and your computer will register a normal physical Left Click. Note:
   - For a **Single Click**: Touch both fingertips together.
   - For a **Double Click**: Vigorously snap the two fingers together *twice* in fast succession (Touch -> Re-open -> Touch).

## 🛠️ Installation

Ensure your webcam is connected properly before starting the application.

1. Install dependencies from the terminal:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```
   *(Note: The very first time you boot the tracker, it will securely auto-download the `.task` tracking AI model locally. Allow it five seconds).*

To safely exit the application, make sure the camera window is clicked/active and press the **`q`** key on your keyboard.
