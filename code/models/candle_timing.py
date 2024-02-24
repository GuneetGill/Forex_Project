import datetime as dt

#when candle manager is updating candles is get the most recent candle time and compare it with
#the last candle timing for a given granulatity and pair. 
class CandleTiming:

    #intilized with pair with most receent time with given candle granularity
    def __init__(self, last_time):
        self.last_time = last_time
        self.is_ready = False

    def __repr__(self):
        return f"last_candle:{dt.datetime.strftime(self.last_time, '%y-%m-%d %H:%M')} is_ready:{self.is_ready}"