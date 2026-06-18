import mediapipe as mp
import time
import cv2 as cv
import numpy as np
import math
import pycaw
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# This class finds hands using MediaPipe and controls the volume using finger distance.
class HandDetector():
    def __init__(self, mode=False, maxhands=2, modelComplexity=1, detectionConfidence=0.5, trackingConfidence=0.5):
        """
        Set up hand tracking and volume control settings.

        :param mode: If True, it checks each frame separately; if False, it keeps tracking.
        :param maxhands: Maximum number of hands to find.
        :param modelComplexity: Level of detail for the hand model.
        :param detectionConfidence: How sure the system needs to be to say a hand is present.
        :param trackingConfidence: How sure the system needs to be to keep tracking the hand.
        """
        self.mode = mode
        self.maxHands = maxhands
        self.detectionConfidence = detectionConfidence
        self.trackinConfidence = trackingConfidence
        self.modelComplexity = modelComplexity

        # Setup MediaPipe hands module and drawing tool
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplexity, self.detectionConfidence, self.trackinConfidence)
        self.mpDraw = mp.solutions.drawing_utils

        # Setup volume control using Pycaw
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = self.interface.QueryInterface(IAudioEndpointVolume)
        self.volume.GetMasterVolumeLevel()
        self.volume_range = self.volume.GetVolumeRange()
        self.min_volume = self.volume_range[0]
        self.max_volume = self.volume_range[1]
        self.volume_bar = 400
        self.volume_percentage = 0

    def findHand(self, image, draw=False):
        """
        Find hands in the camera image and draw them if needed.

        :param image: Camera image
        :param draw: If True, draw the hand landmarks
        :return: Image with or without drawings
        """
        RGB_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        self.mp_hand_result = self.hands.process(RGB_image)
        hand_landmarks = self.mp_hand_result.multi_hand_landmarks

        if hand_landmarks:
            for fist in hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(image, fist, self.mpHands.HAND_CONNECTIONS)

        return image

    def findPosition(self, image, handNo=0, draw=True):
        """
        Get the positions of hand points.

        :param image: Image from the camera
        :param handNo: Which hand to use if there are multiple
        :param draw: If True, show point numbers
        :return: List of point numbers with x and y locations
        """
        landmarkList = []
        hand_landmarks = self.mp_hand_result.multi_hand_landmarks

        if hand_landmarks:
            my_fist_1 = hand_landmarks[handNo]

            for index, landmarks in enumerate(my_fist_1.landmark):
                height, width, channels = image.shape
                pos_x, pos_y = int(landmarks.x * width), int(landmarks.y * height)
                landmarkList.append([index, pos_x, pos_y])

                if draw:
                    cv.putText(image, str(index), (pos_x, pos_y), 1, 1, (0, 0, 0), 1)

        return landmarkList

    def controlVolume(self, image, landmark_positions):
        """
        Change the volume depending on how far the thumb and index finger are.

        :param image: Image from the camera
        :param landmark_positions: List of hand point positions
        :return: Updated image, volume bar height, and percentage
        """
        if len(landmark_positions) != 0:
            thumb_x, thumb_y = landmark_positions[4][1], landmark_positions[4][2]
            index_x, index_y = landmark_positions[8][1], landmark_positions[8][2]
            center_x, center_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2

            cv.circle(image, (thumb_x, thumb_y), 5, (255, 255, 0), cv.FILLED)
            cv.circle(image, (index_x, index_y), 5, (255, 255, 0), cv.FILLED)
            cv.circle(image, (center_x, center_y), 5, (0, 0, 0), cv.FILLED)
            cv.line(image, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 555), 3)

            distance = math.hypot(thumb_x - index_x, thumb_y - index_y)

            self.volume_bar = np.interp(distance, [20, 150], [400, 150])
            self.volume_percentage = np.interp(distance, [20, 150], [0, 100])
            converted_volume = np.interp(self.volume_percentage, [0, 100], [-20, self.max_volume])

            if distance < 85 and distance > 51:
                converted_volume = np.interp(distance, [0, 85], [-35, -11])
            elif distance < 52 and distance > 20:
                converted_volume = np.interp(distance, [0, 52], [-65, -22])
            elif distance < 20:
                converted_volume = self.min_volume

            self.volume.SetMasterVolumeLevel(converted_volume, None)

        return [image, self.volume_bar, self.volume_percentage]

def main():
    width_camera, height_camera = 640, 480  # Size of camera screen
    previous_time = 0  # For FPS calculation

    # Open the camera
    camera = cv.VideoCapture(0)
    camera.set(3, width_camera)
    camera.set(4, height_camera)

    # Start hand detector
    handDetector = HandDetector(detectionConfidence=0.8)

    while True:
        success, cam_image = camera.read()

        # Find hand and hand points
        cam_image = handDetector.findHand(cam_image, True)
        landmark_positions = handDetector.findPosition(cam_image, draw=False)

        # Adjust volume if fingers are found
        cam_image, volume_bar, volume_percentage = handDetector.controlVolume(cam_image, landmark_positions)

        if volume_bar:
            cv.rectangle(cam_image, (50, 150), (85, 400), (0, 255, 0), 2)
            cv.rectangle(cam_image, (50, int(volume_bar)), (85, 400), (0, 255, 0), cv.FILLED)
            cv.putText(cam_image, f"{int(volume_percentage)}%", (55, 390), 1, 0.9, (0, 0, 0), 2)

        # Show FPS
        current_time = time.time()
        fps = 1 / (current_time - previous_time)
        previous_time = current_time
        cv.putText(cam_image, f"{int(fps)} fps", (10, 24), cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        cv.imshow("Main-camera", cam_image)

        # Press 'q' to exit
        if cv.waitKey(1) == ord('q'):
            break

    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
