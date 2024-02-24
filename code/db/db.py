from pymongo import MongoClient, errors
# from pymongo.mongo_client import MongoClient, errors
# from pymongo.server_api import ServerApi
from constants.defs import MONGO_CONN_STR



class DataDB:

    SAMPLE_COLL = "forex_sample"
    CALENDAR_COLL = "forex_calendar"
    INSTRUMENTS_COLL = "forex_instruments"
    

    def __init__(self):
        #set up connection
        self.client = MongoClient(MONGO_CONN_STR)
        #which database we want to access
        self.db = self.client.forex_learning


    def test_connection(self):
        print(self.db.list_collection_names())

    #take in collection and key word argurment since we can delete based on key and value's
    def delete_many(self, collection, **kwargs):
        try:
            _ = self.db[collection].delete_many(kwargs)
        except errors.InvalidOperation as error:
            print("delete_many error:", error)

    #enter in name of collection since we have diff collections
    #ob is what we are inserting
    def add_one(self, collection, ob):
        try:
            #insert the object (1 record)
            #_= tells us if we need to we could do something with return result
            _ = self.db[collection].insert_one(ob)
        #catch error
        except errors.InvalidOperation as error:
            print("add_one error:", error)

    #insert more than 1 so list of objects
    def add_many(self, collection, list_ob):
        try:
            #_= tells us if we need to we could do something with return result
            _ = self.db[collection].insert_many(list_ob)
        #catch error
        except errors.InvalidOperation as error:
            print("add_many error:", error)

    #distince values for a key so just all name values or just all age values
    def query_distinct(self, collection, key):
        try:            
            return self.db[collection].distinct(key)
        except errors.InvalidOperation as error:
            print("query_distinct error:", error) 
    

    #find a single one with a specfic key value requierment
    def query_single(self, collection, **kwargs):
        try:     
            #just give us back 1       
            r = self.db[collection].find_one(kwargs, {'_id':0})
            return r
        
        except errors.InvalidOperation as error:
            print("query_single error:", error)


    #send in object keys and values and then ask it to find it 
    def query_all(self, collection, **kwargs):
        try:
            data = []
            #try and find data
            #id_0 tells us to ignore the id key and not give that back to us
            r = self.db[collection].find(kwargs, {'_id':0})
            for item in r:
                data.append(item)
            return data
        #catch error
        except errors.InvalidOperation as error:
            print("query_all error:", error)

































