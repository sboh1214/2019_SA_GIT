import itertools
import matplotlib.pyplot as plt
from keras import layers, models
from keras.preprocessing.text import Tokenizer
from tqdm import tqdm
from math import sqrt, ceil
from numpy import reshape
import numpy as np

from data import NewsList

'''
from khaiii import KhaiiiApi
class MorphAnalyzer:
    """
    
    """
    @classmethod
    def getMorph(cls, sentence):
        """
        >>> MorphAnalyzer.getMorph()
        {'안녕': 'IC', ',': 'SP', '세상': 'NNG'}
        """
        api = KhaiiiApi()
        dic = {}
        for word in api.analyze(sentence):
            for morph in word.morphs:
                dic[morph.lex] = morph.tag
        return dic
'''


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

    def __init__(self, file, verbose=False, max_len=100):
        self.Verbose = verbose
        self.MaxLen = max_len
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
    def __square(a):
        output = []
        length = ceil(sqrt(len(a)))
        while True:
            if len(a)>length:
                output.append([a.pop() for _ in range(length)])
            elif len(a)==length:
                output.append([a.pop() for _ in range(length)])
                return output
            else:
                output.append(a.extend([0 for _ in range(length-len(a))]))
                return output

    @staticmethod
    def __pad(a, max_len):
        if len(a)==max_len:
            return a
        elif len(a)>max_len:
            return a[0:len(a)]
        else:
            return a.extend([0 for _ in range(max_len-len(a))])

    def __get_news_data(self, filename: str = 'NewsData'):
        """

        """
        self.__info('\nImport News List')
        news_list = NewsList().importPickle(filename)
        if self.Verbose:
            print(news_list[0])
        print(f'{len(news_list)} News Imported')

        self.__info('\nBuild Data : RnnX, RnnY, CnnX, CnnY')
        for news in tqdm(news_list):
            self.RnnX.extend(self.__clean(news.Content))
            self.RnnY.extend(news.Sentence_Bias)
            length = ceil(sqrt(len(news.Sentence_Bias)))
            #self.CnnX.append(self.__square(news.Sentence_Bias))
            self.CnnX.append(news.Sentence_Bias)
            self.CnnY.append(news.Bias)
        if self.Verbose:
            self.__info(f'Rnn X ({len(self.RnnX)})')
            print(self.RnnX[0])
            self.__info(f'Rnn Y ({len(self.RnnY)})')
            print(self.RnnY[0])
            self.__info(f'Cnn X ({len(self.CnnX)})')
            print(self.CnnX[0])
            self.__info(f'Cnn Y ({len(self.CnnY)})')
            print(self.CnnY[0])

        self.__info('\nPre-Process RnnX')
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(self.RnnX)
        rnnXlist = tokenizer.texts_to_sequences(self.RnnX)
        for i in tqdm(rnnXlist):
            self.__pad(i, self.MaxLen)
        rnnXarray=np.array([self.__pad(i, self.MaxLen) for i in rnnXlist])
        self.RnnX = rnnXarray
        if self.Verbose:
            print(self.RnnX[0])

class RNN(models.Model):
    def __init__(self, max_len , data_count, max_features=20000):
        x=layers.Input((max_len, ))
        h=layers.Embedding(max_features, 128)(x)
        h=layers.LSTM(128, dropout=0.2, recurrent_dropout= 0.2)(h)
        y=layers.Dense(units=1, activation='sigmoid')(h)
        super().__init__(x,y)
        self.compile(loss='binary_crossentropy',optimizer='adam', metrics=['accuracy'])

class CNN(models.Model):
    def __init__(self, input_shape):
        x=layers.Input(shape=input_shape)
        h=layers.Conv2D(filters=3, kernel_size=(3,3),activation='relu',input_shape=input_shape)(x)
        h=layers.MaxPooling2D()(h)
        h=layers.Dropout(rate=0.25)(h)
        h=layers.Flatten()(h)
        y=layers.Dense(units=1, activation='sigmoid')(h)
        super().__init__(x,y)
        self.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

class NewsML():
    def __init__(self, rnn_maxlen=100 ,verbose=False):
        self.Verbose = verbose
        self.RnnMaxLen = rnn_maxlen
        count = itertools.count(1)
        
        self.__info(f'[{next(count)}] Prepare Data')
        self.Data = Data(file='NewsData', max_len=rnn_maxlen ,verbose=self.Verbose)

        self.__info(f'[{next(count)}] Build RNN Model')
        self.Rnn = RNN(max_len=self.RnnMaxLen,data_count=len(self.Data.RnnX),max_features=20000)

        self.__info(f'[{next(count)}] Build CNN Model')
        #self.Cnn = CNN()

        self.__info(f'[{next(count)}] Run RNN Model')
        self.RnnHistory = self.Rnn.fit(x=self.Data.RnnX, y=self.Data.RnnY, batch_size=256, epochs=5, validation_split=0.2, verbose=self.Verbose)

        self.__info(f'[{next(count)}] Run CNN Model')
        #self.CnnHistory = self.Cnn.fit(x=self.Data.CnnX, y=self.Data.CnnY, batch_size=128, epochs=5, validation_split=0.2, verbose=self.Verbose)

    def plot_loss_and_accuracy(self, name="", show=False):
        """
        Plot history for loss and accuracy of train and validation data.
        """
        plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(self.RnnHistory.history['loss'])
        plt.plot(self.RnnHistory.history['val_loss'])
        plt.title(name + " RNN Loss")
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(['Train', 'Validation'], loc=0)

        # plt.subplot(2, 1, 2)
        # plt.plot(self.RnnHistory.history['acc'])
        # plt.plot(self.RnnHistory.history['val_acc'])
        # plt.title(name + " RNN Accuracy")
        # plt.xlabel('Epoch')
        # plt.ylabel('Accuracy')
        # plt.legend(['Train', 'Test'], loc=0)

        if show:
            plt.show()

    @staticmethod
    def __info(msg):
        print('\n\033[35m'+msg+'\033[0m')
    

if __name__ == '__main__':
    ml = NewsML(verbose=True)
    ml.plot_loss_and_accuracy(name='Test', show=True)