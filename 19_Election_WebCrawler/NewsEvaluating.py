"""
    튜플 리스트 (L/R,발언내용,단어별로 잘린 리스트)
"""

'''class Sentiment:

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
        return cost'''


class KeyWording:
    def __init__(self, minute):
        self.Minutes = minute  # minute[회의록 번호][[말한사람(L/R),[발언내용(단어 리스트)]]의 리스트]

    keyword = {}  # 키워드 담는 이중 딕셔너리 keyword[키워드][L(좌파)/R(우파)]
    for minute in Minutes:
        for comment in minute:
            for word in range(len(comment[2]) - 1):
                for i in range(2, 5):
                    if i >= len(comment[2]): break
                    word = ""
                    for j in range(word, word + i):
                        word += " " + minute[comment][1][j]
                    if word not in keyword.keys():
                        keyword[word] = {'L': 0, 'R': 0}
                    keyword[word][minute[0]] += 1


'''class Analyzer:  # 형태소 자르기
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
            data[i].append(senti.total_senti(self.morph[i]))'''

if __name__ == "__main__":
    pass
