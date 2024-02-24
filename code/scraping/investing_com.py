from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime as dt
import time
import constants.defs as defs
import cloudscraper

#info from the string we got with bunch of info and these are the varibles we want to look into
data_keys = [
    'pair_name',
    'ti_buy', 
    'ti_sell', 
    'ma_buy', 
    'ma_sell', 
    'S1', 
    'S2', 
    'S3', 
    'pivot', 
    'R1', 
    'R2', 
    'R3', 
    'percent_bullish', 
    'percent_bearish'
]

#takes in text list we created
def get_data_object(text_list, pair_id, time_frame):
    data = {}
    data['pair_id'] = pair_id
    data['time_frame'] = time_frame
    data['updated'] = dt.datetime.utcnow()

    for item in text_list:

        temp_item = item.split("=")
        if len(temp_item) == 2 and temp_item[0] in data_keys:
            data[temp_item[0]] = temp_item[1]

    #change format in pairs from USD/CAD to USD_CAD
    if 'pair_name' in data:
        data['pair_name'] = data['pair_name'].replace("/", "_")


    return data


def investing_com_fetch(pair_id, time_frame):

    scraper = cloudscraper.create_scraper() 

    #use this to try to get past the website which is blocking us 
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
    }

    params = dict(
        action='get_studies',
        pair_ID=pair_id,
        time_frame=time_frame
    )

    # -- try this to extract infro from website-- #
    resp = scraper.get("https://www.investing.com/common/technical_studies/technical_studies_data.php",
                           params=params, headers=headers)
    text = resp.content.decode("utf-8")
   # ---
    
    
    # -- when it doesn't work, use the mockup file-- #
    #open the mockfile and read in information
    # with open("./scraping/mock_files/investing_com.html", "r", encoding="utf-8") as f:
    #     text = f.read()
    # # ---

    #where we want to start with extraction and end with 2nd set of text
    #when we looked at the website the info we needed was in between this line of text vv
    index_start = text.index("pair_name=")
    index_end = text.index("*;*quote_link")

    #this holds the data we want
    data_str = text[index_start:index_end]

    #send in split data string 
    return get_data_object(data_str.split('*;*'), pair_id, time_frame)


def investing_com():
    data = [investing_com_fetch(12, 3600)]
    data = []
    for pair_id in range(1, 12):
        #hourly and daily numbers
        for time_frame in [3600, 86400]:
            print(pair_id, time_frame)
            data.append(investing_com_fetch(pair_id, time_frame))
            time.sleep(0.5) #dont want to spam server 
           # break
       # break
    
    #return dataframe we looped through
    return pd.DataFrame.from_dict(data)

#checks if name and time frame is valid
def get_pair(pair_name, tf):

    #TFS in file defs has all time frames written in there
    if tf not in defs.TFS:
        #set by default 1 hour if someone makes request with wrong time then default
        tf = defs.TFS['H1']
    else:
        tf = defs.TFS[tf]

    #pairname has to be valid which is written in my defs file
    if pair_name in defs.INVESTING_COM_PAIRS:
        pair_id = defs.INVESTING_COM_PAIRS[pair_name]['pair_id']
        return investing_com_fetch(pair_id, tf)
        #give us back the pair name and time frame 