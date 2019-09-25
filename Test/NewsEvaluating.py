from Test.data import PdfList, NewsList


class KeyWording:
    def __init__(self):
        self.pdfList = PdfList()
        self.newsList = NewsList()  # minute[회의록 번호][[말한사람(L/R),[발언내용(단어 리스트)]]의 리스트]

    keyword = {}  # 키워드 담는 이중 딕셔너리 keyword[키워드][L(좌파)/R(우파)]
    congress = {}  # 국회의원의 편향도 (정당기반)
    def congressImport(self, fileName, bias):
        with open("./Congress/"+fileName+".txt", 'rt', encoding='UTF8') as f:
            congress_list = f.read()
            for name in congress_list.split():
                self.congress[name] = bias

    def congressTotalImport(self,fileName):
        with open("./Congress/"+fileName+".txt", 'rt', encoding='UTF8') as f:
            congress_list = f.read().split()
            for i in range(len(congress_list)//4):
                self.congress[congress_list[4*i-3]]=4*i-1


    def pdfKeywording(self):
        minute_list = self.pdfList.importPickle()
        for minute in minute_list:
            for comment in minute:
                for sentence in comment[1]:
                    for index in range(len(sentence) - 1):
                        for i in range(2, 5):
                            if index + i > len(sentence):
                                break
                            word = ""
                            for j in range(index, index + i):
                                word += sentence[j] + " "
                            if word not in self.keyword.keys():
                                self.keyword[word] = {'bias': 0, 'count': 0}
                            if comment[0][1] == '의원':
                                self.keyword[word]['bias'] += self.congress[comment[0][0]]
                            '''else :
                                self.keyword[word]['bias'] += self.congress[comment[0][1]]'''
                            self.keyword[word]['count'] += 1
        nobias=[]
        for word in self.keyword.keys():
            if self.keyword[word]['bias'] == 0:
                nobias.append(word)
        for word in nobias:
            del self.keyword[word]
    def printKeyword(self):
        print(self.keyword)

    def printPDF(self):
        minute_list= self.pdfList.importPickle()
        print("=========minute==========")
        for minute in minute_list:
            print(minute)
            for comment in minute:
                print("=========comment==========")
                print(comment[0],comment[1])
                '''for index in comment:
                    print("=========index==========")
                    print(index)'''

    def newsTagging(self):
        news_list = self.newsList.importPickle()
        for news in news_list:
            print(news.Content)
            all_bias = 0
            for index, sentence in enumerate(news['content']):
                sentence_bias = 0
                for index in range(len(sentence)-1):
                    for i in range(2,5):
                        if index + i >= len(sentence) :
                            break
                    word = ""
                    for j in range(index, index+i):
                        word += sentence[j] + " "
                    if word in self.keyword.keys():
                        word_bias = self.keyword[word]['R'] - self.keyword[word]['L']  # 우편향일수록 양수. 중도가 0
                        sentence_bias += word_bias
                        all_bias += word_bias
                news['sentence_bias'][index] = sentence_bias
            news['bias'] = all_bias
            print(all_bias)

if __name__ == "__main__":

    keyWording = KeyWording()
    #keyWording.printPDF()
    # keyWording.congressImport("bareunmirae",-1)
    # keyWording.congressImport("independent", 0)
    # keyWording.congressImport("jayuhankuk", 8)
    # keyWording.congressImport("jungui", -5)
    # keyWording.congressImport("minjupyungwha", -7)
    # keyWording.congressImport("theminju", -2)
    print(len(keyWording.congress))
    '''keyWording.pdfKeywording()
    keyWording.printKeyword()
    keyWording.newsTagging()'''
