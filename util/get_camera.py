import cv2

camera_id = 0
cap = cv2.VideoCapture(camera_id)

try:
    while True:
        ret, frame = cap.read()
        if ret:
            w, h, ch = frame.shape
            print("Frame dimensions:", w, h)
            image_center = [(h // 2), (w // 2)]
            cv2.circle(frame, (int(h // 2), int(w // 2)), 10, (0, 0, 255), 2)
            cv2.imshow('', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break  # Quit if 'q' is pressed
finally:
    cap.release()
    cv2.destroyAllWindows()
