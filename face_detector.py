import numpy as np
from  math import sqrt
from statistics import median
import cv2
from gpio_thread import Copper_Hat
from queue import Queue

_WIDTH = 320
_HEIGHT = 240

cap = cv2.VideoCapture(1)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap.set(3, _WIDTH)
cap.set(4, _HEIGHT)

prev_face_x = int(_WIDTH / 2)
prev_face_y = int(_HEIGHT / 2)

d_min = 999
d_cur = 999

face_cur_x = 0
face_cur_y = 0

face_x = 0

l_faces = []
x_cur = 0
y_cur = 0
w_cur = 0
h_cur = 0
data_queue = Queue()
cmd_queue = Queue()
return_queue = Queue()

copperHat = Copper_Hat(data_queue, cmd_queue, return_queue, target_pos=160)
copperHat.start()
while(True):
    ret, frame = cap.read()
    d_min = _WIDTH ** 2 * 1.4

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    face_x = -1
    for (x, y, w, h) in faces:
        face_cur_x = x + w / 2
        face_cur_y = y + h / 2
        d_cur = sqrt((face_cur_x - prev_face_x) ** 2 + \
                     (face_cur_x - prev_face_x) ** 2)
        #print("face pos:", (x, y, w, h), end=' ')
        if (d_cur < d_min):
            d_min = d_cur
            face_x = face_cur_x
            prev_face_x = face_cur_x
            prev_face_y = face_cur_y
            x_cur = x
            y_cur = y
            w_cur = w
            h_cur = h

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)

    if face_x > 0:
        cv2.rectangle(frame, (x_cur, y_cur), (x_cur + w_cur, y_cur + h_cur), (0, 0, 255), 2)
        l_faces.append(face_x)
        if len(l_faces) == 11:
            face_x = median(l_faces)
            l_faces.pop(0)
            signal = int(int(_WIDTH / 2) - face_x)
            print('face is', face_x, 'S:', signal)
            data_queue.put(face_x)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # When everything done, release the capture
cmd_queue.put("stopthread")

cap.release()
cv2.destroyAllWindows()
