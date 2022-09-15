import time
import queue
import ctypes
import atexit
import threading

__all__ = ["push"]

ctypes.windll.winmm.timeBeginPeriod(1)


class __MessageQueue(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.stop_event = threading.Event()
        self.queue = queue.PriorityQueue()
        atexit.register(self.stop)
        self.start()

    def stop(self):
        self.stop_event.set()
        self.join()

    def push(self, message, delay: float = 0.0, repeat: int = 0):
        t = time.time() + delay
        self.queue.put((t, delay, repeat, message))
        return t

    def run(self):
        while not self.stop_event.is_set():
            if self.queue.empty():
                time.sleep(0.002)
                continue

            t, d, r, m = self.queue.get()
            now = time.time()

            if now < t:
                self.queue.put((t, d, r, m))
                time.sleep(0.002)
                continue

            m()

            if r != 0:
                self.queue.put((t + d, d, max(r - 1, -1), m))


__message_queue = __MessageQueue()
push = __message_queue.push

if __name__ == "__main__":
    push(lambda: print(time.time()), 0.5, -1)
    time.sleep(10)