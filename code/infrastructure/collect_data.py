import pandas as pd
import datetime as dt
from dateutil import parser

from infrastructure.instrument_collection import InstrumentCollection
from api.oanda_api import OandaApi

'''
api is limited to 5000 candles max amount
if we want collect data over 7 years we will not be able to collect all in 5000 canldes
so we will give data from and date to

dfrom 2014-01-01 to 2014-01-08 put that in dataframe then go from
dfrom 2014-01-08 to 2014-01-15 and put those
and then concate all those smaller ones into 1 big dataframe
dto 2021

'''

#how many candles we will ask for each of our requests 
CANDLE_COUNT = 3000

INCREMENTS = {
    'M5' : 5 * CANDLE_COUNT,
    'H1' : 60 * CANDLE_COUNT,
    'H4' : 240 * CANDLE_COUNT
}

#send in final datafame
def save_file(final_df: pd.DataFrame, file_prefix, granularity, pair):

    #generate file name with pair name and granularity
    filename = f"{file_prefix}{pair}_{granularity}.pkl"

    #increase we have reapeated rows same candles we want to get rid of those
    #get rid of candles with dupcliate time
    final_df.drop_duplicates(subset=['time'], inplace=True)

    #sort by ascending order by time
    final_df.sort_values(by='time', inplace=True) 

    #need to reset index since we are concating multiple df all index will be same
    final_df.reset_index(drop=True, inplace=True) 

    #send in file name to pickle
    final_df.to_pickle(filename) 

    s1 = f"*** {pair} {granularity} {final_df.time.min()} {final_df.time.max()}"
    print(f"*** {s1} --> {final_df.shape[0]} candles ***")



def fetch_candles(pair, granularity, date_f: dt.datetime, 
                    date_t: dt.datetime, api: OandaApi ):
    
    #try to get data at least 3 times
    attempts = 0

    while attempts < 3:

        #try to get candles df
        candles_df = api.get_candles_df(
            pair,
            granularity=granularity,
            date_f=date_f,
            date_t=date_t
        )

        #successfully got candles df
        if candles_df is not None:
            break
        
        #not successful try again
        attempts += 1

    #not None and not empty successful candle df return the dataframe
    if candles_df is not None and candles_df.empty == False:
        return candles_df
    else:
        return None


def collect_data(pair, granularity, date_f, date_t, file_prefix, api: OandaApi ):
    
    time_step = INCREMENTS[granularity]

    #starting and ending dates for data collection
    end_date = parser.parse(date_t)
    from_date = parser.parse(date_f)

    #all dataframes we collect 
    candle_dfs = []

    to_date = from_date

    #loop thorugh all dates and collect candles 
    while to_date < end_date:
        to_date = from_date + dt.timedelta(minutes=time_step)
        if to_date > end_date:
            to_date = end_date

        candles = fetch_candles(
            pair,
            granularity, 
            from_date,
            to_date,
            api
        )

        #ensure candle is correctly collected
        if candles is not None:
            #we got back candles so append to dataframe list we have
            candle_dfs.append(candles)
            print(f"{pair} {granularity} {from_date} {to_date} --> {candles.shape[0]} candles loaded")
        else:
            print(f"{pair} {granularity} {from_date} {to_date} --> NO CANDLES")
        
        #step foward to next data
        from_date = to_date
    
    #loop has finished 
    #if we have data to save then 
    #create final dataframe and concat the other df we had candle_df we made in loop
    #then save the file
    if len(candle_dfs) > 0:
        final_df = pd.concat(candle_dfs)
        save_file(final_df, file_prefix, granularity, pair)
    else:
        #no data to save 
        print(f"{pair} {granularity} --> NO DATA SAVED!")



def run_collection(ic: InstrumentCollection, api: OandaApi):
    our_curr = ["AUD", "CAD", "JPY", "USD", "EUR", "GBP", "NZD"]
    for p1 in our_curr:
        for p2 in our_curr:
            pair = f"{p1}_{p2}"
            if pair in ic.instruments_dict.keys():
                for granularity in ["M5", "H1", "H4"]:
                    print(pair, granularity)
                    collect_data(
                        pair,
                        granularity,
                        "2017-01-07T00:00:00Z",
                        "2022-12-31T00:00:00Z",
                        "./data/",
                        api
                    )

























