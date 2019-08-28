import json
import csv
from NewsLearning import MorphAnalyzer
from tqdm import tqdm


class Sentiment:

    def senti_dict(wordname):
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)
        result = 0
        for i in range(len(data)):
            if data[i]['word'] == wordname:
                result = data[i]['polarity']
        return result

    def total_senti(self,sentence):
        cost = 0
        morph=MorphAnalyzer.getMorph(sentence)
        for key in morph.keys():
            cost+=senti_dict(key)
        return cost


class Analyzer:  # 형태소 자르기
    morph = []
    senti = Sentiment()
    
    def analyzer(self, line):
        return GetMorpheme(line[3])

    def morph_process(self, filename): #morph list에 
        if(filename == None):
            print("No File")
            exit
        else:
            with open(filename, encoding='utf-8', mode='r') as f:
                data = csv.reader(f)
        for line in tqdm(data, desc=f" {Morpheme} "):
            self.morph.append(self.analyzer(line))

    def cost_write(self, filename):
        senti=Sentiment()
        if(filename == None):
            print("No File")
            exit
        else:
            with open(filename, encoding='utf-8', mode='w') as f:
                data=csv.writer(f)
        for i in tqdm(len(data), desc=f" {Sentiment} "):
            data[i].append(senti.total_senti(self.morph[i]))


if (__name__ == "__main__"):
    pass
