import tensorflow
import csv

class NewsML:
    Title = []
    Press = []
    Date = []
    Content = []

    def GetNewsData(fileName):
        f = open(fileName+'.csv', 'r', encoding='utf-8')
        rdr = csv.reader(f)
        for line in rdr:
            Title.append(line['Title'])
            Press.append(line['Press'])
            Date.append(line['Date'])
            Content.append(line['Content'])
        f.close()
    
    
    