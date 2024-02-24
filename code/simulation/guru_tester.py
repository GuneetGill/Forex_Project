import pandas as pd
import datetime as dt

BUY = 1
SELL = -1
NONE = 0

#have to adjust take profit and stop off if stragety is different than these two

def apply_take_profit(row, PROFIT_FACTOR):
    if row.SIGNAL != NONE:
        if row.SIGNAL == BUY:
            #depedning on direction of candle we apply take profit
            #incase of red candle where we want to buy we dont want negative values
            if row.direction == BUY:
                return (row.ask_c - row.ask_o) * PROFIT_FACTOR + row.ask_c
            else:
                return (row.ask_o - row.ask_c) * PROFIT_FACTOR + row.ask_o
        else:
            if row.direction == SELL:
                return (row.bid_c - row.bid_o) * PROFIT_FACTOR + row.ask_c
            else:
                return (row.bid_o - row.bid_c) * PROFIT_FACTOR + row.ask_o
    else:
        return 0.0

def apply_stop_loss(row):
    if row.SIGNAL != NONE:
        if row.SIGNAL == BUY:
            if row.direction == BUY:
                return row.ask_o
            else:
                return row.ask_c
        else:
            if row.direction == SELL:
                return row.bid_o
            else:
                return row.bid_c
    else:
        return 0.0

#choose sim without spread
def remove_spread(df):
    for a in ["ask", "bid"]:
        for b in ["o", "h", "l", "c"]:
            #set them to same as mid prices all prices are mid prices 
            c = f"{a}_{b}"
            df[c] = df[f"mid_{b}"]

#sig is a function
def apply_signals(df, PROFIT_FACTOR, sig):
    df["SIGNAL"] = df.apply(sig, axis=1)
    df["TP"] = df.apply(apply_take_profit, axis=1, PROFIT_FACTOR=PROFIT_FACTOR)
    df["SL"] = df.apply(apply_stop_loss, axis=1)

#fixed to 1 hour u can change it to 4 for 4 hours for ex
def create_signals(df, time_d=1):
    df_signals = df[df.SIGNAL != NONE].copy() 
    df_signals['m5_start'] = [x + dt.timedelta(hours=time_d) for x in df_signals.time]
    #drop cols
    df_signals.drop(['time', 'mid_o', 'mid_h', 'mid_l', 'bid_o', 'bid_h', 'bid_l',
    'ask_o', 'ask_h', 'ask_l', 'direction'], axis=1, inplace=True)
    #rename cols 
    df_signals.rename(columns={
        'bid_c' : 'start_price_BUY',
        'ask_c' : 'start_price_SELL',
        'm5_start' : 'time'
    }, inplace=True)
    return df_signals



class Trade:
    #take in row from dataframe
    def __init__(self, row, profit_factor, loss_factor):
        self.running = True #when we start trades its true
        self.start_index_m5 = row.name  
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor
        
        if row.SIGNAL == BUY:
            self.start_price = row.start_price_BUY
            self.trigger_price = row.start_price_BUY
            
        if row.SIGNAL == SELL:
            self.start_price = row.start_price_SELL
            self.trigger_price = row.start_price_SELL
            
        self.SIGNAL = row.SIGNAL
        self.TP = row.TP
        self.SL = row.SL
        self.result = 0.0
        self.end_time = row.time
        self.start_time = row.time
        
    def close_trade(self, row, result, trigger_price):
        self.running = False
        self.result = result
        self.end_time = row.time
        self.trigger_price = trigger_price
        
    def update(self, row):
        if self.SIGNAL == BUY:
            if row.bid_h >= self.TP:
                self.close_trade(row, self.profit_factor, row.bid_h)
            elif row.bid_l <= self.SL:
                self.close_trade(row, self.loss_factor, row.bid_l)
        if self.SIGNAL == SELL:
            if row.ask_l <= self.TP:
                self.close_trade(row, self.profit_factor, row.ask_l)
            elif row.ask_h >= self.SL:
                self.close_trade(row, self.loss_factor, row.ask_h)   

#use for tests 
class GuruTester:
    #create dataframe send in ref to apply_signal, send in 5min candle df, choose to add spread,
    #set our loss and profit factors and set time delta so 1 hour candles by defualt or 4 hour
    def __init__(self, df_big,
                    apply_signal, 
                    df_m5,
                    use_spread=True,
                    LOSS_FACTOR = -1.0,
                    PROFIT_FACTOR = 1.5,
                    time_d=1 ):
        self.df_big = df_big.copy()
        self.use_spread = use_spread
        self.apply_signal = apply_signal
        self.df_m5 = df_m5.copy()
        self.LOSS_FACTOR = LOSS_FACTOR
        self.PROFIT_FACTOR = PROFIT_FACTOR
        self.time_d = time_d

        self.prepare_data()
    
    def prepare_data(self):
        
        #print("prepare_data...")

        #do we want to use spread? if we dont then set all the ask and bid prices same as mid 
        #on 1hour and 5min df
        if self.use_spread == False:
            remove_spread( self.df_big)
            remove_spread( self.df_m5)

        #send in signals 
        apply_signals(self.df_big,
                    self.PROFIT_FACTOR,
                    self.apply_signal)

        #get slim version 
        df_m5_slim = self.df_m5[['time','bid_h', 'bid_l', 'ask_h', 'ask_l' ]].copy()
        #get our signals
        df_signals = create_signals(self.df_big, time_d=self.time_d)

        #perform merge
        self.merged = pd.merge(left=df_m5_slim, right=df_signals, on='time', how='left')
        #fill nas to 0's
        self.merged.fillna(0, inplace=True)
        #merge those 0's to ints from floats
        self.merged.SIGNAL = self.merged.SIGNAL.astype(int)

    #run simulation
    def run_test(self):
        #print("run_test...")

        open_trades_m5 = []
        closed_trades_m5 = []

        #loop through create trade and create df results 
        for index, row in self.merged.iterrows():
            
            if row.SIGNAL != NONE:
                open_trades_m5.append(Trade(row, self.PROFIT_FACTOR, self.LOSS_FACTOR))  
                
            for ot in open_trades_m5:
                ot.update(row)
                if ot.running == False:
                    closed_trades_m5.append(ot)
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]

        self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
        #print("Result:", self.df_results.result.sum())
