import pickle


class NewsData:
    Title: str = ""
    Press: str = ""
    Date = ""
    Content = [[""]]
    Sentence_Bias = [0]
    Bias: int = 0

    def __init__(self, **kwargs):
        super().__init__()
        if 'title' in kwargs:
            self.Title = kwargs['title']
        elif 'press' in kwargs:
            self.Press = kwargs['press']
        elif 'Date' in kwargs:
            self.Date = kwargs['date']
        elif 'Content' in kwargs:
            self.Content = kwargs['Content']
        elif 'sentence_bias' in kwargs:
            self.Sentence_Bias = kwargs['sentence_bias']
        elif 'Bias' in kwargs:
            self.Bias = kwargs['bias']


class NewsList:
    List = []

    def __init__(self, news_list=None):
        super().__init__()
        self.List = news_list

    def exportPickle(self, fileName: str = "NewsData.dat"):
        with open(fileName, 'wb') as f:
            pickle.dump(self.List, f)

    def importPickle(self, fileName: str = "NewsData.dat"):
        with open(fileName, 'rb') as f:
            self.List = pickle.load(f)
        return self.List


if __name__ == '__main__':
    a = NewsData(title='제목', press='신문사', date='', content=[["여러분", "안녕하세요"], ["감사합니다"]])
    b = NewsData()
    c = NewsData(title='제목', press='신문사', date='', content=[["여러분", "안녕하세요"], ["감사합니다"]])
    d = NewsList(news_list=[a, b, c])
    e = NewsList()
    e.List = [a, b, c]
