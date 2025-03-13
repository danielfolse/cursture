import mediapipe as mp
from mediapipe.python.solutions.hands import HandLandmark
import pyautogui  # Import pyautogui for controlling the mouse
import pygetwindow as gw  # Import pygetwindow for window manipulation
import time

class HandtoMouse:
    def __init__(self):
      self.prev_mouse_x = None
      self.prev_mouse_y = None
      self.hand_flare_detected = False
      self.last_click_time = 0  # Initialize the last click timestamp

    def moveMouse(self, detected_image):
      if detected_image.multi_hand_landmarks:
        index_finger_tip = detected_image.multi_hand_landmarks[0].landmark[HandLandmark.INDEX_FINGER_TIP]  # Use the wrist landmark
        self.convertToMouse(index_finger_tip.x, index_finger_tip.y)  # Convert the wrist position to mouse position
        self.detectPinch(detected_image.multi_hand_landmarks[0].landmark)  # Detect pinch gesture
      return

    def convertToMouse(self, x, y):
      screen_width, screen_height = pyautogui.size()
      # Normalize the wrist coordinates to the detected image bounds
      normalized_x = x
      normalized_y = y
      # Scale the normalized coordinates to the screen size
      mouse_x = int(normalized_x * screen_width)
      if mouse_x > screen_width:
        mouse_x = screen_width - 5
      elif mouse_x < 0:
        mouse_x = 5
      mouse_y = int(normalized_y * screen_height)
      if mouse_y > screen_height:
        mouse_y = screen_height - 5 
      elif mouse_y < 0:
        mouse_y = 5

      # Smooth the mouse cursor movement
      if self.prev_mouse_x is not None and self.prev_mouse_y is not None:
        mouse_x = int((mouse_x + self.prev_mouse_x) / 2)
        mouse_y = int((mouse_y + self.prev_mouse_y) / 2)

      self.prev_mouse_x = mouse_x
      self.prev_mouse_y = mouse_y
      pyautogui.moveTo(mouse_x, mouse_y)
    
    def detectPinch(self, landmarks):
      index_finger_tip = landmarks[HandLandmark.INDEX_FINGER_TIP]
      thumb_tip = landmarks[HandLandmark.THUMB_TIP]
      # Calculate the distance between the index finger tip and thumb tip
      distance = ((index_finger_tip.x - thumb_tip.x) ** 2 + (index_finger_tip.y - thumb_tip.y) ** 2) ** 0.5

      # Check if other fingers are not extended
      middle_finger_tip = landmarks[HandLandmark.MIDDLE_FINGER_TIP]
      ring_finger_tip = landmarks[HandLandmark.RING_FINGER_TIP]
      pinky_tip = landmarks[HandLandmark.PINKY_TIP]

      middle_finger_base = landmarks[HandLandmark.MIDDLE_FINGER_MCP]
      ring_finger_base = landmarks[HandLandmark.RING_FINGER_MCP]
      pinky_base = landmarks[HandLandmark.PINKY_MCP]

      if (middle_finger_tip.y > middle_finger_base.y and
        ring_finger_tip.y > ring_finger_base.y and
        pinky_tip.y > pinky_base.y and
        distance < 0.05):  # Adjust the threshold as needed
        self.clickMouse()

    def clickMouse(self):
      current_time = time.time()
      if current_time - self.last_click_time >= 1:  # Check if 0.5 seconds have passed since the last click
        pyautogui.click()
        self.last_click_time = current_time  # Update the last click timestamp

    def detectHandFlare(self, landmarks):
      # Check if all fingers are extended
      index_finger_tip = landmarks[HandLandmark.INDEX_FINGER_TIP]
      middle_finger_tip = landmarks[HandLandmark.MIDDLE_FINGER_TIP]
      ring_finger_tip = landmarks[HandLandmark.RING_FINGER_TIP]
      pinky_tip = landmarks[HandLandmark.PINKY_TIP]

      index_finger_base = landmarks[HandLandmark.INDEX_FINGER_MCP]
      middle_finger_base = landmarks[HandLandmark.MIDDLE_FINGER_MCP]
      ring_finger_base = landmarks[HandLandmark.RING_FINGER_MCP]
      pinky_base = landmarks[HandLandmark.PINKY_MCP]

      if (index_finger_tip.y < index_finger_base.y and
        middle_finger_tip.y < middle_finger_base.y and
        ring_finger_tip.y < ring_finger_base.y and
        pinky_tip.y < pinky_base.y):
        if not self.hand_flare_detected:
          self.hand_flare_detected = True
          self.makeWindowBigger()
      else:
        self.hand_flare_detected = False

    def makeWindowBigger(self):
      window = gw.getActiveWindow()
      print("making window bigger")
      if window:
        window.resizeTo(window.width + 100, window.height + 100)
