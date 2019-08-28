from tika import parser
from multiprocessing.dummy import Pool
import os
import csv
import re


class ParsePDF:
    threadCount = 4

    def parse(self, text):
        try:
            data = re.search('본회의를 개의하겠습니다.(.+?)ZZZ', text).group(1)
        except AttributeError:
            # AAA, ZZZ not found in the original string
            found = ''  # apply your error handling

        # found: 1234

    def readPDF(self, fileName='1.PDF'):
        try:
            file_data = parser.from_file(fileName)  # Parse data from file
            text = file_data['content']  # Get file's text content
        except:
            print("Error parsing PDF (wrong dir probably)")
            return " "
        return text

    def readFolder(self, dirName='../Data'):            #Multithreaded Read Operations
        directories = os.listdir(dirName)
        pool = Pool(self.threadCount)
        f = open("NA.csv", 'w', encoding='utf-8', newline='')
        results = pool.map(self.readPDF, directories)
        csvFile = csv.writer(f)
        for result in results:
            csvFile.writerows([result])
        f.close()



if __name__ == "__main__":
    print (os.path.dirname(os.path.realpath(__file__))+'/1.PDF')
    parser = ParsePDF()
    parser.readPDF()                    #Default is in git repo


