#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
_t={}
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

def get_proxi():
    return random.choice(https_proxies)
print(get_proxi())
