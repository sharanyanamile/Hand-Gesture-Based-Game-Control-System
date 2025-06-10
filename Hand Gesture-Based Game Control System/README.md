'''Hand Gesture-Based Game Control System🎮🖐️
A simple yet exciting project that allows you to control game actions using hand gestures through your webcam!
🔍 Overview
This project uses OpenCV, imutils, and pynput to track hand movements and convert them into keyboard inputs for basic gaming controls:

Left hand: Accelerate (W) and Brake (S)

Right hand: Steer Left (A) and Steer Right (D)

🚀 How It Works
Run gesture_control.py.

Look at the webcam. After a short countdown, the app will capture a frame.

Select your left hand (used for acceleration/brake) using the mouse and press Enter.

Then select your right hand (used for steering) and press Enter.

Once initialized, move your hands in front of the webcam:

Move left hand up/down → W / S

Move right hand left/right → A / D

The system maps your hand movements to game-like controls using bounding box tracking.

🛠️ Requirements
Install dependencies using:
pip install opencv-python opencv-contrib-python imutils pynput
Make sure your webcam is connected and not used by other applications.

⚠️ Notes
This is a basic prototype — best used for fun or educational purposes.

Works better in good lighting and with clear background contrast.
If the trackers lose your hand, re-run the script and reselect the ROIs.
