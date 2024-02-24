#class used to repersent different pairs such as EUR_CAD etc
class Instrument:

    #constructor initializes different attrubite of instrument
    def __init__(self, name, ins_type, displayName,
                    pipLocation, tradeUnitsPrecision, marginRate,
                    displayPrecision):
        self.name = name 
        self.ins_type = ins_type
        self.displayName = displayName
        self.pipLocation = pow(10, pipLocation) #change from negative value
        self.tradeUnitsPrecision = tradeUnitsPrecision
        self.marginRate = float(marginRate)
        self.displayPrecision = displayPrecision 

    #provides string repersentation of instrument instance.
    #gives us a string containing a dictionary repersentation of the instance's attrubites
    def __repr__(self):
        return str(vars(self))

    #used as alternative constructor 
    #takes dictionary object as argurment which is instance of instrument object
    #returns newly created instrument instance
    @classmethod
    def FromApiObject(cls, ob):
        return Instrument(
            ob['name'],
            ob['type'],
            ob['displayName'],
            ob['pipLocation'],
            ob['tradeUnitsPrecision'],
            ob['marginRate'],
            ob["displayPrecision"]
        )