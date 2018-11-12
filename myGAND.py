#!/usr/bin/env python
# coding=utf-8
from urllib.request import urlopen
from urllib.request import Request
from urllib import error
from bs4 import BeautifulSoup
import json
import time
import logging


logging.basicConfig(format='[%(asctime)s] %(message)s',level=logging.INFO)

def SimpleLog(func):
    def wrapper(*args,**kwargs):
        logging.info("Enter into :%s" % func.__name__)
        func(*args,**kwargs)
        logging.info("Exit :%s" % func.__name__)
        return func(*args,**kwargs)
    return wrapper

@SimpleLog
def GetBSObject(url,headers,encoding=None):
    bsObj = None
    try:
        request = Request(url=url,headers=headers)
        html = urlopen(request)
        if encoding is not None:
            bsObj = BeautifulSoup(html,fromEncoding=encoding)
        else:
            bsObj = BeautifulSoup(html)
    except error.HTTPError as e:
        print("Error in Getting BSObjetc.")
    finally:
        return bsObj

def GetJSON(jsonStr):
    dataJson = ""
    try:
        strJson = jsonStr[jsonStr.find("{"):jsonStr.rfind("}")+1]
        dataJson = json.loads(strJson)
        #print(dataJson)
    except json.decoder.JSONDecodeError as e:  
        pass
    finally:
        return dataJson


def GetDataSKU(ItemInfo):
    dataSkuA = ItemInfo.find("a",{"class":"p-o-btn focus J_focus"})
    dataSku = dataSkuA["data-sku"]
    return dataSku

def GetTitleAndItemUrl(ItemInfo):
    pName = ItemInfo.find("div",{"class":"p-name"})
    title = pName.em.get_text()
    itemURL = "https:"+pName.a["href"]
    return title,itemURL

def GetPrice(ItemInfo,dataSku):
    priceURL = "https://p.3.cn/prices/mgets?callback=jQuery1&skuIds=J_"+dataSku
    bsObj=GetBSObject(priceURL,headers)
    dataJson = GetJSON(str(bsObj))
    price = 0
    try:
        price = dataJson["p"]
    except TypeError as e:
        price = -1
    finally:
        return price

def GetGoodRate(ItemInfo,dataSku,pageSize):
        urlVeryDetailsJson = "https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv4374&productId="+dataSku+"&score=0&sortType=5&page=0&pageSize="+str(pageSize)+"&isShadowSku=0&fold=1"
        bsObj = GetBSObject(urlVeryDetailsJson,headers,"gb18030")
        jsonPageComments = GetJSON(str(bsObj))
        goodRate = 0
        try:
            goodRate = jsonPageComments["productCommentSummary"]["goodRate"]
        except TypeError as e:
            goodRate = -1
        finally:
            return goodRate

def MoveToNextPage(nPageIndex):
    nextPageURL ="https://list.jd.com/list.html?cat=1713,3287,3797&page="+str(nPageIndex)+"&sort=sort_rank_asc&trans=1&JL=6_0_0" 
    bsObj = GetBSObject(nextPageURL,headers)
    allItemInfo = {}
    allItemInfo = bsObj.findAll("li",{"class":"gl-item"})
    return allItemInfo


url = "https://list.jd.com/list.html?cat=1713,3287,3797"
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64)'
           'AppleWebKit/537.36 (KHTML, like Gecko)'
           ' Chrome/55.0.2883.103 Safari/537.36'}

bsObj = GetBSObject(url,headers)
allItemInfo = bsObj.findAll("li",{"class":"gl-item"})

dictItem = {}
nTestCount = 2
while nTestCount <= 3:
    for ItemInfo in allItemInfo:
        dictItemValue = {}
        
        # Get dataSku,name,title and url
        dataSku = GetDataSKU(ItemInfo)
        title,itemURL=GetTitleAndItemUrl(ItemInfo)
        
        # Get Price
        price = GetPrice(ItemInfo,dataSku)

        # Get the goodRate
        pageSize = 1
        goodRate = GetGoodRate(ItemInfo,dataSku,pageSize)

        # Add into a Dict.
        dictItemValue["title"] = title
        dictItemValue["itemURL"] = itemURL
        dictItemValue["price"] = price
        dictItemValue["goodRate"] = int(goodRate*100)
        dictItem[dataSku] = dictItemValue
        
        # Print for interactive
        strValueToPrint = (title,itemURL,price,str(goodRate*100))
        print(",".join(strValueToPrint))

    time.sleep(3)
    # move to next page
    allItemInfo.clear()
    allItemInfo = MoveToNextPage(nTestCount)

    nTestCount += 1

'''
for key in dictItem:
    for subKey in dictItem[key]:
        #pass
        print(subKey+":"+str(dictItem[key][subKey]))
'''
