from data import NewsData
import pickle

with open("../NewsData.dat", 'rb') as f:
        newslist = pickle.load(f)
        for news in newslist:
            print(news)
            #print(title,press,date,journalist,link,content)
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
