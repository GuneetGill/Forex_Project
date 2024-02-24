import requests
import pandas as pd
import json
import constants.defs as defs
from dateutil import parser
from datetime import datetime as dt
from infrastructure.instrument_collection import instrumentCollection as ic
from models.api_price import ApiPrice
from models.open_trade import OpenTrade

#OandaApi class which is designed to interact with the OANDA API
class OandaApi:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(defs.SECURE_HEADER)

    #method is responsible for making HTTP requests to the OANDA API
    #trys to make get request
    def make_request(self, url, verb='get', code=200, params=None, data=None, headers=None):
        full_url = f"{defs.OANDA_URL}/{url}"

        if data is not None:
            data = json.dumps(data)

        try:
            response = None
            if verb == "get":
                response = self.session.get(full_url, params=params, data=data, headers=headers)
            if verb == "post":
                response = self.session.post(full_url, params=params, data=data, headers=headers)
            if verb == "put":
                response = self.session.put(full_url, params=params, data=data, headers=headers)
            if response == None:
                return False, {'error': 'verb not found'}

            if response.status_code == code:
                return True, response.json()
            else:
                return False, response.json()
            
        except Exception as error:
            return False, {'Exception': error}

    #general-purpose function for making requests to specific endpoints
    #within the OANDA API associated with a particular account
    def get_account_ep(self, ep, data_key):
        url = f"accounts/{defs.ACCOUNT_ID}/{ep}"
        ok, data = self.make_request(url)

        if ok == True and data_key in data:
            return data[data_key]
        else:
            print("ERROR get_account_ep()", data)
            return None

    #requests the summary information for the account associated with the OANDA API key
    def get_account_summary(self):
        return self.get_account_ep("summary", "account")

    #designed to retrieve information about the instruments available for trading in the account
    def get_account_instruments(self):
        return self.get_account_ep("instruments", "instruments")


    #retrieves historical candlestick data for a specified trading pair from the OANDA API
    #allowing customization of the number of candlesticks, granularity, price component, 
    #and optionally, a date range
    def fetch_candles(self, pair_name, count=10, granularity="H1",
                            price="MBA", date_f=None, date_t=None):
        
        url = f"instruments/{pair_name}/candles"

        params = dict(
            granularity = granularity,
            price = price
        )

        if date_f is not None and date_t is not None:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params["from"] = dt.strftime(date_f, date_format)
            params["to"] = dt.strftime(date_t, date_format)
        else:
            params["count"] = count

        ok, data = self.make_request(url, params=params)
    
        if ok == True and 'candles' in data:
            return data['candles']
        else:
            print("ERROR fetch_candles()", params, data)
            return None


    #Takes a trading pair name and additional keyword arguments
    #retrieves historical candlestick data using the fetch_candles method
    #processes the data, and returns a pandas DataFrame
    def get_candles_df(self, pair_name, **kwargs):

        data = self.fetch_candles(pair_name, **kwargs)

        if data is None:
            return None
        if len(data) == 0:
            return pd.DataFrame()
        
        prices = ['mid', 'bid', 'ask']
        ohlc = ['o', 'h', 'l', 'c']
        
        final_data = []
        for candle in data:
            if candle['complete'] == False:
                continue
            new_dict = {}
            new_dict['time'] = parser.parse(candle['time'])
            new_dict['volume'] = candle['volume']
            for p in prices:
                if p in candle:
                    for o in ohlc:
                        new_dict[f"{p}_{o}"] = float(candle[p][o])
            final_data.append(new_dict)
        df = pd.DataFrame.from_dict(final_data)
        return df

    #fetch last complete candle for given granularity and pair name 
    def last_complete_candle(self, pair_name, granularity):
            df = self.get_candles_df(pair_name, granularity=granularity, count=10)
            if df.shape[0] == 0:
                return None
            return df.iloc[-1].time #we want last row
    
        
    def web_api_candles(self, pair_name, granularity, count):
        df = self.get_candles_df(pair_name, granularity=granularity, count=count)
        if df.shape[0] == 0:
            return None

        cols = ['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c']
        df = df[cols].copy()

        #make string from datetime 
        df['time'] = df.time.dt.strftime("%y-%m-%d %H:%M")

        #we want a col with all the items written in a list
        #so we can do this by orient=list
        return df.to_dict(orient='list')


    #to place a trade or place a stop loss or take profit trade
    def place_trade(self, pair_name: str, units: float, direction: int,
                        stop_loss: float=None, take_profit: float=None):

        #build url for api request 
        url = f"accounts/{defs.ACCOUNT_ID}/orders"

        #make sure correct # of decimal places, round decimal places 
        instrument = ic.instruments_dict[pair_name]
        units = round(units, instrument.tradeUnitsPrecision)

        #remove any negative values
        if direction == defs.SELL:
            units = units * -1        

        #what we need to place trade
        data = dict(
            order=dict(
                units=str(units),
                instrument=pair_name,
                type="MARKET"
            )
        )

        if stop_loss is not None:
            sld = dict(price=str(round(stop_loss, instrument.displayPrecision)))
            data['order']['stopLossOnFill'] = sld

        if take_profit is not None:
            tpd = dict(price=str(round(take_profit, instrument.displayPrecision)))
            data['order']['takeProfitOnFill'] = tpd

        #print(data)
        
        #make the request using post 
        ok, response = self.make_request(url, verb="post", data=data, code=201)

        #print(ok, response)

        #check if this was returned in api request
        #this tells us the order actaully went through
        #then return trade_id 
        if ok == True and 'orderFillTransaction' in response:
            return response['orderFillTransaction']['id']
        else:
            return None
            
    #use this to close a trade 
    def close_trade(self, trade_id):
        url = f"accounts/{defs.ACCOUNT_ID}/trades/{trade_id}/close"
        #not intrested in response so we put _
        ok, _ = self.make_request(url, verb="put", code=200)

        if ok == True:
            print(f"Closed {trade_id} successfully")
        else:
            print(f"Failed to close {trade_id}")

        return ok

    def get_open_trade(self, trade_id):
        url = f"accounts/{defs.ACCOUNT_ID}/trades/{trade_id}"
        ok, response = self.make_request(url)

        if ok == True and 'trade' in response:
            #return list of trades
            return OpenTrade(response['trade'])

    def get_open_trades(self):
        url = f"accounts/{defs.ACCOUNT_ID}/openTrades"
        ok, response = self.make_request(url)

        #check we got correct object back 
        #return list of open trades
        if ok == True and 'trades' in response:
            return [OpenTrade(x) for x in response['trades']]

    #get the prices for the pair
    def get_prices(self, instruments_list):
        url = f"accounts/{defs.ACCOUNT_ID}/pricing"

        params = dict(
            #make into comma seperated list
            instruments=','.join(instruments_list),
            includeHomeConversions=True
        )

        ok, response = self.make_request(url, params=params)

        #if we got prices back then we got correct response back from API
        if ok == True and 'prices' in response and 'homeConversions' in response:
            return [ApiPrice(x, response['homeConversions']) for x in response['prices']]

        return None            