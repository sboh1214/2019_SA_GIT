from data import NewsData
import pickle
from selectolax.parser import HTMLParser
import re
import random

with open("/Users/sjk/Downloads/NewsData_0_200000fix.dat", 'rb') as f:
    lst = pickle.load(f)
    while True:
        search = input()
        for i in range(len(lst)):
            if search in lst[i].Title:
                print("FOUND",lst[i].Title)
                print(i)
                break


"""
with open("/Users/sjk/Downloads/NewsData_0_200000.dat", 'rb') as f:
	newslist = pickle.load(f)
	newslist = random.sample(newslist, 7)
	for news in newslist:
		print(news.Title,news.Press,news.Date,news.Journalist,news.Content)

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
