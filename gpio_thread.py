import os
import threading
import math
from queue import Queue

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

    def run(self):
        while(True):
            data = self.input_queue.get()
            print("thr data:", data)
            speed = self.PID_regulator(data)
            print("Speed: ")
            if speed > 0:
                pass
                #Positive direction
            else:
                pass
                #Negative direction
            #self.input_queue.task_done() #на другой стороне queue.join()

            cmd = self.cmd_queue.get()
            print("cmd data:", cmd)

            #сли пришла команда на калибровку, то выполняем необходимые действия

            #проверяем состояние кнопки
            state = self.check_btn()


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
        speed = 0
        P = 0.02
        I = 0.01
        D = 0.05

        err_pos = self.target - pos
        self.speed += (P * err_pos) + (D * self.prev_err_pos) + (I * self.sum_err_pos)
        self.prev_err_pos = err_pos
        self.sum_err_pos += err_pos

        if speed < -1023:
            self.speed = -1023
        if speed > 1023:
            self.speed = 1023
        return self.speed