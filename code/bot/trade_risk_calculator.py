from api.oanda_api import OandaApi
import constants.defs as defs
from infrastructure.instrument_collection import instrumentCollection as ic


def get_trade_units(api: OandaApi, pair, signal, loss, trade_risk, log_message):

    #this will get us back the api price 
    prices = api.get_prices([pair])

    #check if we got something back from ^^^
    if prices is None or len(prices) == 0:
        log_message("get_trade_units() Prices is none", pair)
        return False

    #to make sure we acutally get something price
    #try to find something in list that api gave to us
    price = None
    for p in prices:
        #if we found something than the price is equal to p we sohuld have gotten back from api
        if p.instrument == pair:
            price = p
            break

    #another check this should reallt never happen since its double check
    if price == None:
        log_message("get_trade_units() price is None????", pair)
        return False
    
    log_message(f"get_trade_units() price {price}", pair)

    conv = price.buy_conv
    if signal == defs.SELL:
        conv = price.sell_conv

    pipLocation = ic.instruments_dict[pair].pipLocation
    #number of pips we will be losing
    num_pips = loss / pipLocation
    #amount perpared to loose per pip
    per_pip_loss = trade_risk / num_pips
    #units needed to be placed for given risk
    units = per_pip_loss / (conv * pipLocation)

    log_message(f"{pipLocation} {num_pips} {per_pip_loss} {units:.1f}", pair)

    return units


    

