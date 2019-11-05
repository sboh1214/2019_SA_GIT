from data import PdfList, NewsList
from khaiii import KhaiiiApi
from itertools import groupby
from tqdm import tqdm
from multiprocessing.dummy import Pool
import pickle, code, traceback, signal

class MorphAnalyzer():
    def morphAnalyze(self, content):
        api = KhaiiiApi()
        result = list()
        #print(content,'\n')
        for word in api.analyze(content):
            for morph in word.morphs:
                result.append([morph.lex,morph.tag])
        return result

    def morphKeywording(self, content):
        keyword = list()
        for word in content: 
            if(word[1] in ['NNG','NNP','NNB']):
                word[1]='NN'
        for word in content: #단일명사가 5글자 이상인 경우
            if(word[1]=='NN' and len(word[0]) >=5):
                keyword.append(word[0])
        group=list()
        for k,g in groupby(content  ,lambda x:x[1]): # Groupby [(태그,단어),(태그,단어), ...]
            listg=[x[0] for x in list(g)]
            group.append((k,listg))
        #print("Iter Group :",group)
        for word in group: #복합명사 추출
            if(word[0]=='NN' and len(word[1]) >=5): 
                keyword.append(word[1])
        for index in range(len(group)-2): #명사+의/와/과+명사 추출 , 명사+관형사형 접미사+명사
            if(group[index][0]=='NN' and group[index+2][0]=='NN'):
                if(group[index+1][1] in ['적','화','의','와','과']):
                    keyword.append(group[index][1]+group[index+1][1]+group[index+2][1])
        for index in range(len(group)-3): #명사+감성 형용사+명사 , 명사+용언형 접미사+명사
            if(group[index][0]=='NN' and group[index+3][0]=='NN'):
                if(group[index+1][0] in ['VA','XSV','XSA']):
                    keyword.append(group[index][1]+group[index+1][1]+group[index+2][1]+group[index+3][1])
        for index in range(len(group)-2): #감성 형용사+명사
            if(group[index][0]=='VA' and group[index+1][0]=='ETM' and group[index+2][0]=='NN'):
                keyword.append(group[index][1]+group[index+1][1]+group[index+2][1])

        for index,word in enumerate(keyword): #키워드 합치기
            if type(word)==list:
                merge=''
                for i in word:
                    merge+=i
                keyword[index]=merge
        
        del_list=list()
        append_list=list()
        for word in keyword: #키워드 거르기
            if word[-1] in ['것','수']:
                del_list.append(word)
            elif word[3:5] == '의원':
                del_list.append(word)
                append_list.append(word[5:])
            elif '.' in word or '․' in word or '․' in word:
                del_list.append(word)
        
        for word in del_list :
            keyword.remove(word)

        for word in append_list :
            keyword.append(word)

        del_list=list()
        for word in keyword:
            if len(word)<5:
                del_list.append(word)
        for word in del_list :
            keyword.remove(word)
        return keyword
    
class KeyWording:
    def __init__(self):
        self.pdfList = PdfList()
        self.newsList = NewsList()
        self.morphAnalyzer = MorphAnalyzer()  # minute[회의록 번호][[말한사람],[발언내용(단어 리스트)]]의 리스트]

    keyword = dict()  # 키워드 담는 이중 딕셔너리 keyword[키워드][편향도]
    congress = dict()  # 국회의원의 편향도 (정당기반)
    headline = set()  # 기사 제목 키워드 추출
    news_keyword = dict()

    def congressTotalImport(self,fileName):
        with open("./Test/Congress/"+fileName+".txt", 'rt', encoding='UTF8') as f:
            congress_list = f.read().split()
            #   print(congress_list)
            for i in range(len(congress_list)//4):
                self.congress[congress_list[4*i+1]]={'bias':(float(congress_list[4*i+3])+50)/100,'word':dict()}

                    

        # NNG:일반명사 NNP:고유명사 NNB:의존명사 NP:대명사 NR:수사
        # JC:접속조사 JKG:관형격조사(소유격조사) 
        # VA : 형용사
    def pdfKeywording(self):
        minute_list=self.pdfList.importPickle()
        for i in range(len(minute_list)):
            for j in range(i+1,len(minute_list)):
                if minute_list[i]==minute_list[j]:
                    print("Same Minute!")
        for minute in tqdm(minute_list,desc='Pdf Keywording'):
            for comment in minute:
                if len(minute)==1:
                    continue
                #pool=Pool(self.thread)
                morph=self.morphAnalyzer.morphAnalyze(comment[1])
                com_keyword=self.morphAnalyzer.morphKeywording(morph)
                for word in com_keyword:
                    if comment[0][1] == '의원':
                        if comment[0][0] in self.congress.keys():
                            if(word not in self.keyword.keys()):
                                self.keyword[word]={'left':0,'right':0,'a':0,'b':0}
                            if self.congress[comment[0][0]]<0.5: 
                                self.keyword[word]['left']+=1
                            else:
                                self.keyword[word]['right']+=1
                            if(word not in self.congress['word']):
                                self.congress['word'][word]=0
                            self.congress['word'][word]+=1
                            #in_congress+=1
                        #else:
                            #not_in_congress+=1
                            #not_in_name.add(comment[0][0])
        #print("Congress in list :",in_congress)
        #print("Congress not in list :",not_in_congress,not_in_name)

    def newsKeywording(self):
        news_list=self.newsList.importPickle()
        for news in tqdm(news_list,desc="Tagging News"):
            for index, sentence in enumerate(news.Content):
                morph = self.morphAnalyzer.morphAnalyze(sentence)
                sent_keyword = self.morphAnalyzer.morphKeywording(morph)
                for word in sent_keyword:
                    if word not in self.news_keyword:
                        self.news_keyword[word]=0
                    self.news_keyword+=1
        

    def printByCount(self, count):
        for word in self.keyword.keys():
            if self.keyword[word]['left']+self.keyword[word]['right'] >= count:
                #pp=PrettyPrinter(indent=4)
                print((word,self.keyword[word]))
    def printByBias(self, bias1, bias2):
        for word in self.keyword.keys():
            if self.keyword[word]['bias'] >= bias1 and self.keyword[word]['bias'] <=bias2:
                print((word,self.keyword[word]))

    def delKeyword(self, count):
        del_word=list() 
        for word in self.keyword.keys():
            if self.keyword[word]['left']+self.keyword[word]['right'] >= count:
                del_word.append(word)
        for word in del_word:
            del self.keyword[word]

    def exportPickle(self,fileName="./Test/pdfKeyword"):
        with open(fileName + ".dat", 'wb') as f:
            pickle.dump(self.keyword, f)
    
    def importPickle(self,fileName="./Test/pdfKeyword"):
        with open(fileName + ".dat", 'rb') as f:
            self.keyword = pickle.load(f)
    
    def headlineKeywording(self):
        news_list = self.newsList.importPickle()
        print(len(news_list))
        for news in tqdm(news_list,desc='Headline Keywording'):
            #print(news.Title)
            morph=self.morphAnalyzer.morphAnalyze(news.Title)
            title_keyword=self.morphAnalyzer.morphKeywording(morph)
            for word in title_keyword:
                self.headline.add(word)

    def headlineDuplicate(self):
        delWord=list()
        for keyword in self.keyword:
            if keyword not in self.headline:
                delWord.append(keyword)
        for word in delWord:
            del(self.keyword[word])

    '''def headlineKeywording(self):
        news_list = self.newsList.importPickle()
        for news in news_list:
            title=news.Title.split()
            for index in range(len(title)-1):
                for i in range(1, 5):
                    if index + i > len(title):
                        break
                    word = ""
                    for j in range(index,index+i):
                        word += title[j] + " "
                self.headline.append(word)
        delWord = []
        for keyword in self.keyword:
            if keyword not in self.headline:
                delWord.append((keyword))
        for word in delWord:
            del(self.keyword[word])'''


    def newsTagging(self,fileName="NewsData"):
        news_list = self.newsList.importPickle()
        excepted=0
        for news in tqdm(news_list,desc="Tagging News"):
            all_bias=0
            #print(len(news.Content))
            #print(news.Content,"\n\n\n")
            try:
                for index, sentence in enumerate(news.Content):
                    sentence_bias = 0
                    morph = self.morphAnalyzer.morphAnalyze(sentence)
                    sent_keyword = self.morphAnalyzer.morphKeywording(morph)
                    for word in sent_keyword:
                        if(word in self.keyword):
                            word_bias = self.keyword[word]['bias']
                            sentence_bias += word_bias
                            all_bias += word_bias
                    news.Sentence_Bias[index] = sentence_bias
                news.Bias = all_bias
                #print(news.Content, all_bias,'\n\n\n')
            except:
                news.Bias = None
                excepted+=1
                #print("Excepted")
                continue
        print("Excepted News :",excepted)
        newsList=NewsList(news_list)
        newsList.exportPickle(fileName)

    '''def newsTagging(self):
        news_list = self.newsList.importPickle()
        for news in news_list:
            #print(news.Content )
            all_bias = 0
            for index, sentence in enumerate(news.Content):
                sentence_split = sentence.split()
                sentence_bias = 0
                for wordIndex in range(len(sentence_split)-1):
                    for i in range(1, 5):
                        if wordIndex + i > len(sentence_split):
                            break
                        word = ""
                        for j in range(wordIndex, wordIndex+i):
                            word += sentence_split[j] + " "
                        if word in self.keyword.keys():
                            word_bias = self.keyword[word]['bias']  # 우편향일수록 양수. 중도가 0
                            sentence_bias += word_bias
                            all_bias += word_bias
                news.Sentence_Bias[index] = sentence_bias
            news.Bias = all_bias
            print(news.Content, all_bias/len(news.Content))
            print("\n\n\n")'''

if __name__ == "__main__":

    keyWording = KeyWording()
    keyWording.congressTotalImport("total")
    keyWording.newsKeywording()
    keyWording.importPickle()
    #keyWording.pdfKeywording()
    keyWording.exportPickle()
    #keyWording.printByCount(1)
    '''keyWording.headlineKeywording()
    print("Head line Keywording")
    print(keyWording.headline)
    keyWording.headlineDuplicate()
    print("\n\n\nKeyword After Headline")
    keyWording.printByCount(1)'''
    keyWording.newsTagging("./Test/newsData")
