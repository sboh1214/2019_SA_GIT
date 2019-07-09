from tqdm import tqdm
import csv
from khaiii import KhaiiiApi
import matplotlib.pyplot as plt
import os

from keras.preprocessing import sequence
from keras import layers, models

import NewsCrawling as NC
import NewsEvaluating as NE

class MorphAnalyzer:
    """
    
    """
    def GetMorph(sentence):
        """
        >>> MorphAnalyzer.GetMorph("안녕, 세상")
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

    def __init__(self, backend="tensorflow"):
        os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
        return super().__init__()

    def GetNewsData(self, fileName):
        """

        """
        f = open(fileName+'.csv', 'r', encoding='utf-8')
        rdr = csv.reader(f)
        for line in tqdm(rdr):
            Title.append(line['Title'])
            Press.append(line['Press'])
            Date.append(line['Date'])
            Content.append(line['Content'])
        f.close()

    def BuildModel(self, MaxLen, MaxFeatures):
        """

        """
        x = layers.Input(shape=(MaxLen,))
        h = layers.Embedding(input_dim=MaxFeatures, output_dim=128)(x)
        h = layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2)(h)
        y = layers.Dense(1, activation='sigmoid')(h)
        model = Model(x,y)
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    def PlotLoss(self, history, name="", figure=1, subplot=(1,1,1), show=False):
        """
        Plot history for loss of train and validation data.
        """
        plt.figure(figure)
        plt.subplot(subplot)
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title(name+" Loss")
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(['Train','Test'], loc=0)
        if (show):
            plt.show()

    def PlotAccuracy(self, history, name="", figure=1, subplot=(1,1,1), show=False):
        """
        Plot history for accuracy of train and validation data.
        """
        plt.figure(figure)
        plt.subplot(subplot)
        plt.plot(history.history['acc'])
        plt.plot(history.history['val_acc'])
        plt.title(name+" Accuracy")
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend(['Train','Test'], loc=0)
        if (show):
            plt.show()

if __name__=="__main__":
    print(MorphAnalyzer.GetMorph("안녕, 세상"))