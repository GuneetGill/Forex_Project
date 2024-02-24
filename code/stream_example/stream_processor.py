import copy
from queue import Queue
import random
import threading
import time
from stream_example.stream_base import StreamBase #base class


class PriceProcessor(StreamBase):

    def __init__(self, shared_prices, price_lock: threading.Lock, price_events, logname, pair, work_queue: Queue):
        super().__init__(shared_prices, price_lock, price_events, logname)
        self.pair = pair
        self.work_queue = work_queue


    def process_price(self):

        price = None

        try:
            #acquire the price lock
            self.price_lock.acquire()

            #make a copy of the price,since its deep copy we will have access to it even after
            #lock is closed
            price = copy.deepcopy(self.shared_prices[self.pair])
        except Exception as error:
            self.log_message(f"CRASH : {error}", error=True)
        finally:
            #release lock
            self.price_lock.release()

        if price is None:
            self.log_message("NO PRICE", error=True)
        else:
            #here is where we would do something with the info 
            #but for us we are just doing some random stuff for example sake
            self.log_message(f"Found price : {price}")
            time.sleep(random.randint(2,5))
            self.log_message(f"Done processing price : {price}")
            if random.randint(0,5) == 3:
                self.log_message(f"Adding work : {price}")
                self.work_queue.put(price)

    def run(self):

        while True:
            #infinite loop
            #wait until price event has been triggered
            self.price_events[self.pair].wait()
            #logic 
            self.process_price()
            #sets is_set to False so price streamer realizes its False so it reacts to latest price
            self.price_events[self.pair].clear()

            '''
            we get a new live price, update shared prices and fire new price event
            then look to see if event is set
            if it isnt we set it

            '''