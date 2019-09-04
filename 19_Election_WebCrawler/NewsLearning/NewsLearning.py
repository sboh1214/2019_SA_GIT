import csv
import os

import matplotlib.pyplot as plt
from keras import Sequential
from keras.layers import *
from khaiii import KhaiiiApi
from tqdm import tqdm


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


class NewsML:
    """

    """

    X_Train = None
    Y_Train = None
    X_Evaluate = None
    Y_Evaluate = None
    X_Test = None
    Y_Test = None
    Rnn_Model = None
    Cnn_Model = None

    plaidml = "plaidml.keras.backend"
    tensorflow = "tensorflow"
    theano = "theano"
    ctnk = "ctnk"

    def __init__(self, backend):
        if backend is self.plaidml:
            os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
        else:
            os.environ["KERAS_BACKEND"] = backend
        super().__init__()

    def getNewsData(self, filename):
        """

        """
        f = open(filename + '.csv', 'r', encoding='utf-8')
        rdr = csv.reader(f)
        for line in tqdm(rdr):
            self.Title.append(line['Title'])
            self.Press.append(line['Press'])
            self.Date.append(line['Date'])
            self.Content.append(line['Content'])
        f.close()

    def buildRNNModel(self, maxlen, maxfeatures):
        """

        """
        model = Sequential()
        model.add(Input(shape=(maxlen,)))
        model.add(Embedding(input_dim=maxfeatures, output_dim=128))
        model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
        model.add(Dense(1, activation='sigmoid'))
        model.add(Dropout(0.5))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.Rnn_Model = model

    def buildCnnModel(self, input_shape=None):
        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=input_shape))
        model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPool2D(pool_size=(2, 2)))
        model.add(Dropout(rate=0.25))
        model.add(Flatten())
        model.add(Dense(units=128, activation='relu'))
        model.add(Dropout(rate=0.5))
        model.add(Dense(units=1, activation='activation'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.Cnn_Model = model

    @staticmethod
    def plotLoss(history, name="", figure=1, subplot=(1, 1, 1), show=False):
        """
        Plot history for loss of train and validation data.
        """
        plt.figure(figure)
        plt.subplot(subplot)
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title(name + " Loss")
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(['Train', 'Test'], loc=0)
        if show:
            plt.show()

    @staticmethod
    def plotAccuracy(history, name="", figure=1, subplot=(1, 1, 1), show=False):
        """
        Plot history for accuracy of train and validation data.
        """
        plt.figure(figure)
        plt.subplot(subplot)
        plt.plot(history.history['acc'])
        plt.plot(history.history['val_acc'])
        plt.title(name + " Accuracy")
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend(['Train', 'Test'], loc=0)
        if show:
            plt.show()


if __name__ == "__main__":
    print(MorphAnalyzer.getMorph("미친전세값"))
