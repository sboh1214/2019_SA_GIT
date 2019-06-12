import json
import csv
from NewsLearning import GetMorpheme
class Sentiment(word):

    def data_list(wordname):
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)
        result=[None,None]
        for i in range(len(data)):
            if data[i]['word']==wordname:
                result.clear()
                result.append(data[i]['word_root'])
                result.append(data[i]['polarity'])
        return result[0],result[1]

class Analyzer(): #형태소 분석기
    def analyzer(line):
        return GetMorpheme(line[3])
    def cost():
        with open('news.csv',encoding='utf-8',mode='r') as f:
            data=csv.reader(f)
            senti=[]
            for line in data:
               senti.append(analyzer(line))

if __name__=="__main__":
    