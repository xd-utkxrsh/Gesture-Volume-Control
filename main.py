import cv2 as cv
import time
from trackingModule import HandDetector


def main():
    """
    Main function to use the webcam, detect hand gestures, and change system volume based on those gestures.
    It uses the HandDetector class to track hand points and control volume by checking the gap between the thumb and index finger.
    """
    width_camera, height_camera = 640, 480  # Set the size of the webcam window
    previous_time = 0  # Used to calculate the frame rate

    # Start the webcam
    camera = cv.VideoCapture(0)
    camera.set(3, width_camera)  # Width
    camera.set(4, height_camera)  # Height

    # Create a HandDetector object
    handDetector = HandDetector()

    # Keep reading frames from the webcam
    while True:
        success, cam_image = camera.read()  # Read one frame
        if not success:
            print("Failed to capture image")  # If frame not read, show error
            break

        # Detect hand and draw landmarks
        cam_image = handDetector.findHand(cam_image, draw=True)

        # Get positions of fingers and hand points
        landmark_positions = handDetector.findPosition(cam_image, draw=False)

        # Adjust system volume using thumb and index finger distance
        cam_image, volume_bar, volume_percentage = handDetector.controlVolume(cam_image, landmark_positions)

        # If hand is detected and volume bar is available, draw the volume bar
        if volume_bar:
            cv.rectangle(cam_image, (50, 150), (85, 400), (0, 255, 0), 2)  # Outline of volume bar
            cv.rectangle(cam_image, (50, int(volume_bar)), (85, 400), (0, 255, 0), cv.FILLED)  # Fill volume bar
            cv.putText(cam_image, f"{int(volume_percentage)}%", (55, 390), 1, 0.9, (0, 0, 0), 2)  # Show volume %

        # Calculate and display FPS
        current_time = time.time()
        fps = 1 / (current_time - previous_time)
        previous_time = current_time
        cv.putText(cam_image, f"{int(fps)} fps", (10, 24), cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        # Show the webcam window
        cv.imshow("Hand Gesture Volume Control", cam_image)

        # Press 'q' to exit the program
        if cv.waitKey(1) == ord('q'):
            break

    camera.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
