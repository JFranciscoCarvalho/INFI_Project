from datetime import datetime
from threading import Thread
from time import sleep, time

clock_today = 1
clock_seconds = 0
clock_init_day = time()

class ClockThread():
    def __init__(self):
        self._is_alive = False
        Thread.__init__(self)

    def start(self):
        self._is_alive = True
        self.thread = Thread(target=self._run, name='MES_Clock_Thread')
        self.thread.start()

    def stop(self):
        self._is_alive = False
        self.thread.join()

    def _run(self):
        global clock_today, clock_seconds, clock_init_day, is_clock_alive
        while self._is_alive:
            clock_seconds = int(time() - clock_init_day)
            if clock_seconds > 59:
                clock_today += 1
                clock_init_day = time()
                clock_seconds = 0
            sleep(1.0)

def get_clock_today():
    global clock_today
    return clock_today

def get_clock_time():
    global clock_today, clock_seconds
    return f"Day {clock_today:2d} {clock_seconds:2d} s"

def set_time(t, s, i):
    global clock_today, clock_seconds, clock_init_day
    clock_today = t
    clock_seconds = s
    clock_init_day = i

def get_time_to_erp():
    global clock_today, clock_seconds
    return f"{clock_today} {clock_seconds}"

def get_time():
    return datetime.now().strftime("%d/%m/%y %H:%M:%S")

def sleep_next_cycle(init_cycle, cycle):
    if (time() - init_cycle < cycle):
        sleep(cycle - (time() - init_cycle))