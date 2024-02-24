import json
from queue import Queue
import threading
import time

from stream_example.stream_prices import PriceStreamer
from stream_example.stream_processor import PriceProcessor
from stream_example.stream_worker import WorkProcessor

def load_settings():
    with open("./bot/settings.json", "r") as f:
        return json.loads(f.read())

def run_streamer():

    #load up settings
    settings = load_settings()

    #create new objects that will be indexed by key (which is pair) and pair which is live api price
    shared_prices = {}
    #indexed by key(pair name)
    shared_prices_events = {}
    #to lock shared prices when a process is happening
    shared_prices_lock = threading.Lock()
    work_queue = Queue()

    
    for p in settings['pairs'].keys():
        #create new event 
        shared_prices_events[p] = threading.Event()
        #create object that is intilzed with keys
        shared_prices[p] = {}

    #empty list
    threads = []
    
    price_stream_t = PriceStreamer(shared_prices, shared_prices_lock, shared_prices_events)
    ''' 
    A daemon thread is a thread that runs in the background. 
    When the main program exits, all daemon threads are abruptly stopped, 
    regardless of whether they have finished their work or not. Non-daemon threads, 
    will be allowed to complete their work before the program terminates.
    '''
    price_stream_t.daemon = True

    threads.append(price_stream_t)
    price_stream_t.start()
    
    
    worker_t = WorkProcessor(work_queue)
    worker_t.daemon = True
    threads.append(worker_t)
    worker_t.start()

    
    for p in settings['pairs'].keys():
        processing_t = PriceProcessor(shared_prices, shared_prices_lock, shared_prices_events, 
                                    f"PriceProcessor_{p}", p, work_queue)
        processing_t.daemon = True
        threads.append(processing_t)
        processing_t.start()

    #cleaner way for mac and linux 
    '''
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    '''

    #works with windows above only works for mac and linux^^
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")

    print("ALL DONE")

