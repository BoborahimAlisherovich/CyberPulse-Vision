# AR Neon Hand Tracker

This is a real-time computer vision project that tracks hands via webcam and overlays a futuristic neon / hologram effect on top of them. Built with OpenCV and MediaPipe.

## Features ✨
- **Real-Time Hand Tracking:** Tracks up to two hands smoothly.
- **Neon AR Overlay:** Replaces standard static lines with a glowing dynamic bloom effect.
- **Dynamic Colors:** Colors shift and rotate across the hue spectrum based on real-world time passing.
- **Animated Links:** If two hands are held up, glowing holographic chains link the fingers of both hands.
- **Gesture Detection:** Detects basic gestures like `FIST`, `OPEN HAND`, `PEACE`, or counts the number of held-up fingers.
- **Holographic UI HUD:** FPS and hand count are presented on a dark translucent overlay resembling gaming / AR head-up displays.

## How it works 🛠️

1. **Detection (MediaPipe):** The script first feeds the webcam frame (converted to RGB) into MediaPipe's Hand machine-learning model. It extracts the 21 3D joint landmarks for each hand found.
2. **Gesture Mechanics:** Compares the Y-coordinates of finger tips directly against lower joint coordinates to mathematically estimate which fingers are extended versus folded. 
3. **Neon Effect (OpenCV):**
   - The system creates a blank pitch-black image ("canvas").
   - It draws thick, hyper-bright connected lines on this black canvas mapping the hand skeletal structure. 
   - A heavy Gaussian Blur is applied directly to this canvas. This diffuses the bright lines, turning them into a realistic "glow/bloom" field.
   - Using OpenCV's `addWeighted`, the blurred glow canvas is additively layered over the original camera image.
   - Extremely thin pure white lines are strictly drawn completely on top as the "core" of the light tubes (just like real neon lights).

## Installation

Ensure you have Python installed. It is highly recommended to use a virtual environment.

Open your terminal in this directory and install the requirements:

```bash
pip install -r requirements.txt
```

## Running the Application

Execute the script from the terminal:

```bash
python main.py
```

*Note: Ensure your webcam is unplugged and firmly connected if it fails to open. Once running, bring your hands naturally into view.* 

**Press `q` on your keyboard** while the window is focused to exit the program safely.
