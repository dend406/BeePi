import numpy as np
import cv2

cap = cv2.VideoCapture(0)

priore_frame: np.ndarray = None

while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        print("Error capture.")
        break
    to_show = frame.copy()
    if (frame is not None)and(priore_frame is not None):
        dif_frame: np.ndarray = np.abs(priore_frame.astype(np.int16) - frame).astype(np.uint8)
        imgray = cv2.cvtColor(dif_frame, cv2.COLOR_BGR2GRAY)
        imgray = cv2.blur(imgray, (21, 21) )
        ret, thresh = cv2.threshold(imgray, 10, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for one_line in contours:
            cnt = cv2.minAreaRect(one_line)
            box = cv2.boxPoints(cnt)
            box = np.int0(box)
            img = cv2.drawContours(to_show, [box], 0, (0, 0, 255), 2)
        # cv2.drawContours(to_show, contours, -1, (0, 255, 0), 1)

    cv2.imshow("cap", to_show)
    priore_frame = frame
    key = cv2.waitKey(1)
    if key==27:
        break

cv2.destroyAllWindows()