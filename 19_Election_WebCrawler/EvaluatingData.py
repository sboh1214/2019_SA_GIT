import pickle


class PdfList:

    List = []

    def importPickle(self, fileName="PdfData.txt"):
        with open(fileName, 'rb') as f:
            self.List=pickle.load(f)
        return self.List

class NewsData:
    Title = ""
    Press = ""
    Date = ""
    Content = [[""]]
    Bias = 0

    def __init__(self, **kwargs=None):
        super().__init__()
        if 'title' in kwargs:
            self.Title = kwargs['title']
        elif 'press' in kwargs:
            self.Press = kwargs['press']
        elif 'Date' in kwargs:
            self.Date = kwargs['date']
        elif 'Content' in kwargs:
            self.Content = kwargs['Content']
        elif 'Bias' in kwargs:
            self.Bias = kwargs['bias']


class NewsList:
    def __init__(self, **kwargs=None):
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
