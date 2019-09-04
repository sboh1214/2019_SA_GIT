import json
import csv
from tqdm import tqdm
from ..NewsLearning.NewsLearning import MorphAnalyzer


class Sentiment:

    def senti_dict(self, wordname):
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)
        result = 0
        for i in range(len(data)):
            if data[i]['word'] == wordname:
                result = data[i]['polarity']
        return result

    def total_senti(self, sentence):
        cost = 0
        morph = MorphAnalyzer.getMorph(sentence)
        for key in morph.keys():
            cost += senti_dict(key)
        return cost
class Minutes:
    keyword={} #키워드 담는 이중 딕셔너리 keyword[키워드][L(좌파)/R(우파)]
    minute=[] #회의록 담는 리스트가 담긴 튜플의 리스트 (L/R,발언내용)
    for comment in minute:
        for index in range(len(comment[1])-1):
            for i in range(2,5): #iterator로 수정할 것
                word=""
                for j in range(index,index+i):
                    word+=minute[comment][1][j]
                if word not in keyword.keys():
                    keyword[word]={'L':0,'R':0}
                keyword[word][minute[0]]+=1
    




class Analyzer:  # 형태소 자르기
    morph = []
    senti = Sentiment()

    def analyzer(self, line):
        return GetMorpheme(line[3])

    def morph_process(self, filename):  # morph list에
        if filename is None:
            print("No File")
            exit()
        else:
            with open(filename, encoding='utf-8', mode='r') as f:
                data = csv.reader(f)
        for line in tqdm(data, desc=f" {Morpheme} "):
            self.morph.append(self.analyzer(line))

    def cost_write(self, filename):
        senti = Sentiment()
        if filename is None:
            print("No File")
            exit()
        else:
            with open(filename, encoding='utf-8', mode='w') as f:
                data = csv.writer(f)
        for i in tqdm(len(data), desc=f" {Sentiment} "):
            data[i].append(senti.total_senti(self.morph[i]))


if __name__ == "__main__":
    pass
