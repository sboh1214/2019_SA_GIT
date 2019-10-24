import itertools
import matplotlib.pyplot as plt
from keras import layers, models, losses, optimizers, activations
from keras.preprocessing.text import Tokenizer
from keras.callbacks import TensorBoard
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

    def __get_news_data(self, filename: str = 'NewsData'):
        """

        """
        self.__info('\nImport News List')
        news_list = NewsList().importPickle(filename)
        if self.Verbose:
            print(news_list[0])
        print(f'{len(news_list)} News Imported')
        if self.Dev == True:
            news_list = news_list[:100]
        print(f'{len(news_list)} News will be used')

        self.__info('\nAnalyze Data')
        max_sentence = 0
        for i in news_list:
            if max_sentence<len(i.Content):
                max_sentence = len(i.Content)
        self.CnnSide = max_sentence
        print(f'Maximum Sentences Count : {max_sentence}')

        self.__info('\nBuild Data : RnnX, RnnY, CnnX, CnnY')
        for news in tqdm(news_list):
            self.RnnX.extend(self.__clean(news.Content))
            self.RnnY.extend(news.Sentence_Bias)
            length = ceil(sqrt(len(news.Sentence_Bias)))
            self.CnnX.append(self.__square(news.Sentence_Bias, max_sentence))
            self.CnnY.append(news.Bias)
        if self.Verbose:
            self.__info(f'Rnn X ({len(self.RnnX)})')
            print(str(self.RnnX[0])[:80])
            self.__info(f'Rnn Y ({len(self.RnnY)})')
            print(self.RnnY[0])
            self.__info(f'Cnn X ({len(self.CnnX)})')
            print(str(self.CnnX[0])[:80])
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
            print(str(self.RnnX[0])[:80])

class RNN(models.Model):
    def __init__(self, max_len , data_count, max_features=20000):
        x=layers.Input((max_len, ))
        h=layers.Embedding(max_features, 128)(x)
        h=layers.LSTM(128, dropout=0.2, recurrent_dropout= 0.2)(h)
        y=layers.Dense(units=1, activation=activations.sigmoid)(h)
        super().__init__(x,y)
        self.compile(loss=losses.BinaryCrossentropy(),optimizer=optimizers.Adam(), metrics=['acc'])

class CNN(models.Model):
    def __init__(self, side = 100):
        x=layers.Conv2D(filters=3, kernel_size=(3,3),activation=activations.relu, input_shape=(1,side,side))
        h=layers.MaxPooling2D(pool_size=(2,2))(x)
        h=layers.Dropout(rate=0.25)(h)
        h=layers.Flatten()(h)
        y=layers.Dense(units=1, activation=activations.sigmoid)(h)
        super().__init__(x,y)
        self.compile(loss=losses.BinaryCrossentropy(), optimizer=optimizers.Adam(), metrics=['acc'])

class NewsML():
    def __init__(self, rnn_maxlen=100 ,verbose=False, file='Test/NewsData', dev=False):
        self.Verbose = verbose
        self.RnnMaxLen = rnn_maxlen
        count = itertools.count(1)
        
        self.__info(f'[{next(count)}] Prepare Data')
        self.Data = Data(file=file, max_len=rnn_maxlen ,verbose=self.Verbose, dev=dev)

        self.__info(f'[{next(count)}] Build RNN Model')
        self.Rnn = RNN(max_len=self.RnnMaxLen,data_count=len(self.Data.RnnX),max_features=20000)

        self.__info(f'[{next(count)}] Build CNN Model')
        self.Cnn = CNN(side=self.Data.CnnSide)

        self.__info(f'[{next(count)}] Connect Tensorboard')
        tb = TensorBoard(log_dir='./graph', histogram_freq=0, write_graph=True, write_images=True)

        self.__info(f'[{next(count)}] Run RNN Model')
        self.RnnHistory = self.Rnn.fit(x=self.Data.RnnX, y=self.Data.RnnY, batch_size=256, epochs=10, validation_split=0.2, verbose=self.Verbose, callbacks=[tb])

        self.__info(f'[{next(count)}] Run CNN Model')
        self.CnnHistory = self.Cnn.fit(x=self.Data.CnnX, y=self.Data.CnnY, batch_size=256, epochs=10, validation_split=0.2, verbose=self.Verbose, callbacks=[tb])

    def plot_loss_and_accuracy(self, name="", show=False):
        """
        Plot history for loss and accuracy of train and validation data.
        """
        fig, loss_ax = plt.subplots()

        acc_ax = loss_ax.twinx()

        loss_ax.plot(self.RnnHistory.history['loss'], 'y', label='train loss')
        loss_ax.plot(self.RnnHistory.history['val_loss'], 'r', label='val loss')

        acc_ax.plot(self.RnnHistory.history['acc'], 'b', label='train acc')
        acc_ax.plot(self.RnnHistory.history['val_acc'], 'g', label='val acc')

        loss_ax.set_xlabel('epoch')
        loss_ax.set_ylabel('loss')
        acc_ax.set_ylabel('accuray')

        loss_ax.legend(loc='upper left')
        acc_ax.legend(loc='lower left')

        if show:
            plt.show()

    def open_tensorboard(self):
        pass

    @staticmethod
    def __info(msg):
        print('\n\033[35m'+msg+'\033[0m')
    

if __name__ == '__main__':
    ml = NewsML(verbose=True, file='Test/NewsData', dev=True)
    ml.plot_loss_and_accuracy(name='Test', show=True)
    input('Enter to Exit (Prevent stopping docker)')
