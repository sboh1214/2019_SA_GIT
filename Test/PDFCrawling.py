"""

Pickle comes in the following format:
[파일당 한줄,
[[말하는 사람,[말한 문장, 말한 문장]],[말하는 사람,[말한 문장, 말한 문장]],...],
[[말하는 사람,[[단어],[단어],...]]
]

"""

import glob
import pickle
import re
from multiprocessing.dummy import Pool

from tika import parser as tikaParse

from data import PdfList as PDFList


class ParsePDF:
    threadCount = 4
    error_count = 0

    def text(self, parsed_text, file_name):
        parsed_text = re.sub('\n', '', parsed_text)
        parsed_text = re.sub(r'\([^)]*\)', '', parsed_text)
        try:
            parsed_text = re.search(r"^.*(개의하겠습니다\.|의석을 정돈|개회하겠습니다\.|개의하도록 하겠습니다\.)(.*)(산회를 선포|마치도록 하겠습니다\.|속개하도록 하겠습니다\.|정회를 선포합니다\.|회의중지\)|회의를 잠시 중지하고).*$", parsed_text).group(1)
        except AttributeError:
            print("본회의가 개의되지 않았거나 내가 Regex 잘못 씀.")
            self.error_count += 1
            print(file_name)
            print(parsed_text)
        parsed_text = parsed_text.split('◯')
        return_text = []
        for personText in parsed_text:
            speaker_name = personText.split()[:2]
            talk_text = list()
            for txt in personText.split('.'):
                talk_text.append(txt.split()[2:])
            return_text.append([speaker_name, personText, talk_text])
        return return_text

    def read_pdf(self, file_name='1.PDF'):
        # print(file_name)
        try:
            file_data = tikaParse.from_file(file_name)  # Parse data from file
            text_data = file_data['content']  # Get file's text content
        except IOError as e:
            print("Error parsing PDF per next line : ")
            print(e)
            return " "
        except UnicodeEncodeError as e:
            print("Error parsing PDF per next line : ")
            print(e)
            return " "
        return self.text(text_data, file_name)

    def read_folder(self, dir_name="./Data/*.PDF"):  # Multithreaded Read Operations
        files = glob.glob(dir_name)
        print(files)
        pool = Pool(self.threadCount)
        results: PDFList = pool.map(self.read_pdf, files)
        with open('parsedPDF.dat', 'wb') as f:
            pickle.dump(results, f)
        print(results)


if __name__ == "__main__":
    parser = ParsePDF()
    # print(parser.read_pdf('Data/1.PDF'))  # Default is 1.PDF
    parser.read_folder()
    print("Error count :", parser.error_count)
