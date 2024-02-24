class BaseApiPrice:
    
    def __init__(self, api_ob):
        #get the insrument 
        self.instrument = api_ob['instrument']
        #we want price which is first element in list we get returned back from api
        #ask and bid is returned
        self.ask = float(api_ob['asks'][0]['price'])
        self.bid = float(api_ob['bids'][0]['price'])
