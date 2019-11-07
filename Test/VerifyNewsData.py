from data import NewsData
import pickle
from selectolax.parser import HTMLParser
import re
"""
with open("../NewsData.dat", 'rb') as f:
        newslist = pickle.load(f)
        for news in newslist:
            print(news)
            #print(title,press,date,journalist,link,content)
"""
with open("../NewsRawData.dat", 'rb') as f:
    newslist = pickle.load(f)
    news = newslist[3]['Content']
    selector = "#article_txt > article > p"
    text = ""
    for node in HTMLParser(news).css(selector):
        text += node.text()
    text = re.sub('\xa0', '', text)
        
"""
link = news.Link
title = news.Title
press = news.Press
date = news.Date
content = news.Content
journalist = news.Journalist
link = news['Link']
title = news['Title']
press = news['Press']
date = news['Date']
content = news['Content']
journalist = news['Journalist']
"""
