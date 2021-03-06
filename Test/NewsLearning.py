"""
Deprecated
"""
from itertools import count as iter_count
from datetime import datetime
from os import makedirs
from math import sqrt, ceil
from sys import argv, version_info
from platform import platform

import keras.backend as k
from keras import layers, models, losses, optimizers, activations
from keras.preprocessing.text import Tokenizer

import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
from bs4 import BeautifulSoup
from csv import writer

from data import NewsList


@DeprecationWarning
class Data:
    def __init__(self, file='NewsData_0_20000', verbose=False, max_len=100, divide=100000):
        self.Verbose = verbose
        self.MaxLen = max_len
        self.Divide = divide
        self.Tokenizer = Tokenizer(num_words=100000)
        self.get_news_data(file)

    @staticmethod
    def info(msg):
        print('\033[35m' + str(msg) + '\033[0m')

    @staticmethod
    def square(a, side):
        try:
            avg = sum(a) / len(a)
        except ZeroDivisionError:
            avg = 0
        output = [[avg] * side for _ in range(side)]
        for i, bias in enumerate(a):
            output[i // side][i % side] = bias
        return output

    @staticmethod
    def pad(a, max_len):
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

    @staticmethod
    def news_calibrate(news_list):
        for news in news_list:
            if news.Bias > 300:
                news.Bias = 300
            if news.Bias < -300:
                news.Bias = -300
            news.Bias = news.Bias / 150
        for news in news_list:
            for index, bias in enumerate(news.Sentence_Bias):
                if bias > 300:
                    news.Sentence_Bias[index] = 300
                if bias < -300:
                    news.Sentence_Bias[index] = -300
                news.Sentence_Bias[index] = bias / 150
        return news_list

    def get_news_data(self, filename):
        """

        """
        self.info('\nImport News List')
        news_list = NewsList().importPickle(filename)
        self.NewsList = news_list
        if self.Verbose:
            self.__print(news_list)
        print(str(len(news_list)) + ' News Imported')
        news_list = news_list[:self.Divide]
        print(str(len(news_list)) + ' News will be used')
        bias = [i.Bias for i in news_list]
        print('Maximum Bias : ' + str(max(bias)))
        print('Minimum Bias : ' + str(min(bias)))

        self.info('\nAnalyze Data')
        max_sentence = 0
        for i in news_list:
            if max_sentence < len(i.Content):
                max_sentence = len(i.Content)
        self.CnnSide = ceil(sqrt(max_sentence))
        print('Maximum Sentences Count : ' + str(max_sentence))

        self.info('\nCalibrating Data')
        news_list = self.news_calibrate(news_list)

        self.info('\nMake Array of Data')
        self.RnnX = []
        self.RnnY = []
        self.CnnX = []
        self.CnnY = []

        self.info('\nBuild Data : RnnX, RnnY, CnnX, CnnY')
        for news in tqdm(news_list):
            self.RnnX.extend(news.Content)
            self.RnnY.extend(news.Sentence_Bias)
            self.CnnX.append(self.square(news.Sentence_Bias, self.CnnSide))
            self.CnnY.append(news.Bias)

        if self.Verbose:
            self.info('Rnn X (' + str(len(self.RnnX)) + ')')
            self.__print(self.RnnX)
            self.info('Rnn Y (' + str(len(self.RnnY)) + ')')
            self.__print(self.RnnY)
            self.info('Cnn X (' + str(len(self.CnnX)) + ')')
            self.__print(self.CnnX)
            self.info('Cnn Y (' + str(len(self.CnnY)) + ')')
            self.__print(self.CnnY)

        self.info('\nPre-Process CnnX')
        cnnx = np.array(self.CnnX)
        cnnx = cnnx.reshape((len(cnnx), self.CnnSide, self.CnnSide, 1))
        self.CnnX = cnnx
        if self.Verbose:
            self.__print(self.CnnX)
        self.CnnY = np.array(self.CnnY)

        self.info('\nPre-Process RnnX')
        self.Tokenizer.fit_on_texts(self.RnnX)
        rnn_x_list = self.Tokenizer.texts_to_sequences(self.RnnX)
        for i in tqdm(rnn_x_list):
            self.pad(i, self.MaxLen)
        rnn_x_array = np.array([self.pad(i, self.MaxLen) for i in rnn_x_list])
        self.RnnX = rnn_x_array
        if self.Verbose:
            self.__print(self.RnnX)
        self.RnnY = np.array(self.RnnY)


@DeprecationWarning
def rms(y_true, y_pred):
    diff = y_true - y_pred
    return k.sqrt(k.mean(k.square(diff)))


@DeprecationWarning
class RNN(models.Model):
    def __init__(self, max_len, max_features):
        x = layers.Input(shape=(max_len,))
        h = layers.Embedding(max_features, 100)(x)
        h = layers.Bidirectional(layers.LSTM(100, return_sequences=False))(h)
        h = layers.Dropout(rate=0.2)(h)
        h = layers.Dense(units=1)(h)
        y = layers.Dropout(rate=0.2)(h)
        super().__init__(x, y)
        self.compile(loss=losses.MeanSquaredError(), optimizer=optimizers.Adam(learning_rate=0.0001),
                     metrics=['binary_accuracy', rms])


@DeprecationWarning
class CNN(models.Model):
    def __init__(self, side=100):
        x = layers.Input((side, side, 1))
        h = layers.Conv2D(filters=2, kernel_size=(2, 2))(x)
        h = layers.MaxPooling2D(pool_size=(2, 2))(h)
        h = layers.Dropout(rate=0.2)(h)
        h = layers.Flatten()(h)
        h = layers.Dense(units=1)(h)
        y = layers.Dropout(rate=0.2)(h)
        super().__init__(x, y)
        self.compile(loss=losses.MeanSquaredError(), optimizer=optimizers.Adam(learning_rate=0.001),
                     metrics=['binary_accuracy', rms])


@DeprecationWarning
class NewsML:
    def __init__(self):
        self.Verbose = True
        self.Dev = True
        self.File = 'NewsData_0_20000'

        self.RnnEpoch = 10
        self.RnnBatch = 64
        self.RnnMaxLen = 100

        self.CnnEpoch = 10
        self.CnnBatch = 64
        self.Divide = 1000000

    def run(self):
        count = iter_count(1)
        self.__info(str(next(count)) + ' Prepare Data')
        self.Data = Data(file=self.File, max_len=self.RnnMaxLen, verbose=self.Verbose, divide=self.Divide)

        self.__info(str(next(count)) + ' Build RNN Model')
        self.Rnn = RNN(max_len=self.RnnMaxLen, max_features=100000)

        self.__info(str(next(count)) + ' Build CNN Model')
        self.Cnn = CNN(side=self.Data.CnnSide)

        self.__info(str(next(count)) + ' Run RNN Model')
        self.RnnHistory = self.Rnn.fit(x=self.Data.RnnX, y=self.Data.RnnY,
                                       batch_size=self.RnnBatch, epochs=self.RnnEpoch, validation_split=0.2,
                                       verbose=self.Verbose)

        self.__info(str(next(count)) + ' Run CNN Model')
        self.CnnHistory = self.Cnn.fit(x=self.Data.CnnX, y=self.Data.CnnY,
                                       batch_size=self.CnnBatch, epochs=self.CnnEpoch, validation_split=0.2,
                                       verbose=self.Verbose)

        self.__info(str(next(count)) + ' Predict')
        self.PredictX = [814219, 42159, 141318, 48937, 248414]
        self.PredictY = []
        for item in self.PredictX:
            input = np.expand_dims(np.array(self.Data.CnnX[item]), axis=0)
            self.PredictY.append(self.Cnn.predict(input))

        self.__info(str(next(count)) + ' Make Plot')
        # self.__make_plot()

        self.__info(str(next(count)) + ' Save History and Configuration as HTML')
        self.__save()

        self.__info('Done')

    def __make_plot(self):
        """
        Plot history for loss and accuracy of train and validation data.
        """
        fig, ((rnn_loss, cnn_loss), (rnn_acc, cnn_acc)) = plt.subplots(nrows=2, ncols=2, constrained_layout=True)

        rnn_loss.plot(self.RnnHistory.history['binary_accuracy'], 'y', label='train bin acc')
        rnn_loss.plot(self.RnnHistory.history['val_binary_accuracy'], 'r', label='val bin acc')
        rnn_acc.plot(self.RnnHistory.history['rms'], 'b', label='train rms')
        rnn_acc.plot(self.RnnHistory.history['val_rms'], 'g', label='val rms')
        cnn_loss.plot(self.CnnHistory.history['binary_accuracy'], 'y', label='train bin acc')
        cnn_loss.plot(self.CnnHistory.history['val_binary_accuracy'], 'r', label='val bin acc')
        cnn_acc.plot(self.CnnHistory.history['rms'], 'b', label='train rms')
        cnn_acc.plot(self.CnnHistory.history['val_rms'], 'g', label='val rms')

        rnn_loss.set_xlabel('epoch')
        rnn_acc.set_xlabel('epoch')
        cnn_loss.set_xlabel('epoch')
        cnn_acc.set_xlabel('epoch')

        rnn_loss.set_ylabel('loss')
        rnn_acc.set_ylabel('RMSD')
        cnn_loss.set_ylabel('loss')
        cnn_acc.set_ylabel('RMSD')

        rnn_loss.title.set_text('RNN Loss')
        rnn_acc.title.set_text('RNN RMSD')
        cnn_loss.title.set_text('CNN Loss')
        cnn_acc.title.set_text('CNN RMSD')

        self.Fig = fig

    def __save(self):
        n = str(datetime.now())
        makedirs('./result/' + n)

        # self.Fig.savefig('./result/' + n + '/plot.png', dpi=1000)
        #
        # self.Rnn.save('./result/' + n + '/rnn_model.h5')
        # self.Cnn.save('./result/' + n + '/cnn_model.h5')
        #
        # history = [self.RnnHistory.history['loss'],
        #            self.RnnHistory.history['val_loss'],
        #            self.RnnHistory.history['binary_accuracy'],
        #            self.RnnHistory.history['val_binary_accuracy'],
        #            self.RnnHistory.history['rms'],
        #            self.RnnHistory.history['val_rms'],
        #            self.CnnHistory.history['loss'],
        #            self.CnnHistory.history['val_loss'],
        #            self.CnnHistory.history['binary_accuracy'],
        #            self.CnnHistory.history['val_binary_accuracy'],
        #            self.CnnHistory.history['rms'],
        #            self.CnnHistory.history['val_rms']]
        # with open('./result/' + n + '/history.csv', mode='w') as f:
        #     csv = writer(f)
        #     for line in history:
        #         csv.writerow(line)

        with open('./result/' + n + '/predict.csv', mode='w') as f:
            csv = writer(f)
            for line in self.PredictY:
                csv.writerow(line)
            for index in self.PredictX:
                csv.writerow(self.Data.NewsList[index].Title)
            for index in self.PredictY:
                csv.writerow(self.Data.NewsList[index].Bias)

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
        soup.html.body.find('div', attrs={'class': 'sys_info'}).append(str(platform()))
        soup.html.body.find('div', attrs={'class': 'py_version'}).append(str(version_info))

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
    for item in argv:
        eq = item.find('=')
        if eq == -1:
            continue

        elif item[:eq] == 'file':
            ml.File = item[(eq + 1):]

        elif item[:eq] == 'verbose':
            if item[(eq + 1):] == 'true':
                ml.Verbose = True
            elif item[(eq + 1):] == 'false':
                ml.Verbose = False
            else:
                raise ValueError()

        elif item[:eq] == 'divide':
            ml.Divide = int(item[(eq + 1):])

        elif item[:eq] == 'cnnepoch':
            ml.CnnEpoch = int(item[(eq + 1):])

        elif item[:eq] == 'rnnepoch':
            ml.RnnEpoch = int(item[(eq + 1):])

        elif item[:eq] == 'cnnbatch':
            ml.CnnBatch = int(item[(eq + 1):])

        elif item[:eq] == 'rnnbatch':
            ml.RnnBatch = int(item[(eq + 1):])
    ml.run()
    # ml.show_plot()
