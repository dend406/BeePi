import numpy as np
import cv2
import RPi.GPIO as GPIO
from sklearn.cluster import DBSCAN
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
priore_frame = None
epsilon = 100

# Визначаємо номер GPIO піна, до якого підключений сервопривод
servo_pin = 19

# Ініціалізація GPIO режиму
GPIO.setmode(GPIO.BCM)
# Встановлюємо пін на вивід
GPIO.setup(servo_pin, GPIO.OUT)

# Створюємо об'єкт PWM для керування сервоприводом
pwm = GPIO.PWM(servo_pin, 50)  # 50 Гц (20 мс циклу)


def set_angle(angle):
    global pwm
    pwm.start(1)
    duty = angle / 18 + 2  # Розрахунок ширина імпульсу для кута
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)  
    

while True:
    set_angle(0)
    ret, frame = cap.read()
    to_show = frame.copy()
    to_show = to_show[200:, :]
    frame = frame[200:, :]
    

    if priore_frame is not None:
        dif_frame = cv2.absdiff(priore_frame, frame)
        dif_frame = cv2.GaussianBlur(dif_frame, (5, 5), 0)

        imgray = cv2.cvtColor(dif_frame, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(imgray, 30, 255, cv2.THRESH_BINARY)
        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

        contours, _ = cv2.findContours(binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            coordinates = np.vstack([cnt.reshape(-1, 2) for cnt in contours])

            clustering = DBSCAN(eps=epsilon, min_samples=2).fit(coordinates)

            unique_labels = set(clustering.labels_)

            for label in unique_labels:
                if label == -1:
                    continue

                cluster_points = coordinates[clustering.labels_ == label]
                x, y, w, h = cv2.boundingRect(cluster_points)
                #cv2.rectangle(to_show, (x, y), (x + w, y + h), (0, 0, 255), 2)


                roi = frame[y:y+h, x:x+w]
                avg_color = np.mean(roi, axis=(0, 1))
                #print(avg_color)
                if (95 < avg_color[0] < 103 and 110 < avg_color[2] < 120):
                    cv2.rectangle(to_show, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    set_angle(90)
                    print("Оса")
                elif (105 < avg_color[0] < 111 and 124 < avg_color[2] < 130):
                    cv2.rectangle(to_show, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print("Бджола")

        cv2.imshow("cap", to_show)

    priore_frame = frame
    key = cv2.waitKey(1)
    if key == 27:
        break

pwm.stop(1)
cv2.destroyAllWindows()
cap.release()
