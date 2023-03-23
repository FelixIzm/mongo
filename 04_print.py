#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymongo
import glob
import json




with open('dictionary.json') as f:
    data = f.read()
js = json.loads(data)
myclient = pymongo.MongoClient(js['connect'])
mydb = myclient[js['db_name']]
_req = mydb['requests']

#results = mydb['results']

csv_header = mydb['csv_header']
_keys = csv_header.find()[0]['csv_header']
name = js['db_name']

fx = glob.glob('./'+name+'_*.csv')
csvfile = open(name+'_'+str(len(fx))+'.csv', 'w', encoding='utf8', errors='replace', newline='')
#csvfile = open('data.csv', 'w', encoding='cp1251', errors='replace', newline='')

def _split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def print_rec(rec, _keys):
    #f_str = '"'+str(rec['_id'])+'";'
    f_str = '"'+str(rec['id'])+'";'
#        str(rec['id'])+'";"https://pamyat-naroda.ru/heroes/person-hero' + \
#        str(rec['id'])+'";'
    for key in _keys:
        if key in rec['_data']:
            try:
                f_str += '"'+str(rec['_data'][key]).replace('"',"'")+'";'
            except TypeError:
                print(_keys[key], rec['_data'][key])
                exit()
        elif(key=="ID"):
            pass
        elif(key=='Документ'):
            f_str+= '"'+rec['doc'] +'";'           
        else:
            f_str += '"";'
    return f_str
#######################
header = ''

for key in _keys:
   header += '"'+key+'";'
csvfile.write(header+'\n')
#######################
part=10000
recs = _req.find() # ({"processed":{"$exists":False}}).limit(200000)
#_a = _split(list(recs),part)
_a = divide_chunks(list(recs),part)

for items in _a:
    id_list = []
    for item in items:
        id_list.append(item['_id'])
        #print(item['id'])
        d3 = print_rec(item,_keys)
        csvfile.write(d3+'\n')
    #res = _req.update_many ({ '_id': {'$in':id_list}},{'$set':{'processed':'yes'}})
    #print(res.modified_count)


print("Done")
exit(0)

