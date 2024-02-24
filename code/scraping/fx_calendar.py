from bs4 import BeautifulSoup
import pandas as pd
import requests
from dateutil import parser
import time
import datetime as dt
import random
from db.db import DataDB

pd.set_option("display.max_rows", None)

#send in child element
def get_date(c):
    #table row
    tr = c.select_one("tr")
    #table headers 
    ths = (tr.select("th"))
    for th in ths:
        #find colpsan atrtubite since the text is the date
        #function that helps us find if it has specfic attrubite .has_attr
        if th.has_attr("colspan"):
            #strip off white space we get back
            date_text = th.get_text().strip()  
            #parse the date text back 
            return parser.parse(date_text)
    return None

def get_data_point(key, element):
    #either one of these will help us get the forecast and actual and previous
    for e in ['span', 'a']:
        d = element.select_one(f"{e}#{key}")
        if d is not None:
            return d.get_text()
    return '' 

#function to test if key is availble if not return empty 
def get_data_for_key(tr,key):
    if tr.has_attr(key):
        return tr.attrs[key]
    return ''


#loop throguh data under headers and create dataframe 
def get_data_dict(item_date, table_rows):
    #send back last of data
    data = []

    for tr in table_rows:
        data.append(dict(
            date=item_date,
            country=get_data_for_key(tr, 'data-country'),  
            category=get_data_for_key(tr, 'data-category'), 
            event=get_data_for_key(tr, 'data-event'),  
            symbol=get_data_for_key(tr, 'data-symbol'), 
            actual = get_data_point('actual', tr),
            previous = get_data_point('previous', tr),
            forecast = get_data_point('forecast', tr)
        ))
    return data


def get_fx_calendar(from_date):

    session = requests.Session()
    
    #from date
    f_d_str = dt.datetime.strftime(from_date, "%Y-%m-%d 00:00:00")

    #to date
    to_date = from_date + dt.timedelta(days=6)
    to_d_str = dt.datetime.strftime(to_date, "%Y-%m-%d 00:00:00")

    headers = {
        
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Cookie":"calendar-importance=3; cal-custom-range={fr_d_str}|{to_d_str}; TEServer=TEIIS3; cal-timezone-offset=0;"
    }
    
    #unable to scrap from web
    resp = requests.get("https://tradingeconomics.com/calendar", headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')

    #using mock files
    # with open ("./scraping/mock_files/fx_calendar.html", "r", encoding = "utf-8") as f:
    #     resp = f.read()
    #     soup = BeautifulSoup(resp, 'html.parser')

    #select table 
    table = soup.select_one("table#calendar")

    #date was found on most recent header
    last_header_date = None

    #object indexed by date
    trs={}
    #list of objects to make info dataframe
    final_data=[]


    '''
    We will iterate through rows and once we found a header for a date we will assume 
    all things under are for that date and then move onto next set of rows
    These are all under the class "table-header"  
    Their is another second header with class "hidden-header" we will be ignoring
    '''
    #loop through all elements of table under header
    for c in table.children:
        #hit new table head
        if c.name == 'thead':
            #if we found a hidden class ignore it
            if 'class' in c.attrs and 'hidden-head' in c.attrs['class']:
                continue
            
            last_header_date = get_date(c)
            #empty list to start with 
            trs[last_header_date] = []
        #if the table row is availble append to empty list we just craeted
        elif c.name == "tr" :
            trs[last_header_date].append(c)


    for item_date, table_rows in trs.items():
        final_data += get_data_dict(item_date, table_rows)

    
    #[print(x) for x in final_data]
    return final_data


def fx_calendar():
    #final_data = []

    #the terminal gives me correct date output but mongo gives current dates

    start = parser.parse("2021-05-03T00:00:00Z")
    end = parser.parse("2022-03-25T00:00:00Z")

    #insert into database
    database = DataDB()

    while start < end:
        # print(start)
        #final_data += get_fx_calendar(start)
        data = get_fx_calendar(start)
        #print(data)
        print(start, len(data))
        database.add_many(DataDB.CALENDAR_COLL, data)
        start = start + dt.timedelta(days=7)
        time.sleep(random.randint(1,4)) #not to overuse api
    
    #print(pd.DataFrame.from_dict(final_data))

