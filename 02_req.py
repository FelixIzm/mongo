#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pprint import pprint
import requests, json
#from bson.objectid import ObjectId
import pymongo
from requests_html import HTMLSession
import random
import sys
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError

#####################     Удаление поля      #####################
#  db.test.update({}, {$unset: {"processed":1}}, false, true);
#  db.results.update({}, {$unset: {"processed":1}}, false, true);
##################################################################
# db.demo476.updateMany({_id:{$in:[1,3]}},{$set:{Name:"Robert"}});
##################################################################
# use 789ap;
# db.requests.updateMany({}, {$unset:{"_data":1}});
# db.requests.updateMany({}, { $unset : {"processed":1}});


with open('dictionary.json') as f:
    data = f.read()
js = json.loads(data)
myclient = pymongo.MongoClient(js['connect'])
mydb = myclient[js['db_name']]
_req = mydb['requests']

_set = mydb['settings']
_sets = _set.find()

headers = _sets[0]['headers']
cookies = _sets[0]['cookies']


def GET_UA():
    uastrings = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",\
                "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",\
                "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",\
                "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"\
                ]
    return random.choice(uastrings)

http_proxies = []
with open("proxies.txt") as inputs:
    for line in inputs:
        _a= line.split(";")
        #print(_a[0])
        http_proxies.append({_a[0]:_a[0]+"://"+_a[1]+":"+_a[2].replace("\n","")})

https_proxies = []
with open("https.txt") as inputs:
    for line in inputs:
        _a= line.split(";")
        #print(_a[0])
        https_proxies.append({"HTTPS":"HTTPS://"+_a[0]+":"+_a[1].replace("\n","")})

def get_http_proxi():
    return random.choice(http_proxies)

def get_https_proxi():
    return random.choice(https_proxies)



def get_info(req):
    global cookies,headers
    session = HTMLSession()
    headers['User-Agent'] = GET_UA()
    info_url ='https://obd-memorial.ru/html/info.htm?id='+str(req['id'])
    result={}
    try:
        res3 = session.get(info_url,cookies=cookies,headers=headers,proxies=get_http_proxi(), timeout=2)
        list_title = res3.html.find('.card_param-title')
        list_result = res3.html.find('.card_param-result')
        for x in range(len(list_result)):
            if(list_title[x].text!="ID"):
                result[list_title[x].text]=list_result[x-1].text
        #_req.update_one({'_id':req['_id']},{'$set':{'_data': result,'processed':'yes'}})
        return result
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        #print("id error = ",req['id'])
        return {}
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)        


if __name__ == '__main__':
    count_doc = _req.count_documents({"processed": { "$exists": False }})
    #_w =_req.find({"processed": { "$exists": False }})
    while( count_doc > 0):
        print(count_doc)
        _t =_req.find({"processed": { "$exists": False }}).limit(100).rewind()
        for _rec in _t:
            res = get_info(_rec)
            if(len(res)>0):
                #print(len(res)," = ",_rec['_id'])
                _req.update_one({'_id':_rec['_id']},{'$set':{'_data': res,'processed':'yes'}})
            else:
                pass
        count_doc = _req.count_documents({"processed": { "$exists": False }})
