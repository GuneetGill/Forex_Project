from flask import Flask, jsonify
from flask_cors import CORS 
#most common error is cross orgin error, local host 5000 that is where out server will run
#when it makes a requst from api so it wont be same place unless we put a header allowing that
#request so no cross orgin issue flask is good for running on local machine

from api.oanda_api import OandaApi
from api.web_options import get_options
import http

from scraping.bloomberg_com import bloomberg_com
from scraping.investing_com import get_pair

#create new flash object name is equal to main
app = Flask(__name__)
#wrap it in cors so no cross orgin errors
CORS(app)

def get_response(data):
    if data is None:
        #send in response code from front end 
        return jsonify(dict(message='error getting data')), http.HTTPStatus.NOT_FOUND
    else:
        return jsonify(data)

#use a decorator then add a route, when our server is listenting when it makes a request then function we 
#define now will be run
@app.route("/api/test")
def test():
    return jsonify(dict(message='hello'))


#this one has issues since u arent able to scrape it 
@app.route("/api/headlines")
def headlines():
    return get_response(bloomberg_com())
    #return jsonify(bloomberg_com())


@app.route("/api/account")
def account():
    return get_response(OandaApi().get_account_summary())
    #return jsonify(OandaApi().get_account_summary())


@app.route("/api/options")
def options():
    return get_response(get_options())

#send in timeframe and name add parameters to get info about each pair with timeframe
@app.route("/api/technicals/<pair>/<tf>")
def technicals(pair, tf):
    data = get_pair(pair, tf)
    return get_response(data)
    # return get_response(get_pair(pair,tf))
    # if data is None:
    #     return jsonify(dict(message = 'error getting data'))
    # else:
    #     return jsonify(data)


@app.route("/api/prices/<pair>/<granularity>/<count>")
def prices(pair, granularity, count):
    return get_response(OandaApi().web_api_candles(pair, granularity, count))
    # data = OandaApi().web_api_candles(pair, granularity, count)
    # return get_response(OandaApi().web_api_candles(pair, granularity, count))
    # if data is None:
    #     return jsonify(dict(message = 'error getting data'))
    # else:
    #     return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)

    #host="0.0.0.0", port=8000,

