from fastapi import FastAPI
from pymongo import MongoClient
import pymongo, json

client = MongoClient('35.193.230.58',
    username='felix', password='12345678', 
    authSource='obd',authMechanism='SCRAM-SHA-1')

db = client['obd']
collection_name = 'data'
records = db[collection_name]
count_doc_start = records.count_documents({})
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items")
def ret_count():
    #stats = json.loads(json.dumps(db.command("collstats", "data")))
    stats = db.command("collstats", "data")
    return {"count_doc": stats['count']}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
