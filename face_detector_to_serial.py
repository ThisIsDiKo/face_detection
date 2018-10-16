import cv2
from statistics import median
import time
import serial
import threading

_WIDTH = 320
_HEIGHT = 240
_NUMBER_OF_VIDEO_INPUT = 0

_SHOW_FRAMES = 1

_LENGTH_OF_SAMPLES_ARRAY = 5

video_input = cv2.VideoCapture(_NUMBER_OF_VIDEO_INPUT)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

video_input.set(3, _HEIGHT)
video_input.set(4, _HEIGHT)

face_samples = []
face_pos = 0
err_target = 0

mcu_serial = serial.Serial()
mcu_serial.baudrate = 115200
mcu_serial.port = 'COM7'
mcu_serial.open()

if mcu_serial.is_open:
    print('Serial connection set')
else:
    print('No Serial.connection')

data_from_mcu = ''
data_to_send = ''

def write_to_serial(serial_port, data):
    print('thr str...', end='')
    serial_port.write(data)
    print('end')



while(True):
    start_time = time.clock()
    ret, frame = video_input.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5) # 1.3, 5

    face_perimeter_max = 0
    face_x_pos = -1
    face_y_pos = -1
    number_of_faces = 0
    for (x, y, w, h) in faces:
        number_of_faces += 1
        if w + h > face_perimeter_max:
            face_perimeter_max = w + h
            face_x_pos = int(x + w / 2)
            face_y_pos = int(y + h / 2)

        if _SHOW_FRAMES:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)

    if face_x_pos >= 0:
        if _SHOW_FRAMES:
            cv2.circle(frame, (face_x_pos, face_y_pos), 5, (0, 0, 255), 3)
        face_samples.append(face_x_pos)
        if len(face_samples) == _LENGTH_OF_SAMPLES_ARRAY:
            face_pos = median(face_samples)
            face_samples.pop(0)
            err_target = int(int(_WIDTH / 2) - face_pos)
            data_to_send = bytes('p:{}\r\n'.format(err_target), 'utf-8')
            #TODO: отправка сообщения p:<err_target>\r\n
            if mcu_serial.is_open:
                #thread = threading.Thread(target=write_to_serial, args=(mcu_serial, data_to_send,))
                #thread.start()
                mcu_serial.write(data_to_send)

    else:
        #TODO: добавить случай потери цели, через 5 секунд GO HOME
        pass

    if mcu_serial.is_open:
        if mcu_serial.inWaiting() > 0:
            data_from_mcu += mcu_serial.read(mcu_serial.inWaiting()).decode('ascii')
            if data_from_mcu.endswith('\n'):
                print('From MCU:', data_from_mcu)
                data_from_mcu = ''


    if _SHOW_FRAMES:
        cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_rate = round(1 / (time.clock() - start_time))

    print('num of faces:{:>2}  target:{:>4}  err:{:>4}  fps:{:>3}'.format(number_of_faces,
                                                                          face_pos,
                                                                          err_target,
                                                                          frame_rate))


video_input.release()
cv2.destroyAllWindows()
