#!/usr/bin/env python
# coding=utf-8
from urllib.request import urlopen
from urllib.request import Request
from urllib import error
from bs4 import BeautifulSoup
import json
import time

url = "https://list.jd.com/list.html?cat=1713,3287,3797"
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64)'
           'AppleWebKit/537.36 (KHTML, like Gecko)'
           ' Chrome/55.0.2883.103 Safari/537.36'}
request = Request(url=url,headers=headers)
html = urlopen(request)
bsObj = BeautifulSoup(html)
allItemInfo = bsObj.findAll("li",{"class":"gl-item"})
#print(allItemInfo[0])

dictItem = {}
nTestCount = 2
while nTestCount <= 2:
    #dictItemValue = {}
    for ItemInfo in allItemInfo:
        #dictItemValue.clear()
        dictItemValue = {}
        dataSkuA = ItemInfo.find("a",{"class":"p-o-btn focus J_focus"})
        dataSku = dataSkuA["data-sku"]
        pName = ItemInfo.find("div",{"class":"p-name"})
        title = pName.em.get_text()
        itemURL = "https:"+pName.a["href"]
        
        # Get Price
        priceURL = "https://p.3.cn/prices/mgets?callback=jQuery1&skuIds=J_"+dataSku
        request = Request(url=priceURL,headers=headers)
        html = urlopen(request)
        bsObj=BeautifulSoup(html)
        strReturn = str(bsObj)
        strJson = strReturn[strReturn.find("{"):strReturn.rfind("}")+1]
        dataJson = json.loads(strJson)
        
        # Add into a Dict.
        dictItemValue["title"] = title
        dictItemValue["itemURL"] = itemURL
        dictItemValue["price"] = dataJson["p"]
        #dictItem[dataSku] = title+","+itemURL+","+dataJson["p"]
        dictItem[dataSku] = dictItemValue
    nTestCount += 1


for key in dictItem:
    for subKey in dictItem[key]:
        print(subKey+":"+dictItem[key][subKey])

