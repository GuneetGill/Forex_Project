
from api.oanda_api import OandaApi
from bot.trade_risk_calculator import get_trade_units
from models.trade_decision import TradeDecision

#send in pair and API instance
def trade_is_open(pair, api: OandaApi):

    #get list of open trades
    open_trades = api.get_open_trades()

    #if the instrument is same as pair thatn it is open
    for ot in open_trades:
        if ot.instrument == pair:
            return ot

    return None

#called from the bot once a trade should be placed
def place_trade(trade_decision: TradeDecision, api: OandaApi, log_message, log_error, trade_risk):

    ot = trade_is_open(trade_decision.pair, api)

    #if trade is already open send error message and send to log error
    if ot is not None:
        log_message(f"Failed to place trade {trade_decision}, already open: {ot}", trade_decision.pair)
        return None

    trade_units = get_trade_units(api, trade_decision.pair, trade_decision.signal, 
                            trade_decision.loss, trade_risk, log_message)

    #get the trade info 
    trade_id = api.place_trade(
        trade_decision.pair, 
        trade_units,
        trade_decision.signal,
        trade_decision.sl,
        trade_decision.tp
    )

    #if no trade id is given back then log an error
    if trade_id is None:
        log_error(f"ERROR placing {trade_decision}")
        log_message(f"ERROR placing {trade_decision}", trade_decision.pair)
    #trade was successfully placed
    else:
        log_message(f"placed trade_id:{trade_id} for {trade_decision}", trade_decision.pair)


