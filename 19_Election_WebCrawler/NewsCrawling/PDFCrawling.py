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

    def text(self, parsed_text):
        parsed_text = re.sub('\n', '', parsed_text)
        parsed_text = re.sub(r'\([^)]*\)', '', parsed_text)
        try:
            parsed_text = re.search('본회의를 개의하겠습니다.(.*)산회를 선포합니다.', parsed_text).group(1)
        except AttributeError:
            print("본회의가 개의되지 않았거나 내가 Regex 잘못 씀.")
        parsed_text = parsed_text.split('◯')
        return_text = list()
        for personText in parsed_text:
            speaker_name = personText.split()[:2]
            person_text = list()
            for txt in personText.split('.'):
                person_text.append(txt.split()[2:])
            return_text.append([speaker_name, person_text])
        return return_text

    def read_pdf(self, file_name='1.PDF'):
        try:
            file_data = tikaParse.from_file(file_name)  # Parse data from file
            text_data = file_data['content']  # Get file's text content
        except IOError as e:
            print("Error parsing PDF per next line : ")
            print(e)
            return " "
        return self.text(text_data)

    def read_folder(self, dir_name="../Data/*.PDF"):  # Multithreaded Read Operations
        directories = glob.glob(dir_name)
        pool = Pool(self.threadCount)
        results = pool.map(self.read_pdf, directories)
        with open('../parsedPDF.txt', 'wb') as f:
            pickle.dump(results, f)


if __name__ == "__main__":
    parser = ParsePDF()
    print(parser.read_pdf('../Data/1.PDF'))  # Default is 1.PDF
    parser.read_folder()
