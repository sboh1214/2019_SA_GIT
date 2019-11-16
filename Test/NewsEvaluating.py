from data import PdfList, NewsList
from khaiii import KhaiiiApi
from itertools import groupby
from tqdm import tqdm
from multiprocessing.dummy import Pool
import pickle, code, traceback, signal
from sklearn.linear_model import LinearRegression

class MorphAnalyzer():
    api = KhaiiiApi()
    def morphAnalyze(self, content):
        result = list()
        #print(content,'\n')
        for word in self.api.analyze(content):
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
    news_list = list()
    pdf_error = 0
    news_error = 0
    news_success = 0
    with open("./Test/Data/NewsData" + ".dat", 'rb') as f:
        news_list = pickle.load(f)

    def congressTotalImport(self,fileName):
        with open("./Test/Congress/"+fileName+".txt", 'rt', encoding='UTF8') as f:
            congress_list = f.read().split()
            for i in range(len(congress_list)//4):
                self.congress[congress_list[4*i+1]]={'bias':(float(congress_list[4*i+3])+50)/100,'word':dict(),'count':0}

                    

        # NNG:일반명사 NNP:고유명사 NNB:의존명사 NP:대명사 NR:수사
        # JC:접속조사 JKG:관형격조사(소유격조사) 
        # VA : 형용사
    def pdfKeywordingMulti(self,minute):
        try:
            for comment in minute:
                if len(minute)==1:
                    continue
                morphAnalyzer=MorphAnalyzer()
                morph=morphAnalyzer.morphAnalyze(comment[1])
                com_keyword=morphAnalyzer.morphKeywording(morph)
                for word in com_keyword:
                    if comment[0][1] == '의원':
                        if comment[0][0] in self.congress.keys():
                            if(word not in self.keyword.keys()):
                                self.keyword[word]={'left':0,'right':0,'count':0,'a':0,'b':0}
                            self.keyword[word]['count']+=1
                            if self.congress[comment[0][0]]['bias']<0.5: 
                                self.keyword[word]['left']+=1
                            else:
                                self.keyword[word]['right']+=1
                            if(word not in self.congress[comment[0][0]]['word']):
                                self.congress[comment[0][0]]['word'][word]=0
                            self.congress[comment[0][0]]['word'][word]+=1
                            self.congress[comment[0][0]]['count']+=1
        except:
            self.pdf_error+=1
            return -1

    def pdfKeywording(self,threadCount=56):
        minute_list = self.pdfList.importPickle("./Test/Data/parsedPDF.dat")
        pool = Pool(threadCount)
        with tqdm(total=len(minute_list)) as pbar:
            for i, _ in tqdm(enumerate(pool.imap_unordered(self.pdfKeywordingMulti,minute_list))):
                pbar.update()
        print("Error PDF :",self.pdf_error)

    def keywordRegression(self):
        for keyword in self.keyword.keys():
            model=LinearRegression()
            y_c=list()
            f_pc_list=list()
            for congress in self.congress.values():
                if keyword in congress['word'].keys():
                    f_pc = congress['word'][keyword]/congress['count']
                    f_pc_list.append([f_pc])
                    y_c.append([congress['bias']])
            if len(f_pc_list)>1:
                model.fit(X=y_c,y=f_pc_list)
                self.keyword[keyword]['a'],self.keyword[keyword]['b']=model.intercept_[0],model.coef_[0][0]
        del_list=list()
        for keyword in self.keyword.keys():
            if(self.keyword[keyword]['a']==0):
                del_list.append(keyword)
        for word in del_list:
            del(self.keyword[word])
                
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

    def exportPickle(self,keywordFile="./Test/Data/pdfKeyword",congressFile="./Test/Data/congressData"):
        with open(keywordFile + ".dat", 'wb') as f:
            pickle.dump(self.keyword, f)
        with open(congressFile + ".dat", 'wb') as f:
            pickle.dump(self.congress,f)
        print("Pickle Export Finish")
    
    def importPickle(self,keywordFile="./Test/Data/pdfKeyword",congressFile="./Test/Data/congressData"):
        with open(keywordFile + ".dat", 'rb') as f:
            self.keyword = pickle.load(f)
        with open(congressFile + ".dat", 'rb') as f:
            self.congress = pickle.load(f)
        print("Pickle Import Finish")
    
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

    def newsLabelingMulti(self,news):
        news_keyword = dict()
        news_count = 0
        for index, sentence in enumerate(news.Content):
            sentence_keyword = dict()
            sentence_count = 0
            try:
                morph = self.morphAnalyzer.morphAnalyze(sentence)
                sent_analyze = self.morphAnalyzer.morphKeywording(morph)
            except:
                self.news_error+=1
                news.Sentence_Bias[index]=None
                continue
            self.news_success+=1
            for word in sent_analyze:
                if word in self.keyword():
                    if word not in news_keyword:
                        news_keyword[word]=0
                        sentence_keyword[word]=0
                    elif word not in sentence_keyword:
                        sentence_keyword[word]=0
                    news_count+=1
                    sentence_count+=1
                    news_keyword[word]+=1
                    sentence_keyword[word]+=1
            sent_f_minus_alpha=0
            sent_beta_square_sum=0
            for keyword in sentence_keyword:
                f_pn=sentence_keyword[keyword]/sentence_count
                if keyword in self.keyword:
                    sent_beta_square_sum+=pow(self.keyword[keyword]['b'],2)
                    sent_f_minus_alpha+=self.keyword[keyword]['b']*(f_pn-self.keyword[keyword]['a'])
            if(sent_beta_square_sum!=0):
                news.Sentence_Bias[index]=sent_f_minus_alpha/sent_beta_square_sum
            else:
                news.Sentence_Bias[index]=None

        news_beta_square_sum=0
        news_f_minus_alpha=0
        for keyword in news_keyword:
            f_pn=news_keyword[keyword]/news_count
            if keyword in self.keyword:
                news_beta_square_sum+=pow(self.keyword[keyword]['b'],2)
                news_f_minus_alpha+=self.keyword[keyword]['b']*(f_pn-self.keyword[keyword]['a'])
        if(news_beta_square_sum!=0):
            news.Bias=news_f_minus_alpha/news_beta_square_sum   
        else:
            news.Bias=None
        return news

    def newsLabeling(self,threadCount=56,start=0,finish=1):
        pool=Pool(threadCount)
        with tqdm(total=len(self.news_list[start:finish])) as pbar:
            for i, _ in tqdm(enumerate(pool.imap_unordered(self.newsLabelingMulti,self.news_list[start:finish]))):
                pbar.update()
        print("Error News :",self.news_error)
        print("Success News :",self.news_success)
        del_list=list()
        del_count=0
        for news in self.news_list:
            if news.Bias==None:
                del_list.append(news)
                del_count+=1
        for news in del_list:
            self.news_list.remove(news)
        print(del_count," news removed")
        with open("./Test/Data/NewsData"+str(start)+"-"+str(finish) + ".dat", 'wb') as f:
            pickle.dump(self.news_list[start:finish], f)
        print("Export Done")

if __name__ == "__main__":
    threadCount=int(input("Process Count?"))
    start=int(input("Start index?"))
    finish=int(input("Finish index?"))
    keyWording = KeyWording()
    keyWording.congressTotalImport("total")
    keyWording.importPickle()
    keyWording.keywordRegression()
    #keyWording.pdfKeywording(threadCount)
    #keyWording.exportPickle()
    #keyWording.printByCount(5)
    #keyWording.printByCount(1)
    keyWording.newsLabeling(threadCount,start,finish)
