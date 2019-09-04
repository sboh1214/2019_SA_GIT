import csv
import os
import warnings

import matplotlib.pyplot as plt
from keras import layers, Model
from khaiii import KhaiiiApi
from tqdm import tqdm

warnings.filterwarnings('ignore')


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
    Title = []
    Press = []
    Date = []
    Content = []

    X_Train = None
    Y_Train = None
    X_Evaluate = None
    Y_Evaluate = None
    X_Test = None
    Y_Test = None
    Model = None

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

    @staticmethod
    def buildRNNModel(maxlen, maxfeatures):
        """

        """
        x = layers.Input(shape=(maxlen,))
        h = layers.Embedding(input_dim=maxfeatures, output_dim=128)(x)
        h = layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2)(h)
        y = layers.Dense(1, activation='sigmoid')(h)
        model = Model(x, y)
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    @staticmethod
    def buildCnnModel():
        x = layers.Input()
        y = layers.Dense(1, activation='sigmoid')(x)
        model = Model(x,y)
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

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
    print(MorphAnalyzer.getMorph("올바른 국정교과서"))
