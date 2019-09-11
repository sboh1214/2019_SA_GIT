from .EvaluatingData import PdfList,NewsList
class KeyWording:
    def __init__(self):
        self.pdfList=PdfList()
        self.newsList=NewsList() # minute[회의록 번호][[말한사람(L/R),[발언내용(단어 리스트)]]의 리스트]

    keyword = {}
    # 키워드 담는 이중 딕셔너리 keyword[키워드][L(좌파)/R(우파)]
    def PdfKeywording(self):
        Minutes=self.pdfList.importPickle()
        for minute in Minutes:
            for comment in minute:
                for word in range(len(comment[2]) - 1):
                    for i in range(2, 5):
                        if i >= len(comment[2]): break
                        word = ""
                        for j in range(word, word + i):
                            word += " " + minute[comment][1][j]
                        if word not in self.keyword.keys():
                            self.keyword[word] = {'L': 0, 'R': 0}
                        self.keyword[word][minute[0]] += 1
    
    def NewsTagging(self):
        News=self.newsList.importPickle()
        for news in News:
            allBias=0
            for sentence in news['content']:
                sentenceBias=0
                for word in sentence:
                    wordBias=self.keyword[word]['R']-self.keyword[word]['L'] #우편향일수록 양수. 중도가 0
                    sentenceBias+=wordBias; allBias+=wordBias
                    




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
