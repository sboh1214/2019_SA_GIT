from data import NewsData, NewsList
import pickle, glob, tqdm
files = glob.glob("/Users/sjk/Downloads/NewsData*.dat")
count = 0
with open("NewsDataM.dat", "wb") as f:
    newslist = []
    for file in tqdm.tqdm(files, unit=" Files"):
        with open(file, 'rb') as f1:
            news_s = pickle.load(f1)
            for new in news_s:
                if type(new) is list:                
                    for news in new:
                        count += 1
                        newslist.append(NewsData(content=news['Content'], title=news['Title'], id=news['ID'], journal=news['Journalist'], press=news['Press'], date=['Date']))
                elif type(new) is str:
                    print(new)
                else:
                    count += 1
                    newslist.append(NewsData(content=new['Content'], title=new['Title'], id=new['ID'], journal=new['Journalist'], press=new['Press'], date=['Date']))
                #newslist.append()
    pickle.dump(newslist, f)
print (count)
