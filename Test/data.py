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
        if 'press' in kwargs:
            self.Press = kwargs['press']
        if 'date' in kwargs:
            self.Date = kwargs['date']
        if 'content' in kwargs:
            self.Content = kwargs['content']
        if 'sentence_bias' in kwargs:
            self.Sentence_Bias = kwargs['sentence_bias']
        else:
            self.Sentence_Bias = [0 for _ in self.Content]
        if 'bias' in kwargs:
            self.Bias = kwargs['bias']

    def __str__(self):
        return f"NewsData.dat Title:{self.Title}, Press:{self.Press}, Date:{self.Date}, Bias:{self.Bias}, Count of Sentence:{len(self.Content)}, Count of Bias:{len(self.Sentence_Bias)}"


class NewsList:
    List = []

    def __init__(self, news_list=None):
        super().__init__()
        self.List = news_list

    def exportPickle(self, fileName: str = "NewsData"):
        with open(fileName + ".dat", 'wb') as f:
            pickle.dump(self.List, f)

    def importPickle(self, fileName: str = "NewsData"):
        with open(fileName + ".dat", 'rb') as f:
            self.List = pickle.load(f)
        return self.List


class PdfData:
    pass


class PdfList:
    List = []

    def importPickle(self, fileName="PdfData.txt"):
        with open(fileName, 'rb') as f:
            self.List = pickle.load(f)
        return self.List


if __name__ == '__main__':
    a = NewsData(title='제목 A', press='신문사 A', date='', content=[["여러분", "안녕하세요"], ["감사합니다"]])
    b = NewsData()
    c = NewsData(title='제목 C', press='신문사 C', date='', content=[["여러분", "안녕하세요"], ["감사합니다"]], sentence_bias=[1, -1],
                 bias=0)
    d = NewsList(news_list=[a, b, c])
    e = NewsList()
    e.List = [a, b, c]
    print(e.List[0])
    print(e.List[1])
    print(e.List[2])
