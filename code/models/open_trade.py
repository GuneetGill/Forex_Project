from dateutil import parser


class OpenTrade:

    #the api object we get back from open trade
    #this is the info we get back from the json object we select few attrubites we need
    def __init__(self, api_ob):
        #some come back as strings so we change it into float
        self.id = api_ob['id']
        self.instrument = api_ob['instrument']
        self.price = float(api_ob['price'])
        self.currentUnits = float(api_ob['currentUnits'])
        self.unrealizedPL = float(api_ob['unrealizedPL'])
        self.marginUsed = float(api_ob['marginUsed'])

    #we get a string back after
    def __repr__(self):
        return str(vars(self))