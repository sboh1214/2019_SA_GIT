"""
Execute this file with command line
$ python3 NewsLearning.py file=Test/NewsData dev=False
"""
import itertools
from datetime import datetime
import os
from math import sqrt, ceil
import sys
import platform

from keras import layers, models, losses, optimizers, activations
from keras.preprocessing.text import Tokenizer
from keras.callbacks import TensorBoard
from keras import backend as K

import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
from bs4 import BeautifulSoup

from data import NewsList


class Data:
    """

    """

    tokenizer = Tokenizer()
    RnnX = []
    RnnY = []
    CnnX = []
    CnnY = []

    Rnn_Model = None
    Cnn_Model = None

    History = None

    def __init__(self, file, verbose=False, max_len=100, dev=False):
        self.Verbose = verbose
        self.MaxLen = max_len
        self.Dev = dev
        self.__get_news_data(filename=file)

    @staticmethod
    def __info(msg):
        print('\033[35m'+msg+'\033[0m')

    @staticmethod
    def __clean(sentences:list):
        for i in range(len(sentences)):
            sentences[i] = sentences[i].replace('\n','')
        return sentences

    @staticmethod
    def __square(a, side):
        output = [[0]*side for _ in range(side)]
        for i, bias in enumerate(a):
            output[i//side][i%side] = bias
        return output

    @staticmethod
    def __pad(a, max_len):
        if len(a)==max_len:
            return a
        elif len(a)>max_len:
            return a[0:len(a)]
        else:
            return a.extend([0 for _ in range(max_len-len(a))])

    def __get_news_data(self, filename: str):
        """

        """
        self.__info('\nImport News List')
        news_list = NewsList().importPickle(filename)
        if self.Verbose:
            print(news_list[0])
        print(len(news_list) + 'News Imported')
        if self.Dev == True:
            news_list = news_list[:100]
        print(len(news_list) + 'News will be used')

        self.__info('\nAnalyze Data')
        max_sentence = 0
        for i in news_list:
            if max_sentence<len(i.Content):
                max_sentence = len(i.Content)
        self.CnnSide = max_sentence
        print('Maximum Sentences Count : ' + max_sentence)

        self.__info('\nBuild Data : RnnX, RnnY, CnnX, CnnY')
        for news in tqdm(news_list):
            self.RnnX.extend(self.__clean(news.Content))
            self.RnnY.extend(news.Sentence_Bias)
            length = ceil(sqrt(len(news.Sentence_Bias)))
            self.CnnX.append(self.__square(news.Sentence_Bias, max_sentence))
            self.CnnY.append(news.Bias)
        if self.Verbose:
            self.__info('Rnn X ('+len(self.RnnX)+')')
            print(str(self.RnnX[0])[:80])
            self.__info('Rnn X ('+len(self.RnnY)+')')
            print(self.RnnY[0])
            self.__info('Rnn X ('+len(self.CnnX)+')')
            print(str(self.CnnX[0])[:80])
            self.__info('Rnn X ('+len(self.CnnY)+')')
            print(self.CnnY[0])

        self.__info('\nPre-Process CnnX')
        cnnx = np.array(self.CnnX)
        cnnx = cnnx.reshape((len(cnnx), max_sentence, max_sentence, 1))
        self.CnnX = cnnx

        self.__info('\nPre-Process RnnX')
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(self.RnnX)
        rnnXlist = tokenizer.texts_to_sequences(self.RnnX)
        for i in tqdm(rnnXlist):
            self.__pad(i, self.MaxLen)
        rnnXarray=np.array([self.__pad(i, self.MaxLen) for i in rnnXlist])
        self.RnnX = rnnXarray
        if self.Verbose:
            print(str(self.RnnX[0])[:80])

class RNN(models.Model):
    def __init__(self, max_len , data_count, max_features=20000):
        x=layers.Input((max_len,))
        h=layers.Embedding(max_features, 128)(x)
        h=layers.LSTM(128, dropout=0.2, recurrent_dropout= 0.2)(h)
        y=layers.Dense(units=1, activation=activations.sigmoid)(h)
        super().__init__(x,y)
        self.compile(loss=losses.BinaryCrossentropy(),optimizer=optimizers.Adam(), metrics=['acc'])

class CNN(models.Model):
    def __init__(self, side = 100):
        x=layers.Input((side,side,1))
        h=layers.Conv2D(filters=3, kernel_size=(3,3),activation=activations.relu)(x)
        h=layers.MaxPooling2D(pool_size=(2,2))(h)
        h=layers.Dropout(rate=0.25)(h)
        h=layers.Flatten()(h)
        y=layers.Dense(units=1, activation=activations.sigmoid)(h)
        super().__init__(x,y)
        self.compile(loss=losses.BinaryCrossentropy(), optimizer=optimizers.Adam(), metrics=['acc'])

class NewsML():
    def __init__(self):
        self.Verbose:bool = True
        self.Dev:bool = True
        self.File = 'Test/NewsData'

        self.RnnEpoch:int = 10
        self.RnnBatch:int = 256
        self.RnnMaxLen:int = 100

        self.CnnEpoch:int = 10
        self.CnnBatch:int = 256
    
    def run(self):
        count = itertools.count(1)
        self.__info(next(count) + ' Prepare Data')
        self.Data = Data(file=self.File, max_len=self.RnnMaxLen ,verbose=self.Verbose, dev=self.Dev)

        self.__info(next(count) + ' Build RNN Model')
        self.Rnn = RNN(max_len=self.RnnMaxLen,data_count=len(self.Data.RnnX),max_features=20000)

        self.__info(next(count) + ' Build CNN Model')
        self.Cnn = CNN(side=self.Data.CnnSide)

        #self.__info(next(count) + ' Connect Tensorboard')
        #tb = TensorBoard(log_dir='./graph', histogram_freq=0, write_graph=True, write_images=True)

        self.__info(next(count) + ' Run RNN Model')
        self.RnnHistory = self.Rnn.fit(x=self.Data.RnnX, y=self.Data.RnnY, 
        batch_size=self.RnnBatch, epochs=self.RnnEpoch, validation_split=0.2, verbose=self.Verbose)

        self.__info(next(count) + ' Run CNN Model')
        self.CnnHistory = self.Cnn.fit(x=self.Data.CnnX, y=self.Data.CnnY, 
        batch_size=self.CnnBatch, epochs=self.CnnEpoch, validation_split=0.2, verbose=self.Verbose)

        self.__info(next(count) + ' Make Plot')
        self.__make_plot()

        self.__info(next(count) + ' Save History and Configuration as HTML')
        self.__save()

        self.__info('Done')

    def __make_plot(self):
        """
        Plot history for loss and accuracy of train and validation data.
        """
        fig, ((rnn_loss,cnn_loss),(rnn_acc, cnn_acc)) = plt.subplots(nrows=2, ncols=2, constrained_layout=True)

        rnn_loss.plot(self.RnnHistory.history['loss'], 'y', label='train loss')
        rnn_loss.plot(self.RnnHistory.history['val_loss'], 'r', label='val loss')
        rnn_acc.plot(self.RnnHistory.history['acc'], 'b', label='train acc')
        rnn_acc.plot(self.RnnHistory.history['val_acc'], 'g', label='val acc')
        cnn_loss.plot(self.CnnHistory.history['loss'], 'y', label='train loss')
        cnn_loss.plot(self.CnnHistory.history['val_loss'], 'r', label='val loss')
        cnn_acc.plot(self.CnnHistory.history['acc'], 'b', label='train acc')
        cnn_acc.plot(self.CnnHistory.history['val_acc'], 'g', label='val acc')

        rnn_loss.set_xlabel('epoch')
        rnn_acc.set_xlabel('epoch')
        cnn_loss.set_xlabel('epoch')
        cnn_acc.set_xlabel('epoch')

        rnn_loss.set_ylabel('loss')
        rnn_acc.set_ylabel('accuray')
        cnn_loss.set_ylabel('loss')
        cnn_acc.set_ylabel('accuray')

        rnn_loss.title.set_text('RNN Loss')
        rnn_acc.title.set_text('RNN Accuracy')
        cnn_loss.title.set_text('CNN Loss')
        cnn_acc.title.set_text('CNN Accuracy')

        self.Fig = fig

    def open_tensorboard(self):
        pass

    def __save(self):
        n = datetime.now()
        os.makedirs(f'./result/{n}')

        self.Fig.savefig(f'./result/{n}/plot.png', dpi=1000)

        self.Rnn.save(f'./result/{n}/rnn_model.h5')
        self.Cnn.save(f'./result/{n}/cnn_model.h5')

        basic="""
        <html>
        <body>
        
        <h1>Machine Learning Result</h1>
        <div class="datetime">Date and Time : </div>
        
        <h2>Environment</h2>
        <div class="sys_info">System Info : </div>
        <div class="py_version">Python Version : </div>
        <div class="keras_backend">Keras Backend : </div>
        
        <h2>RNN Configuration</h2>
        <div class="rnn_epoch">Epoch : </div>
        <div class="rnn_batch">Batch Size : </div>
        <div class="rnn_model"></div>
        
        <h2>CNN Configuration</h2>
        <div class="cnn_epoch">Epoch : </div>
        <div class="cnn_batch">Batch Size : </div>
        <div class="cnn_model"></div>
        
        <h2>Plot<h2>
        <img src="plot.png" alt="plt" height="400" width="600">

        </body>
        </html>
        """
        soup = BeautifulSoup(basic,'html.parser')
        soup.html.body.find('div', attrs={'class': 'datetime'}).append(str(n))
        soup.html.body.find('div', attrs={'class': 'sys_info'}).append(str(platform.platform()))
        soup.html.body.find('div', attrs={'class': 'py_version'}).append(str(sys.version_info))
        soup.html.body.find('div', attrs={'class': 'keras_backend'}).append(K.backend())

        soup.html.body.find('div', attrs={'class': 'rnn_epoch'}).append(str(self.RnnEpoch))
        soup.html.body.find('div', attrs={'class': 'rnn_batch'}).append(str(self.RnnBatch))
        self.Rnn.summary(print_fn=lambda x: self.__to_html(soup,'rnn_model',x))

        soup.html.body.find('div', attrs={'class': 'cnn_epoch'}).append(str(self.CnnEpoch))
        soup.html.body.find('div', attrs={'class': 'cnn_batch'}).append(str(self.CnnBatch))
        self.Rnn.summary(print_fn=lambda x: self.__to_html(soup,'cnn_model',x))

        soup.prettify()
        with open(f'./result/{n}/result.html',mode='w') as f:
            f.write(str(soup))

    def __to_html(self, soup:BeautifulSoup, class_:str , x:str):
        soup.html.body.find('div', attrs={'class': class_}).append(x)
        soup.html.body.find('div', attrs={'class': class_}).append(soup.new_tag('br'))

    def show_plot(self):
        plt.show()

    @staticmethod
    def __info(msg):
        print('\n\033[35m'+msg+'\033[0m')

class NewsMLHistory():
    pass    

if __name__ == '__main__':
    ml = NewsML()
    for item in sys.argv:
        eq = item.find('=')
        if eq==-1:
            continue

        elif item[:eq] == 'file':
            ml.File = item[(eq+1):]

        elif item[:eq] == 'dev':
            if item[(eq+1):]=='true':
                ml.Dev = True
            elif item[(eq+1):]=='false':
                ml.Dev = False
            else:
                raise ValueError()
        
        elif item[:eq] == 'verbose':
            if item[(eq+1):]=='true':
                ml.Verbose = True
            elif item[(eq+1):]=='false':
                ml.Verbose = False
            else:
                raise ValueError()
    ml.run()
    #ml.show_plot()
    while True:
        pass
