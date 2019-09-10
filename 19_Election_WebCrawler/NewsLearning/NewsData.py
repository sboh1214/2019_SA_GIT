import pickle


class NewsData:
    def __init__(self, **kwargs):
        super().__init__()
        self.Title = kwargs['title']
        self.Press = kwargs['press']
        self.Date = kwargs['date']
        self.Content = kwargs['content']

    Title = ""
    Press = ""
    Date = ""
    Content = [[""]]


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
