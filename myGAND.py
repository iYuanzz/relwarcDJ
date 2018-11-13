#!/usr/bin/env python
# coding=utf-8
from urllib.request import urlopen
from urllib.request import Request
from urllib import error
from bs4 import BeautifulSoup
import json
import time
import logging
import functools
from multiprocessing import Pool

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64)'
           'AppleWebKit/537.36 (KHTML, like Gecko)'
           ' Chrome/55.0.2883.103 Safari/537.36'}

def InitialLog():
    logger = logging.getLogger("funny logger")
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler("./funny_log.log")
    format="[%(asctime)s] %(name)s:%(message)s"
    formatter = logging.Formatter(format)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger


def NotSoSimpleLog(bPass):
    def ActualDecorator(func):
        @functools.wraps(func)
        def Wrapper(*args,**kwargs):
            logger = InitialLog()
            logger.info("Enter into :%s" % func.__name__)
            try:
                func(*args,**kwargs)
            except:
                err = "exception raised in"+func.__name__
                logger.exception(err)
                if bPass:
                    raise
                else:
                    pass
            finally:
                logger.info("Exit :%s" % func.__name__)
            return func(*args,**kwargs)
        return Wrapper
    return ActualDecorator

@NotSoSimpleLog(True)
def GetBSObject(url,headers,encoding=None):
    bsObj = None
    request = Request(url=url,headers=headers)
    html = urlopen(request)
    if encoding is not None:
        bsObj = BeautifulSoup(html,fromEncoding=encoding)
    else:
        bsObj = BeautifulSoup(html)
    return bsObj


@NotSoSimpleLog(False)
def GetJSON(jsonStr):
    dataJson = ""
    strJson = jsonStr[jsonStr.find("{"):jsonStr.rfind("}")+1]
    dataJson = json.loads(strJson)
    return dataJson

@NotSoSimpleLog(False)
def GetDataSKU(ItemInfo):
    dataSkuA = ItemInfo.find("a",{"class":"p-o-btn focus J_focus"})
    dataSku = dataSkuA["data-sku"]
    return dataSku

@NotSoSimpleLog(False)
def GetTitleAndItemUrl(ItemInfo):
    pName = ItemInfo.find("div",{"class":"p-name"})
    title = pName.em.get_text()
    itemURL = "https:"+pName.a["href"]
    return title,itemURL

@NotSoSimpleLog(False)
def GetPrice(ItemInfo,dataSku):
    priceURL = "https://p.3.cn/prices/mgets?callback=jQuery1&skuIds=J_"+dataSku
    bsObj=GetBSObject(priceURL,headers)
    dataJson = GetJSON(str(bsObj))
    price = 0
    price = dataJson["p"]
    return price

@NotSoSimpleLog(False)
def GetGoodRate(ItemInfo,dataSku,pageSize):
        urlVeryDetailsJson = "https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv4374&productId="+dataSku+"&score=0&sortType=5&page=0&pageSize="+str(pageSize)+"&isShadowSku=0&fold=1"
        bsObj = GetBSObject(urlVeryDetailsJson,headers,"gb18030")
        jsonPageComments = GetJSON(str(bsObj))
        goodRate = 0
        goodRate = jsonPageComments["productCommentSummary"]["goodRate"]
        return goodRate

@NotSoSimpleLog(True)
def MoveToNextPage(nPageIndex):
    nextPageURL ="https://list.jd.com/list.html?cat=1713,3287,3797&page="+str(nPageIndex)+"&sort=sort_rank_asc&trans=1&JL=6_0_0" 
    bsObj = GetBSObject(nextPageURL,headers)
    allItemInfo = {}
    allItemInfo = bsObj.findAll("li",{"class":"gl-item"})
    return allItemInfo

def OutputTheResult(strItem):
    with open("result.txt","a+") as f:
        f.writelines(strItem)

def CrawlTheItem(nStartPage,nEndPage):
    allItemInfo = None

    print(str(nStartPage)+","+str(nEndPage))
    if nStartPage == 1:
        url = "https://list.jd.com/list.html?cat=1713,3287,3797"

        bsObj = GetBSObject(url,headers)
        allItemInfo = bsObj.findAll("li",{"class":"gl-item"})
    else:
        allItemInfo = MoveToNextPage(nStartPage)

    for i in range(nStartPage+1,nEndPage+1):
        for ItemInfo in allItemInfo:
            #dictItemValue = {}
        
            # Get dataSku,name,title and url
            dataSku = GetDataSKU(ItemInfo)
            title,itemURL=GetTitleAndItemUrl(ItemInfo)
        
            # Get Price
            price = GetPrice(ItemInfo,dataSku)

            # Get the goodRate
            pageSize = 1
            goodRate = GetGoodRate(ItemInfo,dataSku,pageSize)

            # Add into a Dict.
            #dictItemValue["title"] = title
            #dictItemValue["itemURL"] = itemURL
            #dictItemValue["price"] = price
            #dictItemValue["goodRate"] = int(goodRate*100)
            #dictItem[dataSku] = dictItemValue
        
            # Print for interactive
            strValueToPrint = (dataSku,title,itemURL,price,str(goodRate*100))
        
            OutputTheResult(",".join(strValueToPrint)+"\n")
        
        time.sleep(3)
        # move to next page
        allItemInfo.clear()
        allItemInfo = MoveToNextPage(i)
    
    return nEndPage


if __name__=="__main__":
    pool = Pool()
    
    #dictItem = {}a
    for i in range(1,20,10):
        pool.apply_async(CrawlTheItem,(i,i+10))

    pool.close()
    pool.join()
    '''
    for key in dictItem:
        for subKey in dictItem[key]:
            #pass
            print(subKey+":"+str(dictItem[key][subKey]))
    '''
