from data import NewsData
import pickle
from selectolax.parser import HTMLParser
import re, random

with open("/Users/sjk/Downloads/NewsData_0_200000.dat", 'rb') as f:
	newslist = pickle.load(f)
	newslist = random.sample(newslist, 7)
	for news in newslist:
		print(news.Title,news.Press,news.Date,news.Journalist,news.Content)
"""
with open("../NewsRawData.dat", 'rb') as f:
    newslist = pickle.load(f)
    news = newslist[3]['Content']
    selector = "#article_txt > article > p"
    text = ""
    for node in HTMLParser(news).css(selector):
        text += node.text()
    text = re.sub('\xa0', '', text)
        
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
