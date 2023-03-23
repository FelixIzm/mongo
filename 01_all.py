#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
import requests, re, json
import asyncio,urllib.parse
import csv,sys
import argparse
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
import multiprocessing
import time


with open('dictionary.json') as f:
    data = f.read()
js = json.loads(data)

myclient = pymongo.MongoClient(js['connect'])
print(js['ip'],js['port'],js['db_name'])
mydb = myclient[js['db_name']]
_set = mydb['settings']
_req = mydb['requests']

# Книга памят
# https://obd-memorial.ru/html/getimageinfo?id=409663384&_=1679122575655

#url3='lp=T~923 сп&entity=000000011111110&entities=7003,8001,6006,6007,30,24,28,27,23,34,22,20,21'
url3=js['url3']+'&ps=200'

 
def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('name', nargs='?')
    return parser
 
 

# ID
# Doc = Вид документа
# f1  = Фамилия
# f2  = Имя
# f3  = Отчество
# f4  = Дата рождения/Возраст
# f5  = Место рождения
# f6  = Дата и место призыва
# f7  = Последнее место службы
# f8  = Воинское звание
# f9  = Причина выбытия
# f10 = Дата выбытия
# f11 = Место захоронения
# f12 = Первичное место захоронения



sys.tracebacklimit = None
cookies = {}
headers={}
secret_cookie = "3fbe47cd30daea60fc16041479413da2"
secret_cookie_value = ''
JSESSIONID_value = ''
countPages = ''
headers['User-Agent']='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
loop = asyncio.get_event_loop()

########################################################
url1= 'https://obd-memorial.ru/html'
url2 = '/search.htm?'
# место призыва - d
# место рождения - pb
# место службы - lp


def excepthook(type, value, traceback):
    print(value)
    print('excepthook')
    print(traceback)


#sys.excepthook = excepthook

def split_list(a_list):
    half = len(a_list)//2
    return a_list[:half], a_list[half:]

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def main():
    global JSESSIONID_value, secret_cookie,secret_cookie_value, countPages, headers, cookies, url2,url3
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )

    URL = 'https://obd-memorial.ru/html'
    URL_search = URL + '/search.htm?'+url3
    print(URL_search)
    s = requests.get('https://obd-memorial.ru/html/advanced-search.htm',headers=headers)
    print(s.status_code)
    if(s.status_code==307 or s.status_code==200):
        secret_cookie_value = s.cookies[secret_cookie]
        cookies = { secret_cookie:secret_cookie_value}
        cookies['request']=urllib.parse.quote(url3)
        headers['cookie']=secret_cookie+"="+secret_cookie_value
        headers['path'] = '/html/search.htm?'+urllib.parse.quote(url3)
        headers['referer']='https://obd-memorial.ru/html/advanced-search.htm'
        headers['cookie']=secret_cookie+"="+secret_cookie_value+'; request='+urllib.parse.quote(url3)
        headers['referer']='https://obd-memorial.ru/html/advanced-search.htm'
        headers['authority'] = 'obd-memorial.ru'
        headers['User-Agent']='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'
        headers['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        headers['Accept-Language'] = 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        headers['Connection'] = 'keep-alive'
        headers['Upgrade-Insecure-Requests']='1'
        headers['path'] = '/html/search.htm?'+urllib.parse.quote(url3)
        r1 = requests.get(URL_search,cookies=cookies,headers=headers)
        if('JSESSIONID' in r1.cookies.keys()):
            JSESSIONID_value =  r1.cookies["JSESSIONID"]
            cookies = {'JSESSIONID': JSESSIONID_value, secret_cookie:secret_cookie_value}
            cookies['request']=urllib.parse.quote(url3)
            cookies['showExtendedParams']='false'
            headers['JSESSIONID'] = JSESSIONID_value
            headers['referer']='https://obd-memorial.ru/html/advanced-search.htm'
            headers['authority'] = 'obd-memorial.ru'
            headers['User-Agent']='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'
            headers['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            headers['Accept-Language'] = 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
            headers['Accept-Encoding'] = 'gzip, deflate, br'
            headers['Connection'] = 'keep-alive'
            headers['cookie']=secret_cookie+"="+secret_cookie_value+'; request='+urllib.parse.quote(url3)+'; JSESSIONID='+JSESSIONID_value
            headers['Upgrade-Insecure-Requests']='1'
            headers['path'] = '/html/search.htm?'+urllib.parse.quote(url3)

            r2 = requests.get(URL_search,cookies=cookies,headers=headers)
            match = re.search(r'countPages = \d+',r2.text)
            if match:
                m1=re.search(r'\d+',match[0])
                countPages = (m1[0])
            if(countPages==''):
                raise ValueError('Не определилось число страниц!')

            _set.insert_one({'headers':headers, 'cookies':cookies, 'countPages':countPages})

        else:
            print('else+++')
            raise ValueError('JSESSIONID not')
    else:
        print(s.status_code)



def get_page(page):
    global cookies,headers
    ids={}
    print("get_page = ", page)
    if(page==0):
        URL_search =url1+url2+url3
        #cookies[secret_cookie]=secret_cookie_value
        #cookies['request']=urllib.parse.quote(url3)
        headers['cookie']=secret_cookie+"="+secret_cookie_value
        res1 = requests.get(URL_search,cookies=cookies,headers=headers)
        if('JSESSIONID' in res1.cookies.keys()):
            #cookies[secret_cookie]=secret_cookie_value
            #cookies['request']=urllib.parse.quote(url3)
            #cookies['JSESSIONID'] = JSESSIONID_value
            res2 = requests.get(URL_search,cookies=cookies,headers=headers,timeout=10)
            soup = BeautifulSoup(res2.text, 'html.parser')
            list_result = soup.find_all("div", {"class": "search-result"})
            while (len(list_result)==0):
                res2 = requests.get(URL_search,cookies=cookies,headers=headers,timeout=10)
                soup = BeautifulSoup(res2.text, 'html.parser')
                list_result = soup.find_all("div", {"class": "search-result"})
            print('status - {}, length - {}'.format(res2.status_code,len(list_result)))
            for res in list_result:
                ids[res['id']]=res.find('div', {"class":"search-result__col-pos-and-icon"}).find('img')['title']
            return ids
    else:
        URL_search =url1+url2+url3 +'&p='+str(int(page)+1)
        #cookies[secret_cookie]=secret_cookie_value
        #cookies['request']=urllib.parse.quote(url3)
        #cookies['JSESSIONID'] = JSESSIONID_value
        res1 = requests.get(URL_search,cookies=cookies,headers=headers)
        if(secret_cookie in res1.cookies.keys()):
            res2 = requests.get(URL_search,cookies=cookies,headers=headers,timeout=10)
            soup = BeautifulSoup(res2.text, 'html.parser')
            list_result = soup.find_all("div", {"class": "search-result"})
            while (len(list_result)==0):
                res2 = requests.get(URL_search,cookies=cookies,headers=headers,timeout=10)
                soup = BeautifulSoup(res2.text, 'html.parser')
                list_result = soup.find_all("div", {"class": "search-result"})

            #print('status - {}, length - {}'.format(res2.status_code,len(list_result)))
            for res in list_result:
                ids[res['id']]=res.find('div', {"class":"search-result__col-pos-and-icon"}).find('img')['title']
            return ids

def get_list_info(list_ids):
    for id in list_ids:
        result = get_page(id)
        for key, value in result.items():
            _req.insert_one({'id':key,'doc':value})
    print('{} записей'.format(len(list_ids)))

async def fxMain():
    global countPages #, insertedPages
    print('countPages = {}'.format(countPages))

    futures = [get_page(i) for i in range(0, int(countPages))]
    for i, future in enumerate(futures):
        result = await future
        #print(i)
        for key, value in result.items():
            _req.insert_one({'id':key,'doc':value})


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args()
    # если что-то передали в аргументах, удаляем таблицы и все заново
    if namespace.name:
        _req = mydb['requests']
        if _req.drop():
            _req = mydb['requests']
        _set = mydb['settings']
        if _set.drop():
            _set = mydb['settings']
        main()
    else:
        _sets = _set.find()
        headers = _sets[0]['headers']
        cookies = _sets[0]['cookies']
        totalPages = int(_sets[0]['countPages'])
        #print(len(list(count_pages)))
        countPages = int(int(_req.count_documents({"id": { "$exists": True }}))/200)
        print(totalPages,countPages)
        restPages = totalPages-countPages
        if(restPages>0):
            _r = range(restPages+1, totalPages+1)
            ids = [str(_pages) for _pages in _r]
            thrnum = 4
            asd= list(split(ids,thrnum))
    #        print(asd)

            parms = []
            for i in asd:
                parms.append(i)

            multiprocessing.freeze_support()
            pool = multiprocessing.Pool( processes = thrnum, )
            clc = time.time()
            pool.map( get_list_info, parms )
            clc = time.time() - clc
            print( "время {0:.2f} секунд".format( clc ) )

        exit(1)
        #print(headers)
        #print(cookies)


#loop.run_until_complete(fxMain())
#loop.close()
