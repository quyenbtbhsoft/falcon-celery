from pymongo import MongoClient

client = MongoClient("mongodb+srv://guest:guest@fibonacci.clxiv.mongodb.net/fibonacci?retryWrites=true&w=majority")

db = client.test

col = db.inventory

filter_dict ={"ID":"canvs"}

if col.count_documents(filter_dict):
    print(1)
else:
    print(2)    