#!/usr/bin/env python
# coding=utf-8
from urllib.request import urlopen
from urllib import error
from bs4 import BeautifulSoup
import json
import time

html = urlopen("https://list.jd.com/list.html?cat=1713,3287,3797")
bsObj = BeautifulSoup(html)
allItemInfo = bsObj.findAll("li",{"class":"gl-item"})
print(allItemInfo[0])


nTestCount = 2
while nTestCount <= 3:
    for ItemInfo in allItemInfo:
        pName = ItemInfo.find("div",{"class":"p-name"})
        title = pName.em.get_text()
        itemURL = "https:"+pName.a["href"]
        print(title + "," + itemURL)
    nTestCount += 1;
