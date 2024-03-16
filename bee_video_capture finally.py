import numpy as np
import cv2
from sklearn.cluster import DBSCAN

# Ініціалізуємо захоплення відео з камери
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Встановлюємо ширину кадру
cap.set(4, 720)   # Встановлюємо висоту кадру
prior_frame = None  # Змінна для зберігання попереднього кадру
epsilon = 100  # Параметр для DBSCAN

while cap.isOpened():
    # Захоплюємо кадр з камери
    ret, frame = cap.read()
    if not ret:
        print("Error capture.")
        break

    # Копіюємо кадр для відображення
    to_show = frame.copy()
    to_show = to_show[200:, :]  # Обрізаємо верхню частину кадру
    frame = frame[200:, :]      # Обрізаємо верхню частину кадру

    # Обробка руху
    if prior_frame is not None:
        # Вираховуємо різницю між попереднім і поточним кадрами
        dif_frame = cv2.absdiff(prior_frame, frame)
        dif_frame = cv2.GaussianBlur(dif_frame, (5, 5), 0)

        # Перетворюємо до відтінків сірого
        imgray = cv2.cvtColor(dif_frame, cv2.COLOR_BGR2GRAY)
        # Бінаризуємо зображення
        _, binary_image = cv2.threshold(imgray, 30, 255, cv2.THRESH_BINARY)
        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

        # Знаходимо контури
        contours, _ = cv2.findContours(binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Збираємо координати точок контурів
            coordinates = np.vstack([cnt.reshape(-1, 2) for cnt in contours])

            # Кластеризуємо точки контурів за допомогою DBSCAN
            clustering = DBSCAN(eps=epsilon, min_samples=2).fit(coordinates)

            # Отримуємо унікальні мітки кластерів
            unique_labels = set(clustering.labels_)

            # Проходимося по кожній мітці кластеру
            for label in unique_labels:
                if label == -1:
                    continue

                # Отримуємо точки кластера з поточною міткою
                cluster_points = coordinates[clustering.labels_ == label]
                x, y, w, h = cv2.boundingRect(cluster_points)

                # Відображаємо прямокутник на відображеному кадрі
                roi = frame[y:y+h, x:x+w]
                avg_color = np.mean(roi, axis=(0, 1))
                # Перевіряємо кольори та малюємо прямокутник з відповідним кольором
                if (95 < avg_color[0] < 103 and 110 < avg_color[2] < 120):
                    cv2.rectangle(to_show, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    print("Оса")
                elif (105 < avg_color[0] < 111 and 124 < avg_color[2] < 130):
                    cv2.rectangle(to_show, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print("Бджола")

        # Відображаємо кадр
        cv2.imshow("cap", to_show)

    # Зберігаємо поточний кадр для майбутнього порівняння
    prior_frame = frame
    # Очікуємо на натискання клавіші 'Esc' для виходу з циклу
    key = cv2.waitKey(1)
    if key == 27:
        break

# Закриваємо вікна та вивільняємо ресурси
cv2.destroyAllWindows()
cap.release()
