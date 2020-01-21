from data import PdfList, NewsList
from khaiii import KhaiiiApi
from itertools import groupby
from tqdm import tqdm
from multiprocessing.dummy import Pool
import pickle, code, traceback, signal
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
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
    sentence_error = 0
    sentence_success = 0
    sentence_none = 0
    error_press = dict()
    error_link = list()
    press_count = dict()
    '''with open("./Test/Data/NewsDataM" + ".dat", 'rb') as f:
        news_list = pickle.load(f)'''

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
                
    def printByCount(self):
        count=int(input("Print Keyword Coun? :"))
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
            if self.keyword[word]['count'] < count:
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

    def newsLabelingMulti(self,news):
        news_keyword = dict()
        news_count = 0
        #print(type(news))
        if(type(news.Content)==str):
            self.error_link.append(news.ID)
            if (news.Press not in self.error_press):
                self.error_press[news.Press]=0
            self.error_press[news.Press]+=1
            news.Bias=-9999
            return -1
        for sent_index, sentence in enumerate(news.Content):
            sentence_keyword = dict()
            sentence_count = 0
            try:
                morph = self.morphAnalyzer.morphAnalyze(sentence)
                sent_analyze = self.morphAnalyzer.morphKeywording(morph)
            except:
                self.sentence_error+=1
                news.Sentence_Bias[sent_index]=-9999
                continue
            
            for word in sent_analyze:
                if word in self.keyword:
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
                self.sentence_success+=1
                news.Sentence_Bias[sent_index]=sent_f_minus_alpha/sent_beta_square_sum
            else:
                self.sentence_none+=1
                news.Sentence_Bias[sent_index]=0
        del_list=list()
        for sent_index,sentence in enumerate(news.Content):
            if news.Sentence_Bias[sent_index]==-9999:
                del_list.append(sentence)
        
        for sentence in del_list:
            news.Content.remove(sentence)
            news.Sentence_Bias.remove(-9999)
            
            
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
            news.Bias=0

        self.news_list.append(news)

    def newsLabeling(self,threadCount=56,start=0,finish=1):
        pool=Pool(threadCount)
        index = [i for i in range(start,finish)]
        with open("./Test/Data/NewsDataM" + ".dat", 'rb') as f:
            news_list = pickle.load(f)
        print("News Import Finish")
        with tqdm(total=len(index)) as pbar:
            for i, _ in tqdm(enumerate(pool.imap_unordered(self.newsLabelingMulti,news_list[start:finish]))):
                pbar.update()
        
        print("Error Sentence :",self.sentence_error)
        print("None Sentence:",self.sentence_none)
        print("Success Sentence :",self.sentence_success)
        del_list=list()
        del_count=0
        '''for news in self.news_list[start:finish]:
            if news.Press not in self.press_count:
                self.press_count[news.Press]=0
            self.press_count[news.Press]+=1'''
        for news in self.news_list:
            if news.Bias==-9999:
                del_list.append(news)
                del_count+=1
        for news in del_list:
            self.news_list.remove(news)
        print(del_count," news is Deleted")
        '''for press in self.press_count:
            if press in self.error_press:
                self.press_count[press]={"Total":self.press_count[press],"Error":self.error_press[press],"Rate":self.error_press[press]/self.press_count[press]}
            else:
                self.press_count[press]={"Total":self.press_count[press],"Error":0,"Rate":0}
        print("Press Error")
        for press in self.press_count:
            print(self.press_count[press])'''
        with open("./Test/Data/NewsData"+"_"+str(start)+"_"+str(finish) + "fix.dat", 'wb') as f:
            pickle.dump(self.news_list[start:(finish-del_count)], f)
        print("Export Done")

    def biasCheck(self):
        with open("./Test/Data/NewsData_0_1000000fix" + ".dat", 'rb') as f:
            news_list = pickle.load(f)
        #print(news_list[index].Bias)
        news_over300=0
        news_underm300=0
        news_tot=0
        sent_over300=0
        sent_underm300=0
        sent_tot=0

        news_max=-99999
        news_min=99999
        news_all=dict()
        sentence_max=-99999
        sentence_min=99999
        sentence_all=dict()
        zero=0
        for news in news_list:
            news_tot+=1
            if news.Bias>300 : news_over300+=1
            if news.Bias<-300 : news_underm300+=1
            if(news.Bias>news_max):news_max=news.Bias
            if(news.Bias<news_min):news_min=news.Bias
            if news.Bias not in news_all:
                news_all[news.Bias]=0
            news_all[news.Bias]+=1

            for bias in news.Sentence_Bias:
                sent_tot+=1
                if bias>300 : sent_over300+=1
                if bias<-300 : sent_underm300+=1
                if(bias>sentence_max):sentence_max=bias
                if(bias<sentence_min):sentence_min=bias
                if bias not in sentence_all:
                    sentence_all[bias]=0
                sentence_all[bias]+=1
            if(news.Bias==0):zero+=1
        news_x=list(news_all.keys())
        news_y=list(news_all.values())
        sent_x=list(sentence_all.keys())
        sent_y=list(sentence_all.values())

        print("News",news_tot,news_over300,news_underm300)
        print("Sent",sent_tot,sent_over300,sent_underm300)

        plt.bar(sent_x,sent_y)
        plt.ylim(0,500)
        plt.xlim(-300,300)
        plt.xlabel('Bias')
        plt.ylabel('Count')
        plt.savefig("sent_bias.png", dpi=350)

        print(news_max,news_min,sentence_max,sentence_min,zero)
    def newsCali(news_list):
        for news in news_list:
            if news.Bias > 300 : news.Bias = 300
            if news.Bias < -300 : news.Bias = -300
            news.Bias=news.Bias/150
        for news in news_list:
            for index,bias in enumerate(news.Sentence_Bias):
                if bias > 300 : news.Sentence_Bias[index]=300
                if bias < -300 : news.Sentence_Bias[index]=-300
            news.Sentence_Bias[index]=bias/150

        return news_list
if __name__ == "__main__":
    keyWording = KeyWording()
    keyWording.congressTotalImport("total")
    keyWording.importPickle()
    keyWording.delKeyword(5)
    keyWording.keywordRegression()
    #keyWording.pdfKeywording(threadCount)
    #keyWording.exportPickle()
    keyWording.biasCheck()
    #keyWording.printByCount()
    #print(len(keyWording.keyword))
    threadCount=int(input("Process Count?"))
    start=int(input("Start index?"))
    finish=int(input("Finish index?"))
    #keyWording.newsLabeling(threadCount,start,finish)

