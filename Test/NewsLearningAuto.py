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
from multiprocessing.dummy import Pool

from keras import layers, models, losses, optimizers, activations, Sequential
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

    def __init__(self, file='NewsData0_20000', verbose=False, max_len=100, dev=False):
        self.Verbose = verbose
        self.MaxLen = max_len
        self.Dev = dev
        self.Divide = 1000000
        self.__get_news_data(filename=file)

    @staticmethod
    def __info(msg):
        print('\033[35m' + str(msg) + '\033[0m')

    @staticmethod
    def __square(a, side):
        output = [[0] * side for _ in range(side)]
        for i, bias in enumerate(a):
            output[i // side][i % side] = bias
        return output

    @staticmethod
    def __pad(a, max_len):
        if len(a) == max_len:
            return a
        elif len(a) > max_len:
            return a[0:max_len]
        else:
            a.extend([0 for _ in range(max_len - len(a))])
            return a

    @staticmethod
    def __print(a):
        print(str(a[0])[:80])
        print(str(a[1])[:80])
        print(str(a[2])[:80])

    def __get_news_data(self, filename):
        """

        """
        self.__info('\nImport News List')
        news_list = NewsList().importPickle(filename)
        if self.Verbose:
            self.__print(news_list)
        print(str(len(news_list)) + ' News Imported')
        if self.Dev:
            news_list = news_list[:self.Divide]
        print(str(len(news_list)) + ' News will be used')
        bias = [i.Bias for i in news_list]
        print('Maximum Bias : ' + str(max(bias)))
        print('Minimum Bias : ' + str(min(bias)))

        self.__info('\nAnalyze Data')
        max_sentence = 0
        for i in news_list:
            if max_sentence < len(i.Content):
                max_sentence = len(i.Content)
        self.CnnSide = ceil(sqrt(max_sentence))
        print('Maximum Sentences Count : ' + str(max_sentence))

        self.__info('\nMake Array of Data')
        self.RnnX = []
        self.RnnY = []
        self.CnnX = []
        self.CnnY = []

        self.__info('\nBuild Data : RnnX, RnnY, CnnX, CnnY')
        for news in tqdm(news_list):
            self.RnnX.extend(news.Content)
            self.RnnY.extend(news.Sentence_Bias)
            self.CnnX.append(self.__square(news.Sentence_Bias, self.CnnSide))
            self.CnnY.append(news.Bias)

        if self.Verbose:
            self.__info('Rnn X (' + str(len(self.RnnX)) + ')')
            self.__print(self.RnnX)
            self.__info('Rnn Y (' + str(len(self.RnnY)) + ')')
            self.__print(self.RnnY)
            self.__info('Cnn X (' + str(len(self.CnnX)) + ')')
            self.__print(self.CnnX)
            self.__info('Cnn Y (' + str(len(self.CnnY)) + ')')
            self.__print(self.CnnY)

        self.__info('\nPre-Process CnnX')
        cnnx = np.array(self.CnnX)
        cnnx = cnnx.reshape((len(cnnx), self.CnnSide, self.CnnSide, 1))
        self.CnnX = cnnx
        if self.Verbose:
            self.__print(self.CnnX)

        self.__info('\nPre-Process RnnX')
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(self.RnnX)
        rnn_x_list = tokenizer.texts_to_sequences(self.RnnX)
        for i in tqdm(rnn_x_list):
            self.__pad(i, self.MaxLen)
        rnn_x_array = np.array([self.__pad(i, self.MaxLen) for i in rnn_x_list])
        self.RnnX = rnn_x_array
        if self.Verbose:
            self.__print(self.RnnX)


class RNN(models.Model):
    def __init__(self, max_len, data_count, max_features=20000):
        x = layers.Input(shape=(max_len,))
        h = layers.Embedding(max_features, 128)(x)
        h = layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2)(h)
        y = layers.Dense(units=1, activation=activations.sigmoid)(h)
        super().__init__(x, y)
        self.compile(loss=losses.BinaryCrossentropy(), optimizer=optimizers.Adam(), metrics=['acc'])


class CNN(models.Model):
    def __init__(self, side=100):
        x = layers.Input((side, side, 1))
        h = layers.Conv2D(filters=3, kernel_size=(3, 3), activation=activations.relu)(x)
        h = layers.MaxPooling2D(pool_size=(2, 2))(h)
        h = layers.Dropout(rate=0.25)(h)
        h = layers.Flatten()(h)
        y = layers.Dense(units=1, activation=activations.sigmoid)(h)
        super().__init__(x, y)
        self.compile(loss=losses.BinaryCrossentropy(), optimizer=optimizers.Adam(), metrics=['acc'])


class NewsML:
    def __init__(self):
        self.Verbose = True
        self.Dev = True
        self.File = 'NewsData0_20000'

        self.RnnEpoch = 10
        self.RnnBatch = 256
        self.RnnMaxLen = 100

        self.CnnEpoch = 10
        self.CnnBatch = 256

    def rnn_model(self, max_len, max_features):
        model = Sequential([
            layers.Input(shape=(max_len,)),
            layers.Embedding(max_features, 128),
            layers.CuDNNLSTM(128, return_sequences=False),
            layers.Dropout(rate=0.2),
            layers.Dense(units=1, activation=None)
        ])
        model.compile(optimizer=optimizers.Adam(learning_rate=0.001), loss=losses.MeanSquaredError())

        self.RnnHistory = model.fit(self.Data.CnnX, self.Data.CnnY,
                        batch_size=self.RnnBatch,
                        epochs=self.RnnEpoch,
                        validation_split=0.2,
                        verbose=self.Verbose)

        return self.RnnHistory, model

    def cnn_model(self, x_train, y_train, x_val, y_val, params):
        model = Sequential()
        model.add(Dense(32, input_dim=4, activation=params['activation']))
        model.add(Dense(3, activation='softmax'))
        model.compile(optimizer=params['optimizer'], loss=params['losses'])

        out = model.fit(x_train, y_train,
                        batch_size=params['batch_size'],
                        epochs=params['epochs'],
                        validation_data=[x_val, y_val],
                        verbose=0)

        return out, model

    def run(self):
        count = itertools.count(1)
        self.__info(str(next(count)) + ' Prepare Data')
        self.Data = Data(file=self.File, max_len=self.RnnMaxLen, verbose=self.Verbose, dev=self.Dev)

        self.__info(str(next(count)) + ' Build RNN Model')
        self.Rnn = RNN(max_len=self.RnnMaxLen, data_count=len(self.Data.RnnX), max_features=20000)

        self.__info(str(next(count)) + ' Build CNN Model')
        self.Cnn = CNN(side=self.Data.CnnSide)

        # self.__info(str(next(count)) + ' Connect Tensor board')
        # tb = TensorBoard(log_dir='./graph', histogram_freq=0, write_graph=True, write_images=True)

        self.__info(str(next(count)) + ' Run RNN Model')
        self.RnnHistory = self.Rnn.fit(x=self.Data.RnnX, y=self.Data.RnnY,
                                       batch_size=self.RnnBatch, epochs=self.RnnEpoch, validation_split=0.2,
                                       verbose=self.Verbose)

        self.__info(str(next(count)) + ' Run CNN Model')
        self.CnnHistory = self.Cnn.fit(x=self.Data.CnnX, y=self.Data.CnnY,
                                       batch_size=self.CnnBatch, epochs=self.CnnEpoch, validation_split=0.2,
                                       verbose=self.Verbose)

        self.__info(str(next(count)) + ' Make Plot')
        self.__make_plot()

        self.__info(str(next(count)) + ' Save History and Configuration as HTML')
        self.__save()

        self.__info('Done')

    def __make_plot(self):
        """
        Plot history for loss and accuracy of train and validation data.
        """
        fig, ((rnn_loss, cnn_loss), (rnn_acc, cnn_acc)) = plt.subplots(nrows=2, ncols=2, constrained_layout=True)

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
        n = str(datetime.now())
        os.makedirs('./result/' + n)

        self.Fig.savefig('./result/' + n + '/plot.png', dpi=1000)

        self.Rnn.save('./result/' + n + '/rnn_model.h5')
        self.Cnn.save('./result/' + n + '/cnn_model.h5')

        basic = """
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
        soup = BeautifulSoup(basic, 'html.parser')
        soup.html.body.find('div', attrs={'class': 'datetime'}).append(str(n))
        soup.html.body.find('div', attrs={'class': 'sys_info'}).append(str(platform.platform()))
        soup.html.body.find('div', attrs={'class': 'py_version'}).append(str(sys.version_info))
        soup.html.body.find('div', attrs={'class': 'keras_backend'}).append(K.backend())

        soup.html.body.find('div', attrs={'class': 'rnn_epoch'}).append(str(self.RnnEpoch))
        soup.html.body.find('div', attrs={'class': 'rnn_batch'}).append(str(self.RnnBatch))
        self.Rnn.summary(print_fn=lambda x: self.__to_html(soup, 'rnn_model', x))

        soup.html.body.find('div', attrs={'class': 'cnn_epoch'}).append(str(self.CnnEpoch))
        soup.html.body.find('div', attrs={'class': 'cnn_batch'}).append(str(self.CnnBatch))
        self.Rnn.summary(print_fn=lambda x: self.__to_html(soup, 'cnn_model', x))

        soup.prettify()
        with open('./result/' + n + '/result.html', mode='w') as f:
            f.write(str(soup))

    @staticmethod
    def __to_html(soup: BeautifulSoup, class_: str, x: str):
        soup.html.body.find('div', attrs={'class': class_}).append(x)
        soup.html.body.find('div', attrs={'class': class_}).append(soup.new_tag('br'))

    @staticmethod
    def show_plot():
        plt.show()

    @staticmethod
    def __info(msg):
        print('\n\033[35m' + msg + '\033[0m')


if __name__ == '__main__':
    ml = NewsML()
    for item in sys.argv:
        eq = item.find('=')
        if eq == -1:
            continue

        elif item[:eq] == 'file':
            ml.File = item[(eq + 1):]

        elif item[:eq] == 'dev':
            if item[(eq + 1):] == 'true':
                ml.Dev = True
            elif item[(eq + 1):] == 'false':
                ml.Dev = False
            else:
                raise ValueError()

        elif item[:eq] == 'verbose':
            if item[(eq + 1):] == 'true':
                ml.Verbose = True
            elif item[(eq + 1):] == 'false':
                ml.Verbose = False
            else:
                raise ValueError()

        elif item[:eq] == 'divide':
            ml.Divide = int(item[(eq + 1):])
    ml.run()
    # ml.show_plot()