from scraping.investing_com import investing_com
from scraping.dailyfx_com import dailyfx_com
from scraping.bloomberg_com import bloomberg_com
from scraping.fx_calendar import fx_calendar

if __name__ == "__main__":
   #print(investing_com()) #works 

   #print(dailyfx_com()) #works great returns dataframe

    hl = bloomberg_com()   #works returns news headlines
    [print(x) for x in hl]

   # print(fx_calendar())  #-----works i think

  