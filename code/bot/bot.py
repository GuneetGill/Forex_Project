import json
import time
from bot.candle_manager import CandleManager
from bot.technicals_manager import get_trade_decision
from bot.trade_manager import place_trade

from infrastructure.log_wrapper import LogWrapper
from models.trade_settings import TradeSettings
from api.oanda_api import OandaApi
import constants.defs as defs

class Bot:

    #set up logging to know what is going on when bot is running
    #we cannot print it on screen too much so we set up log
    ERROR_LOG = "error" 
    MAIN_LOG = "main" 
    GRANULARITY = "M1" #temp create varible for this file u can cahnge letter
    SLEEP = 10

    def __init__(self):
        #what are the settings we have the bot set to 
        self.load_settings()
        self.setup_logs()


        self.api = OandaApi()
        self.candle_manager = CandleManager(self.api, self.trade_settings, self.log_message, Bot.GRANULARITY)

        # self.log_to_main("Bot started")
        # self.log_to_error("Bot started")

    def load_settings(self):
        #reading json file 
        with open("./bot/settings.json", "r") as f:
            data = json.loads(f.read())
            self.trade_settings = { k: TradeSettings(v, k) for k, v in data['pairs'].items() }
            self.trade_risk = data['trade_risk']

    def setup_logs(self):
        self.logs = {} #new object

        for k in self.trade_settings.keys():
            self.logs[k] = LogWrapper(k) #new wrapper with name like EUR_CAD
            self.log_message(f"{self.trade_settings[k]}", k) #log settings key is pair name

        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG)
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)

        self.log_to_main(f"Bot started with {TradeSettings.settings_to_str(self.trade_settings)}")

    #message we want to log 
    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    #when we want to log to main and key is Bot.MainLog
    def log_to_main(self, msg):
        self.log_message(msg, Bot.MAIN_LOG)

    #when we want to log to error and key is Bot.MainLog
    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)

    def process_candles(self, triggered):
        #array has something in it
        if len(triggered) > 0:
            #log a message 
            self.log_message(f"process_candles triggered:{triggered}", Bot.MAIN_LOG)
            #loop thorugh candles list
            for p in triggered:
                #decide if we want to make trade or not using most recent candle time 
                last_time = self.candle_manager.timings[p].last_time
                trade_decision = get_trade_decision(last_time, p, Bot.GRANULARITY, self.api, 
                                                       self.trade_settings[p],  self.log_message)
                
                #we want to make a trade if not None
                if trade_decision is not None and trade_decision.signal != defs.NONE:
                    #log that we have a trade
                    self.log_message(f"Place Trade: {trade_decision}", p)
                    self.log_to_main(f"Place Trade: {trade_decision}")
                    #place the trade
                    place_trade(trade_decision, self.api, self.log_message, self.log_to_error, self.trade_risk)


    def run(self):
        #infinite look
        while True:
            time.sleep(Bot.SLEEP) #make it sleep for a bit
            #use candle manager to update timings this will return a list of all updated pairs
            #process candles will deal with processed candles 

            #log to error if something goes wrong 
            try:
                self.process_candles(self.candle_manager.update_timings())
            except Exception as error:
                self.log_to_error(f"CRASH: {error}")
                break
    

