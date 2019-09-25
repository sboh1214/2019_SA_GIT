import matplotlib.pyplot as plt
from tensorflow.keras import Sequential
from tensorflow.keras.layers import *
# from khaiii import KhaiiiApi
from tqdm import tqdm

from Test.data import NewsList

'''
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


class NewsMLKeras:
    """

    """
    NewsList = []

    Rnn_X_Train = []
    Rnn_Y_Train = []
    Rnn_X_Test = []
    Rnn_Y_Test = []

    Cnn_X_Train = []
    Cnn_Y_Train = []
    Cnn_X_Test = []
    Cnn_Y_Test = []

    Rnn_Model = None
    Cnn_Model = None
    History = None

    def setKor2Vec(self, train=False):
        if train:

            pass

    def getNewsData(self, filename: str):
        """

        """
        news = NewsList()
        news_list = news.importPickle(filename)
        self.NewsList = news_list
        train: list = news_list[:int(len(news_list) * 0.8)]
        test: list = news_list[int(len(news_list) * 0.8):]
        for data in tqdm(train):
            for i, sentence in enumerate(data.Content):
                self.Rnn_X_Train.append(" ".join(sentence))
                self.Rnn_Y_Train.append(data.Sentence_Bias[i])
                self.Cnn_Y_Test.append(data.Bias)
        for data in tqdm(test):
            for i, sentence in enumerate(data.Content):
                self.Rnn_X_Test.append(" ".join(sentence))
                self.Rnn_Y_Test.append(data.Sentence_Bias[i])
                self.Cnn_Y_Test.append(data.Bias)
        news.printCell()

    def buildRNNModel(self, max_length: int = 100, max_features: int = 100):
        """

        """
        model = Sequential()
        model.add(Embedding(input_dim=max_features, output_dim=128))
        model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
        model.add(Dense(1, activation='sigmoid'))
        model.add(Dropout(0.5))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.Rnn_Model = model

    def buildCnnModel(self):
        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
        model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPool2D(pool_size=(2, 2)))
        model.add(Dropout(rate=0.25))
        model.add(Flatten())
        model.add(Dense(units=128, activation='relu'))
        model.add(Dropout(rate=0.5))
        model.add(Dense(units=1, activation='relu'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.Cnn_Model = model

    def runRnnModel(self, epochs: int = 1, batch_size: int = 10):
        self.Rnn_Model.fit(x=self.Rnn_X_Test, y=self.Rnn_Y_Test,
                           batch_size=batch_size,
                           epochs=epochs,
                           validation_split=0.2)

    def runCnnModel(self, epochs: int = 1, batch_size: int = 10):
        self.Cnn_Model.fit(x=self.Cnn_X_Test, y=self.Cnn_Y_Test,
                           batch_size=batch_size,
                           epochs=epochs,
                           validation_split=0.2)

    def plotLossAndAccuracy(self, name="", show=False):
        """
        Plot history for loss and accuracy of train and validation data.
        """
        plt.figure()
        plt.subplot((4, 1, 1))
        plt.plot(self.History.history['loss'])
        plt.plot(self.History.history['val_loss'])
        plt.title(name + " RNN Loss")
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(['Train', 'Test'], loc=0)

        plt.subplot((4, 1, 2))
        plt.plot(self.History.history['acc'])
        plt.plot(self.History.history['val_acc'])
        plt.title(name + " CNN Accuracy")
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend(['Train', 'Test'], loc=0)

        if show:
            plt.show()


if __name__ == "__main__":
    newsML = NewsMLKeras()
    newsML.getNewsData('NewsData')
    newsML.setKor2Vec(train=True)
    newsML.buildRNNModel()
    newsML.buildCnnModel()
    newsML.runRnnModel()
    newsML.runCnnModel()
