
class TradeSettings:

    #take in object and name of pair
    #all the .json settings we are writing those vvv 
    def __init__(self, ob, pair):
        self.n_ma = ob['n_ma']
        self.n_std = ob['n_std']
        self.maxspread = ob['maxspread']
        self.mingain = ob['mingain']
        self.riskreward = ob['riskreward']

    def __repr__(self):
        return str(vars(self))

    #to list out all settings in string format 
    #they are indexed by keys so
    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"

        return ret_str