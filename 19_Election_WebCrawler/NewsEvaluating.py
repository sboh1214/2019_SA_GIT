import json
import csv
from NewsLearning import GetMorpheme
from tqdm import tqdm


class Sentiment:

    def data_list(wordname):
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
            data = json.load(f)
        result = [None, None]
        for i in range(len(data)):
            if data[i]['word'] == wordname:
                result.clear()
                result.append(data[i]['word_root'])
                result.append(data[i]['polarity'])
        return result[0], result[1]

    def total_senti(self, article):
        cost = 0
        # 무언가 분석
        return cost


class Analyzer:  # 형태소 자르기
    morph = []

    def analyzer(self, line):
        return GetMorpheme(line[3])

    def morph_process(self, filename):
        if(filename == None):
            print("No File")
            exit
        else:
            with open(filename, encoding='utf-8', mode='r') as f:
                data = csv.reader(f)
        for line in data:
            self.morph.append(self.analyzer(line))

    def cost_write(sel):
        senti = Sentiment()
        with open(filename, encoding='utf-8', mode='w') as f:
            data = csv.writer(f)
            for i in len(data)

if __name__ == "__main__":
    pass
