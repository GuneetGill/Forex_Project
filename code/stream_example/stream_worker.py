from queue import Queue
import threading
import time
from infrastructure.log_wrapper import LogWrapper
from models.live_api_price import LiveApiPrice


class WorkProcessor(threading.Thread):

    #send in a queue
    def __init__(self, work_queue: Queue):
        super().__init__()
        self.work_queue = work_queue
        self.log = LogWrapper("WorkProcessor")


    def run(self):
        while True:
            #infinite loop unril work is given to it then it will do somethign with it
            work: LiveApiPrice = self.work_queue.get()
            self.log.logger.debug(f"New Work: {work}")
            time.sleep(7)


