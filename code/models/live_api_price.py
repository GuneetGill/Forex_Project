
from dateutil import parser
from models.base_api_price import BaseApiPrice

#also inherts from basepaiprice 
class LiveApiPrice(BaseApiPrice):
    
    #create insutrment ask and bid from api that came in using parent class
    def __init__(self, api_ob):
        super().__init__(api_ob)
        self.time = parser.parse(api_ob['time'])

    
    def __repr__(self):
        return f"LiveApiPrice() {self.instrument} {self.ask} {self.bid} {self.time}"

    def get_dict(self):
        return dict(
            instrument=self.instrument,
            time = self.time,
            ask=self.ask,
            bid=self.bid
        )