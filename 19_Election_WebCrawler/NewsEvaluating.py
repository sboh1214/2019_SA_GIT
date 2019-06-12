import json
import csv

class Sentiment():

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

       
        