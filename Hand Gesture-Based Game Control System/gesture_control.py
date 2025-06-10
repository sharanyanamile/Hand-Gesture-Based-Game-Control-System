import numpy as np
import cv2
import time
import math
import imutils
from imutils.video import VideoStream
from pynput.keyboard import Key, Controller

keyboard = Controller()

size_height = 600
size_width = 600

COLOR_RED = (0, 0, 255)
COLOR_BLACK = (0, 0, 0)
color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
THRESH_ACTION = 60

# === Utility Functions ===

def get_centroid(bbox):
    x, y, w, h = bbox
    return ((2 * x + w) // 2, (2 * y + h) // 2)

def draw_circle(frame, center, radius=THRESH_ACTION, color=COLOR_BLACK, thickness=3):
    cv2.circle(frame, center, radius, color, thickness)

def detect_center(img, hand):
    x, y, w, h = [int(v) for v in hand]
    cv2.circle(img, ((2 * x + w) // 2, (2 * y + h) // 2), 2, color['green'], 2)
    return img, ((2 * x + w) // 2, (2 * y + h) // 2)

def draw_controller_left(img, cords):
    size = 40
    y1 = cords[1] - size
    y2 = cords[1] + size
    cv2.circle(img, cords, size, color['blue'], 2)
    return (y1, y2)

def draw_controller_right(img, cords):
    size = 40
    x1 = cords[0] - size
    x2 = cords[0] + size
    cv2.circle(img, cords, size, color['red'], 2)
    return (x1, x2)

def keyboard_events_l(lcord, cord_left, cmd):
    try:
        y1, y2 = cord_left
        _, yl = lcord
        if yl < y1:
            cmd = "w"
        elif yl > y2:
            cmd = "s"
        if cmd:
            print("Detected movement: ", cmd)
            keyboard.press(cmd)
    except Exception as e:
        print("Left command error:", e)
    return cmd

def keyboard_events_r(rcord, cord_right, cmd2):
    try:
        x1, x2 = cord_right
        xr, _ = rcord
        if xr < x1:
            cmd2 = "a"
        elif xr > x2:
            cmd2 = "d"
        if cmd2:
            print("Detected another movement: ", cmd2)
            keyboard.press(cmd2)
    except Exception as e:
        print("Right command error:", e)
    return cmd2

def reset_press_flag(lcord, rcord, cord_left, cord_right, cmd, cmd2):
    try:
        x1, x2 = cord_right
        y1, y2 = cord_left
        _, yl = lcord
        xr, _ = rcord

        if x1 < xr < x2:
            if cmd2:
                keyboard.release(cmd2)
            cmd2 = None
        if y1 < yl < y2:
            if cmd:
                keyboard.release(cmd)
            cmd = None
        press = not ((x1 < xr < x2) and (y1 < yl < y2))
        return press, cmd, cmd2
    except:
        return True, cmd, cmd2

def get_frame(cap):
    res, frame = cap.read()
    if not res or frame is None:
        print("❌ Failed to capture frame")
        raise Exception("Failed to read from webcam")
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=size_width, height=size_height)
    return frame

def create_tracker():
    if hasattr(cv2, 'TrackerCSRT_create'):
        return cv2.TrackerCSRT_create()
    elif hasattr(cv2, 'TrackerKCF_create'):
        print("⚠️ Using KCF tracker instead of CSRT.")
        return cv2.TrackerKCF_create()
    elif hasattr(cv2, 'TrackerMIL_create'):
        print("⚠️ Using MIL tracker instead of CSRT.")
        return cv2.TrackerMIL_create()
    else:
        raise Exception("No compatible tracker found in your OpenCV build. Install opencv-contrib-python.")

# === Main Program ===

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("❌ Webcam not detected. Is it connected or used by another application?")

time.sleep(2.0)

# Countdown before frame capture
TIMER_SETUP = 3
t = time.time()
while True:
    frame = get_frame(cap)
    curr = time.time() - t
    if curr > TIMER_SETUP:
        break
    cv2.putText(frame, str(int(TIMER_SETUP - curr) + 1), (225, 255), cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLOR_RED, 4)
    cv2.imshow("Setup", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

FRAME = frame.copy()
cv2.destroyAllWindows()

# Select ROIs
frame = FRAME.copy()
cv2.putText(frame, 'Select Left Hand for movement (W/S)', (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)
bboxleft = cv2.selectROI("Select Left", frame, False)
cv2.destroyWindow("Select Left")

frame = FRAME.copy()
cv2.putText(frame, 'Select Right Hand for steering (A/D)', (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_RED, 2)
bboxright = cv2.selectROI("Select Right", frame, False)
cv2.destroyWindow("Select Right")

# Validate ROIs
if bboxleft == (0, 0, 0, 0) or bboxright == (0, 0, 0, 0):
    raise Exception("❌ Invalid hand selection. Please rerun and properly select both hand regions.")

# Initialize trackers
trackerleft = create_tracker()
trackerright = create_tracker()
trackerleft.init(FRAME, bboxleft)
trackerright.init(FRAME, bboxright)

press_flag = True
cmd = ""
cmd2 = ""

# === Main Loop ===
while True:
    frame = get_frame(cap)

    success_left, box_left = trackerleft.update(frame)
    success_right, box_right = trackerright.update(frame)

    if success_left and success_right:
        (x, y, w, h) = [int(v) for v in box_left]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        (a, b, c, d) = [int(f) for f in box_right]
        cv2.rectangle(frame, (a, b), (a + c, b + d), (0, 255, 0), 2)

        frame, lcord = detect_center(frame, box_left)
        frame, rcord = detect_center(frame, box_right)

        cord_left = draw_controller_left(frame, (110, 189))
        cord_right = draw_controller_right(frame, (479, 189))

        if press_flag and not cmd:
            cmd = keyboard_events_l(lcord, cord_left, cmd)
        if press_flag and not cmd2:
            cmd2 = keyboard_events_r(rcord, cord_right, cmd2)

        press_flag, cmd, cmd2 = reset_press_flag(lcord, rcord, cord_left, cord_right, cmd, cmd2)

    cv2.imshow("Gesture Controlled Gaming", frame)
    if cv2.waitKey(1) == 13:  # Press Enter to quit
        break

cap.release()
cv2.destroyAllWindows()
