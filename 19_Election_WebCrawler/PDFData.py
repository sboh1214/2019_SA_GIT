import pickle


class PdfData:
    def __init__(self, speaker, speech, word):
        self.Speaker = speaker
        self.Speech = speech  # 안잘린거
        self.Word = word  # 잘린거

    Minutes = []


class PdfList:
    def __init__(self, l):
        self.List = l

    List = []

    def exportPickle(self, fileName="PdfData.txt"):
        with open(fileName, 'wb') as f:
            pickle.dump(self.List, f)
