import pickle


class PdfData:
    Speaker=""
    Speech=""
    Word=[""]
    def __init__(self, speaker, speech, word):
        self.Speaker=speaker
        self.Speech=speech #안잘린거
        self.Word=word #잘린거


class PdfList:
    def __init__(self, l):
        self.List = l

    List = []

    def importPickle(self, fileName="PdfData.txt"):
        with open(fileName, 'rb') as f:
            self.List=pickle.load(f)
        return self.List

class NewsList:
    def __init__(self, **kwargs):
        super().__init__()
        self.List = kwargs['list']

    List = []

    def exportPickle(self, fileName="NewsData.txt"):
        with open(fileName, 'wb') as f:
            pickle.dump(self.List, f)

    def importPickle(self, fileName="NewsData.txt"):
        with open(fileName, 'rb') as f:
            self.List = pickle.load(f)
        return self.List
