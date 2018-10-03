import os
import threading
import math
from queue import Queue
import time

class Copper_Hat(threading.Thread):
    def __init__(self, input_queue, cmd_queue, output_queue, target_pos=160):
        threading.Thread.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.cmd_queue = cmd_queue
        self.target = target_pos
        self.cur_dir = True
        self.cur_speed = 0
        self.cur_sector = True #True - по часовой, False - против часовой

        self.prev_err_pos = 0
        self.sum_err_pos = 0
        self.speed = 0
        self.isRunning = True

    def run(self):
        while(self.isRunning):
            if not self.input_queue.empty():
                data = self.input_queue.get()
                print("thr data:", data)
                #speed = self.PID_regulator(data)
                speed = self.P_regulator(data)
                print("Speed: ", speed)
                if speed > 0:
                    pass
                    #Positive direction
                else:
                    pass
                    #Negative direction
            #self.input_queue.task_done() #на другой стороне queue.join()

            if not self.cmd_queue.empty():
                cmd = self.cmd_queue.get()
                print("cmd data:", cmd)
                if cmd == "stopthread":
                    print("thread stop")
                    self.isRunning = False
                if cmd == "gohome":
                    self.go_home()
                if cmd == "stop":
                    self.stop_motor()

            #сли пришла команда на калибровку, то выполняем необходимые действия

            #проверяем состояние кнопки
            state = self.check_btn()
            time.sleep(0.05)


    def go_home(self):
        """Двигаемся до тех пор, пока не сработает концевик
        при этом необходимо точно подобрать скорость, чтобы остановка была минимальная
        Также стоит добавить переменную, которая будет отвечать за определение текущего квадрата головы"""
        pass

    def check_btn(self):
        state = False
        #Проверка состояния кнопки
        #Если нажата, то сообщаем главной программе, он аостанавливает механизм и перестает выполняться пока не будет
        return state

    def PID_regulator(self, pos):
        Kp = 0.02       #
        Ki = 0.01       #
        Kd = 0.05       #

        err_pos = self.target - pos
        print("Err pos:", err_pos)
        self.speed += (Kp * err_pos) + (Kd * self.prev_err_pos) + (Ki * self.sum_err_pos)
        self.prev_err_pos = err_pos
        self.sum_err_pos += err_pos

        if self.speed < -1023:
            self.speed = -1023
        if self.speed > 1023:
            self.speed = 1023
        return self.speed

    def P_regulator(self, pos):
        err_pos = self.target - pos
        Kp = 1 #160 -> 1023 Kp = 6.39
        self.speed += Kp * err_pos

        if self.speed < -1023:
            self.speed = -1023
        if self.speed > 1023:
            self.speed = 1023
        return self.speed

    def stop_motor(self):
        pass