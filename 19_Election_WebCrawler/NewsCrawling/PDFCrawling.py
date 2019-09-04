"""

Pickle comes in the following format:
[파일당 한줄,
[[말하는 사람,[말한 문장, 말한 문장]]]
[[말하는 사람,[[단어],[단어],...]]
]

"""

from tika import parser as tikaParse
from multiprocessing.dummy import Pool
import os, glob
import pickle
import re


class ParsePDF:
    threadCount = 4

    def text(self, parsedText):
        parsedText = re.sub('\n', '', parsedText)
        parsedText = re.sub(r'\([^)]*\)', '', parsedText)
        try:
            parsedText = re.search('본회의를 개의하겠습니다.(.*)산회를 선포합니다.', parsedText).group(1)
        except AttributeError:
            print("본회의가 개의되지 않았거나 내가 Regex 잘못 씀.")
        parsedText = parsedText.split('◯')
        returnText = list()
        for personText in parsedText:
            speakerName = personText.split()[:2]
            personTextList = list()
            for txt in personText.split('.'):
                personTextList.append(txt.split()[2:])
            returnText.append([speakerName, personTextList])
        return returnText

    def readPDF(self, fileName='1.PDF'):
        try:
            file_data = tikaParse.from_file(fileName)  # Parse data from file
            textData = file_data['content']  # Get file's text content
        except IOError as e:
            print("Error parsing PDF per next line : ")
            print(e)
            return " "
        return self.text(textData)

    def readFolder(self, dirName='../Data/'):  # Multithreaded Read Operations
        directories = glob.glob("../Data/*.PDF")
        pool = Pool(self.threadCount)
        results = pool.map(self.readPDF, directories)
        with open('../parsedPDF.txt', 'wb') as f:
            pickle.dump(results,f)


if __name__ == "__main__":
    parser = ParsePDF()
    print(parser.readPDF('../Data/1.PDF'))  # Default is 1.PDF
    parser.readFolder()
