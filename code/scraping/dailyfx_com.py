from bs4 import BeautifulSoup
import pandas as pd
import requests

def dailyfx_com():

    # -- try this -- #
    
    #resp = requests.get("https://www.dailyfx.com/sentiment")

    #uses html parser to pick out each element in html webpage
    #soup = BeautifulSoup(resp.content, 'html.parser')
    # ---
    
    # -- when it doesn't work, use the mockup -- #
    with open("./scraping/mock_files/daily-fx.html", "r", encoding="utf-8") as f:
        resp = f.read()
        soup = BeautifulSoup(resp, 'html.parser')
    # ---

    #this was a single row in the website
    rows = soup.select(".dfx-technicalSentimentCard")

    pair_data = []

    #extract all the data out of the table on the website and make into dataframe
    for r in rows:
        #values in the colms VVV
        card = r.select_one(".dfx-technicalSentimentCard__pairAndSignal")
        change_values = r.select(".dfx-technicalSentimentCard__changeValue")
        #add data to dict
        pair_data.append(dict(
            #pair and sentiment added on vvv like EUR_CAD and bullish and strip off newline char
            pair=card.select_one("a").get_text().replace("/", "_").strip("\n"),
            sentiment=card.select_one("span").get_text().strip("\n"),
            #daily changes in shorts and longs 
            longs_d=change_values[0].get_text(),
            shorts_d=change_values[1].get_text(),
            #weekly changes in shorts and longs 
            longs_w=change_values[3].get_text(),
            shorts_w=change_values[4].get_text()
        ))

    #return back the dataframe
    return pd.DataFrame.from_dict(pair_data)

    