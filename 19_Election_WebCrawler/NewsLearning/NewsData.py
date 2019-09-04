import pickle


class NewsData:
    def __init__(self, title, press, date, content):
        self.Title = title
        self.Press = press
        self.Date = date
        self.Content = content

    Title = ""
    Press = ""
    Date = ""
    Content = [[""]]


class NewsList:
    def __init__(self, l):
        self.List = l

    List = []

    def exportPickle(self, fileName="NewsData.txt"):
        with open(fileName, 'wb') as f:
            pickle.dump(self.List, f)
