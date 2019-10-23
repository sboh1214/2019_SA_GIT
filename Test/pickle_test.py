from data import NewsList

newsList = NewsList()

del_list=list()
news_list=newsList.importPickle()
for index,news in enumerate(news_list):
    if news.Bias == None:
        del_list.append(news)

for news in del_list:
    news_list.remove(news)

export=NewsList(news_list)
export.exportPickle()


