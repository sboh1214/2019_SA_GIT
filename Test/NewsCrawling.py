import urllib.request
import json
import csv
import re
import datetime
import glob
from urllib.error import URLError
from functools import partial

import dateutil.parser  # pip install python-dateutil
import pytz

from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from multiprocessing.dummy import Pool
import xlrd
from xlrd.sheet import ctype_text 

from data import NewsData, NewsList


class NaverNewsAPI:
    """

    """
    Client_ID = 'Mo_tHONZPPs7OeNzZQAE'
    Client_Secret = 'vVve0WqXE5'
    LinkData = []  # Title, Link, OriginalLink, pubDate

    def RequestNewsLink(self, query, n=1, display=100, sort="sim"):
        """

        """
        if n < 1 or n > 1000:
            return "Error (invalid n)"
        if display < 1 or display > 100:
            return "Error (invalid display)"

        q = urllib.parse.quote(query)
        url = "https://openapi.naver.com/v1/search/news?query=" + q + \
              "&display=" + str(display) + "&sort=" + sort + "&start=" + str(n)
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.Client_ID)
        request.add_header("X-Naver-Client-Secret", self.Client_Secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode != 200:
            return "Error (http)" + rescode
        response_body = response.read()
        json_data = response_body.decode('utf-8')

        json_data = json.loads(json_data)
        json_items = json_data['items']
        for item in json_items:
            title = self.MakePlainText(item['title'])
            link = item['link']
            original_link = item['originallink']
            pub_date = dateutil.parser.parse(item['pubDate'])  # Tue, 04 Jun 2019 11:52:00 +0900
            self.LinkData.append({"Title": title, "Link": link, "OriginalLink": original_link, "pubDate": pub_date})
        return "Success"

    @staticmethod
    def MakePlainText(title):
        """

        """
        title = re.sub('\"\'', '', title)
        # html 태그 제거
        title = BeautifulSoup(title, 'html.parser').text
        # 한자 변경
        title = re.sub('與', '여당', title)
        title = re.sub('野', '야당', title)
        title = re.sub('朴', '박근혜', title)
        title = re.sub('文', '문재인', title)
        title = re.sub('號', '호', title)
        return title

    def SaveLink(self, fileName="LinkData.csv"):
        """

        """
        with open(fileName, 'w', encoding='utf-8', newline='') as f:
            try:
                csv_file = csv.writer(f)
                for item in tqdm(self.LinkData):
                    title = item['Title']
                    link = item['Link']
                    original_link = item['OriginalLink']
                    csv_file.writerow([title, link, original_link])
                    f.close()
                return "Success"
            except FileNotFoundError:
                return "Error : File {fileName} does not exist."

    def RequestNewsByDate(self, query, begin=datetime.datetime(1900, 1, 1), end=datetime.datetime.today(),
                          pages=1000, display=100):  # 날짜를 기준으로 거르기
        """

        """
        utc = pytz.UTC
        for x in tqdm(range(1, pages + 1), desc='Grabbing Links'):
            self.RequestNewsLink(query, x, display, sort='date')
            for data in self.LinkData:
                if data['pubDate'].replace(tzinfo=utc) < begin.replace(tzinfo=utc):
                    self.LinkData.remove(data)
                    continue
                if data['pubDate'].replace(tzinfo=utc) > end.replace(tzinfo=utc):
                    self.LinkData.remove(data)
                    break


class NewsArticleCrawler:
    """

    """
    LinkData = []   # Title, Link, OriginalLink
    NewsData = []   # Title, Press, Date, Content
    NewsData_K = [] # NewsData List
    error_cnt=0

    UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15"

    threadCount = 16

    def __init__(self, linkData):
        self.LinkData = linkData

    def GetNewsMultithread(self):
        # threadCount = 4
        """

        """
        pool = Pool(self.threadCount)
        print("Fetching News...")
        pool.map(self.GetNews, self.LinkData)

    def GetNews(self, item):
        url = item["Link"]
        request = urllib.request.Request(url)
        request.add_header("User-Agent", self.UserAgent)
        try :
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
        except URLError as e:
            print("URL Error -", e, url)
            return "Error " + str(e)
        except ConnectionResetError as e:
            print("CR Error -", e, url)
            return "Error " + str(e)
        if rescode != 200:
            return "Error (http)" + rescode
        content = response.read()
        if "news.naver.com" in url:  # 네이버뉴스 모바일 - "dic_area"
            formatted_data = self.Format_Naver(content, item)
            if formatted_data is None:
                print('Error (Parsing Newspaper Content)')
            self.NewsData.append(formatted_data)
        else:
            pass
    """
    def GetSource(self, content):
        # khaiii만 돌리기엔 신뢰성이 낮다(예 : 더불어민주당 => 더불어 민/NNP 주/NNG 당/NNP으로)
        # 아마 preset(당명 등) 만들어 대입?
        possible_source = re.findall(r"[^.]*\w*은 [^.]*|[^.]*\w*는 [^.]*", content)
        api = khaiii.KhaiiiApi()
        print(possible_source)
        for line in possible_source:
            dic = {}
            for word in api.analyze(line):
                for morph in word.morphs:
                    print(morph)
    """

    def multi_parser(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find("div", {"class": "art_txt"})
        if content is not None:
            return content.text
        content = soup.find("div", {"class": "article_area"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "article_body"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "article_content"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "article_story"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "contents"}) #동아
        if content is not None:
            try:
                soup1 = BeautifulSoup(content, 'html.parser')
                content = soup1.find("div", {"class": "article_txt"})
                return content.text
            except:
                pass
        content = soup.find("div", {"id": "article_txt"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "articleBody"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "articleText"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "articletxt"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "CmAdContent"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "cont_newstext"}) #KBS
        if content is not None:
            return content.text
        content = soup.find("div", {"class": "description"}) #KBS_i
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "contents"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "contents-article"})
        if content is not None:
            return content.text
        content = soup.find("div", {"class": "news_article"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "news_body_id"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "NewsAdContent"})
        if content is not None:
            return content.text
        content = soup.find("div", {"class": "text_area"})
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "textBody"})
        if content is not None:
            return content.text
        content = soup.find("div", {"class": "txt"})
        if content is not None:
            return content.text
        content = soup.find("div", {"itemprop": "articleBody"}) #아경 ㄱㅅㄲ
        if content is not None:
            return content.text
        content = soup.find("div", {"class": "va_cont"}) #아경 ㄱㅅㄲ(2)
        if content is not None:
            return content.text
        content = soup.find("div", {"class": "view_con"})
        if content is not None:
            return content.text
        content = soup.find("section", {"class": "txt"})    #MBC
        if content is not None:
            return content.text
        content = soup.find("section", {"id": "articleBody"})    #ETNEWS
        if content is not None:
            return content.text
        content = soup.find("div", {"id": "article-view-content-div"}) #전북일보
        if content is not None:
            return content.text
        #print("PARSE FAIL")
        #print(html)
        self.error_cnt += 1
        return "ERR"

    def Format_Naver(self, content, item):
        """

        """
        soup = BeautifulSoup(content, 'html.parser')
        content = soup.find("div", {"id": "dic_area"})
        if content is None:
            return None
        content = str(content)
        content = content.split('<a href')[0]
        content = BeautifulSoup(content, 'html.parser').text
        date = soup.find("span", {"class": "media_end_head_info_datestamp_time"}).text
        #print(content)
        # self.GetSource(content)
        return item["Title"], urlparse(item["OriginalLink"]).netloc, date, content.split('.')

    def SmartFetch(self, url):
        if url.startswith('http:www.'): #아시아경제 나뻐
            url = 'http://' + url[5:]
        elif url.startswith('www.'):
            url = 'http://' + url
        request = urllib.request.Request(url)
        request.add_header("User-Agent", self.UserAgent)
        try :
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
        except URLError as e:
            print("URL Error -", e, url)
            return "Error " + str(e)
        except ConnectionResetError as e:
            print("CR Error -", e, url)
            return "Error " + str(e)
        if rescode != 200:
            return "Error (http)" + rescode
        try:
            content = response.read().decode('UTF-8')
        except UnicodeDecodeError as e:
            try:
                content = response.read().decode('EUC-KR')
            except UnicodeDecodeError as e:
                print('ay shit')
        if content == "":
            #print('aye shit')
            return None
        content = self.multi_parser(content)
        if content == "ERR":
            #print(url)
            return ""
        #print("OK")
        return content
    def ReadNewsFromFolder(self, dir_name="./Test/Data/BigKinds/조국/*.xlsx"):  # Multithreaded Read Operations
        files = glob.glob(dir_name)
        print(files)
        results = list()
        for file in tqdm(files):
            results.append(self.GetFromBigKinds(file))
        return results

    def ReadAppend(self, xl_sheet, row_idx):
        #print(xl_sheet.cell(row_idx, 17).value)
        try:
            content = self.SmartFetch(xl_sheet.cell(row_idx, 17).value)
        except:
            return
        
        if content is None:
            return
        news = NewsData(id = xl_sheet.cell(row_idx, 0).value, date = xl_sheet.cell(row_idx, 1).value, press = xl_sheet.cell(row_idx, 2).value, journalist = xl_sheet.cell(row_idx, 3).value, title = xl_sheet.cell(row_idx, 4).value, content = content)
        self.NewsData_K.append(news)
        
    def GetFromBigKinds(self, fileName="/Users/sjk/Desktop/뉴스/Fasttrack-NewsResult_20180101-20191029.xlsx"):
        wb = xlrd.open_workbook(fileName)
        xl_sheet = wb.sheet_by_index(0)
        pool = Pool(self.threadCount)
        func = partial(self.ReadAppend, xl_sheet)
        #pool.map(func, range(1, xl_sheet.nrows))
        with tqdm(total=xl_sheet.nrows) as pbar:
            for i, _ in tqdm(enumerate(pool.imap_unordered(func, range(1, xl_sheet.nrows))), unit=" Articles"):
                pbar.update()
        #pool.close()
        #pool.join()
        return 

    def SaveNews(self, fileName="NewsData"):
        """

        """

        #self.GetNewsMultithread()
        self.ReadNewsFromFolder()
        news_list = list()
        """
        for item in self.NewsData:
            if item is not None:
                news_list.append(NewsData(title=item[0], press=item[1], date=item[2], content=item[3]))
        news_list = NewsList(news_list + self.ReadNewsFromFolder())
        """
        news_list = NewsList(self.ReadNewsFromFolder())
        #news_list.printCell()
        news_list.exportPickle(fileName)
        return "Success"


if __name__ == "__main__":
    api = NaverNewsAPI()
    # api.RequestNewsLink("19대 대선", 1, 1) #제안 : '이번 대선' 등으로 나타내는 경우도 있으므로 '대선' 이라고 찾은 뒤에 날짜로 필터링
    # api.RequestNewsByDate("19대 대선", datetime.datetime(2019, 6, 5), pages=30, display=100)
    api.RequestNewsByDate("19대 대선", datetime.datetime(2019, 6, 5), pages=1, display=10)
    crawler = NewsArticleCrawler(api.LinkData)
    #crawler.LinkData = api.LinkData
    crawler.SaveNews()
    #print(crawler.SmartFetch('https://www.asiae.co.kr/article/2019101509145170905'))
    print("Done!")
    print("ERR CNT:", crawler.error_cnt)
