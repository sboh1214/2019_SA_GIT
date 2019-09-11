import pickle

class PdfList:

    List = []

    def importPickle(self, fileName="PdfData.txt"):
        with open(fileName, 'rb') as f:
            self.List=pickle.load(f)
        return self.List