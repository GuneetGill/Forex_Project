from api.oanda_api import OandaApi
from infrastructure.instrument_collection import instrumentCollection
from stream_example.streamer import run_streamer
from db.db import DataDB
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

#this adds objections to db
# def db_tests():
#     d=DataDB()
    #so we pass in collection which we had defiened and the object which is a dict with key value arguments
    #d.add_one(DataDB.SAMPLE_COLL, dict(age=12, name ='fred', eyes='blue' ) )
    #if collection not there it will make one for you

    #for add many we have a list which has many objects inside it 
    # data = [
    #     dict(age=12, name ='fred', eyes='blue' ),
    #     dict(age=1, name ='simon', eyes='red' ),
    #     dict(age=120, name ='heera', eyes='pink' ),
    #     dict(age=10, name ='baaj', eyes='black' )
    # ]
    # d.add_many(DataDB.SAMPLE_COLL, data)
    
    #we can add items with diff keys as well
    #d.add_one(DataDB.SAMPLE_COLL, dict(sex='F', name ='fred', lips='yellow' ) )

    #print(d.query_all(DataDB.SAMPLE_COLL))
    #print(d.query_single(DataDB.SAMPLE_COLL, age=10))
    #print(d.query_distinct(DataDB.SAMPLE_COLL, 'age'))


 

if __name__ == '__main__':
    api = OandaApi()
    #instrumentCollection.LoadInstruments("./data")

    #instrumentCollection.CreateDB(api.get_account_instruments())

    # instrumentCollection.LoadInstrumentsDB()
    # print(instrumentCollection.instruments_dict)
    #run_streamer()
    d =DataDB()
    d.test_connection()
    # db_tests()

    


    
        