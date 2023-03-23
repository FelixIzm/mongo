#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymongo
import json

with open('dictionary.json') as f:
    data = f.read()
js = json.loads(data)

myclient = pymongo.MongoClient(js['connect'])
mydb = myclient[js['db_name']]
_req = mydb['requests']

header = {}
with open("header.txt") as inputs:
    for line in inputs:
        header[line.replace("\n","")] = None


csv_header = mydb['csv_header']
if csv_header.drop():
    csv_header = mydb['csv_header']


_keys = {}
def get_keys(obj):
    r={}
    for key in obj:
        #print(key)
        if(key not in _keys) and (key != '_id'):
            _keys[key]=None

#############
recs = _req.find()
i = 1
for rec in recs:
    #print(i)
    i += 1
    get_keys(rec['_data'])

for key in _keys:
    if(key not in header.keys()): 
        header[key]=""

csv_header.insert_one({'csv_header':header})
#print(_keys)
print(header)
