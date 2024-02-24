import pandas as pd
from models.trade_decision import TradeDecision
from technicals.indicators import BollingerBands

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

from api.oanda_api import OandaApi
from models.trade_settings import TradeSettings
import constants.defs as defs

ADDROWS = 20

#used to get signal from dataframe we take in row and trade settings
def apply_signal(row, trade_settings: TradeSettings):

    #check if spread is within trade settings
    if row.SPREAD <= trade_settings.maxspread and row.GAIN >= trade_settings.mingain:
        #are we doing a buy or sell or nothing?
        if row.mid_c > row.BB_UP and row.mid_o < row.BB_UP:
            return defs.SELL
        elif row.mid_c < row.BB_LW and row.mid_o > row.BB_LW:
            return defs.BUY
    return defs.NONE


def apply_SL(row, trade_settings: TradeSettings):
    if row.SIGNAL == defs.BUY:
        return row.mid_c - (row.GAIN / trade_settings.riskreward)
    elif row.SIGNAL == defs.SELL:
        return row.mid_c + (row.GAIN / trade_settings.riskreward)
    return 0.0

def apply_TP(row):
    
    if row.SIGNAL == defs.BUY:
        return row.mid_c + row.GAIN
    elif row.SIGNAL == defs.SELL:
        return row.mid_c - row.GAIN
    return 0.0

#take in dataframe with pair trade settings and to log message
def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message):
    #reset index to make sure index is reset to 0 just incase
    df.reset_index(drop=True, inplace=True)
    df['PAIR'] = pair
    df['SPREAD'] = df.ask_c - df.bid_c

    #make indicator 
    #apply Boillinger Bands which gives us 3 cols back
    df = BollingerBands(df, trade_settings.n_ma, trade_settings.n_std)
    #add cols for the indicator we are doing 
    df['GAIN'] = abs(df.mid_c - df.BB_MA)
    #use func we created above to apply the signal
    df['SIGNAL'] = df.apply(apply_signal, axis=1, trade_settings=trade_settings)
    df['TP'] = df.apply(apply_TP, axis=1)
    df['SL'] = df.apply(apply_SL, axis=1, trade_settings=trade_settings)
    df['LOSS'] = abs(df.mid_c - df.SL)

    #cols we want to log 
    log_cols = ['PAIR', 'time', 'mid_c', 'mid_o', 'SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']
    log_message(f"process_candles:\n{df[log_cols].tail()}", pair)

    #return last row 
    return df[log_cols].iloc[-1]

#how many rows we are getting, candle time to make sure we have correct candle set, api and log messages
def fetch_candles(pair, row_count, candle_time, granularity,
                    api: OandaApi, log_message):

    #get a dataframe with specfications 
    df = api.get_candles_df(pair, count=row_count, granularity=granularity)

    #check if we got something back 
    if df is None or df.shape[0] == 0: #got nothing from api, empty dataframe
        log_message("tech_manager fetch_candles failed to get candles", pair)
        return None
    
    #-1 is to get the final row if the time isnt equal to candle time we have problem
    if df.iloc[-1].time != candle_time:
        log_message(f"tech_manager fetch_candles {df.iloc[-1].time} not correct", pair)
        return None

    #everything worked out return dataframe
    return df

#should we make the trade or not? yes or no
def get_trade_decision(candle_time, pair, granularity, api: OandaApi, 
                            trade_settings: TradeSettings, log_message):

    #trade settings and number of moving average and add 20 to make sure we have enough candles
    max_rows = trade_settings.n_ma + ADDROWS

    #update our log messages 
    log_message(f"tech_manager: max_rows:{max_rows} candle_time:{candle_time} granularity:{granularity}", pair)

    #get candles dataframe
    df = fetch_candles(pair, max_rows, candle_time,  granularity, api, log_message)

    #we got back something 
    if df is not None:
        last_row = process_candles(df, pair, trade_settings, log_message)
        #will be returned to Bot either None or returned row
        return TradeDecision(last_row)

    return None


