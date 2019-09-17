import os

import matplotlib.pyplot as plt
from keras import Sequential
from keras.layers import *
from khaiii import KhaiiiApi

from Test.data import NewsList


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
    NewsList = []
    X_Train = None
    Y_Train = None
    X_Validate = None
    Y_Validate = None
    X_Test = None
    Y_Test = None
    Rnn_Model = None
    Cnn_Model = None
    History = None

    PLAIDML: str = "plaidml.keras.backend"
    TENSORFLOW: str = "tensorflow"
    THEANO: str = "theano"
    CTNK: str = "ctnk"

    def __init__(self, backend):
        super().__init__()
        if backend is self.PLAIDML:
            os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
        else:
            os.environ["KERAS_BACKEND"] = backend

    def getNewsData(self, filename: str):
        """

        """
        news = NewsList()
        self.NewsList = news.importPickle(filename)

    def buildRNNModel(self, max_length: int, max_features: int):
        """

        """
        model = Sequential()
        model.add(Input(shape=(max_length,)))
        model.add(Embedding(input_dim=max_features, output_dim=128))
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

    def runRnnModel(self, epochs: int = 1, batch_size: int = 10):
        self.Rnn_Model.fit(x=self.X_Train, y=self.Y_Train,
                           batch_size=batch_size,
                           epochs=epochs,
                           validation_data=(self.X_Validate, self.Y_Validate))

    def runCnnModel(self, epochs: int = 1, batch_size: int = 10):
        self.Cnn_Model.fit(x=None, y=None,
                           batch_size=batch_size,
                           epochs=epochs,
                           validation_data=(None, None))

    def plotLossAndAccuracy(self, name="", show=False):
        """
        Plot history for loss and accuracy of train and validation data.
        """
        plt.figure()
        plt.subplot((2, 1, 1))
        plt.plot(self.History.history['loss'])
        plt.plot(self.History.history['val_loss'])
        plt.title(name + " Loss")
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(['Train', 'Test'], loc=0)

        plt.subplot((2, 1, 2))
        plt.plot(self.History.history['acc'])
        plt.plot(self.History.history['val_acc'])
        plt.title(name + " Accuracy")
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend(['Train', 'Test'], loc=0)

        if show:
            plt.show()


if __name__ == "__main__":
    print(MorphAnalyzer.getMorph("미친전세값"))
    newsML = NewsML(NewsML.TENSORFLOW)
    newsML.getNewsData('')
