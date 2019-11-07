import urllib.request
import json
import csv
import re
import datetime
import glob
import pickle
import chardet
from urllib.error import URLError
from functools import partial

import dateutil.parser  # pip install python-dateutil
import pytz

from tqdm import tqdm
#from bs4 import BeautifulSoup
from urllib.parse import urlparse
from multiprocessing.dummy import Pool
import xlrd
from xlrd.sheet import ctype_text 
from selectolax.parser import HTMLParser
import requests

from data import NewsData, NewsList


class NaverNewsAPI:
    """

    """
    Client_ID = 'Mo_tHONZPPs7OeNzZQAE'
    Client_Secret = 'vVve0WqXE5'
    LinkData = []  # {Title, Link, OriginalLink, Date}

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
            pub_date = dateutil.parser.parse(item['Date'])  # Tue, 04 Jun 2019 11:52:00 +0900
            self.LinkData.append({"Title": title, "Link": link, "OriginalLink": original_link, "Date": pub_date})
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

    def RequestNewsByDate(self, query, begin=datetime.datetime(1900, 1, 1), end=datetime.datetime.today(),
                          pages=1000, display=100):  # 날짜를 기준으로 거르기
        """

        """
        utc = pytz.UTC
        for x in tqdm(range(1, pages + 1), desc='Grabbing Links'):
            self.RequestNewsLink(query, x, display, sort='date')
            for data in self.LinkData:
                if data['Date'].replace(tzinfo=utc) < begin.replace(tzinfo=utc):
                    self.LinkData.remove(data)
                    continue
                if data['Date'].replace(tzinfo=utc) > end.replace(tzinfo=utc):
                    self.LinkData.remove(data)
                    break


class NewsArticleCrawler:
    """

    """
    LinkData = []   # {Title, Link, OriginalLink, Date}
    NewsData = []   # {Title, Press, Date, Content, ID, Journalist}
    NewsRaw = [] 
    NewsLink = []
    error_cnt={'url':0, 'connection':0, 'data':0, 'parse':0}
    UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15"
    threadCount = 4

    def FetchNews(self, url):
        if url == '':
            self.error_cnt['url'] += 1
            return ""
        elif url.startswith('http:www.'): #아시아경제 나뻐
            url = 'http://' + url[5:]
        elif url.startswith('www.'): #빅카인즈 에휴
            url = 'http://' + url
        """
        request = urllib.request.Request(url)
        request.add_header("User-Agent", self.UserAgent)
        try :
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
        except URLError as e:
            print("URL Error -", e, url)
            self.error_cnt['url'] += 1
            return ""
        except ConnectionResetError as e:
            print("CR Error -", e, url)
            self.error_cnt['connection'] += 1
            return ""
        if rescode != 200:
            print("Response Error -", rescode, url)
            self.error_cnt['connection'] += 1
            return ""
        try:
            content = response.read().decode('UTF-8')
        except UnicodeDecodeError as e:
            try:
                content = response.read().decode('EUC-KR')
            except UnicodeDecodeError as e:
                self.error_cnt['data'] += 1
                return ""
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15',
            'Host': url.split('/')[2],
            'Connection': "keep-alive",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Accept-language': "ko-kr", 
            'Referer': 'https://duckduckgo.com/',
            "Accept-Encoding": "gzip, deflate, br"
        }
        r = requests.get(url, headers=headers)
        if r.apparent_encoding != "Windows-1254":
            r.encoding = r.apparent_encoding
        return r.text

    def FetchNewsWrapper(self, newslink):
        self.NewsRaw.append({
            'Content' : self.FetchNews(newslink['OriginalLink']),
            'Title' : newslink['Title'],
            'Link' : newslink['OriginalLink'],
            'ID' : newslink['ID'],
            'Journalist' : newslink['Journalist'],
            'Press': newslink['Press'],
            'Date': newslink['Date']
            })

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

    def multi_parser(self, html, link):
        #soup = BeautifulSoup(html, 'html.parser')
        if "khan" in link:
            selector = "#articleBody > p"
        elif "kmib" in link:
            selector = "#articleBody"
        elif "kookje" in link:
            selector = ".news_article"
        elif "naeil" in link:
            selector = "#contents > p"
        elif "donga" in link:
            selector = ".article_txt" #동아 좆까
        elif "dt.co.kr" in link:
            selector = ".art_txt"
        elif "mk.co.kr" in link: #빅카인즈 주소 오류ㅠ
            selector = "#article_body"
        elif "imaeil" in link:
            selector = ".article_area > p" 
        elif "moneytoday" in link:
            selector = "#textBody" #리디렉션 오류
        elif "munhwa" in link:
            selector = "#NewsAdContent" 
        elif "sedaily" in link:
            selector = ".view_con"
        elif "segye" in link:
            selector = "#article_txt > article > p"
        elif "asiae." in link:
            selector = "#txt_area > p"
        elif "ajunews." in link:
            selector = "#articleBody"
        elif "etnews." in link:
            selector = "#articleBody > p"
        elif "chosun." in link:
            selector = "#news_body_id"
        elif "joins." in link:
            selector = "#article_body"
        elif "fnnews." in link:
            selector = "#article_content"
        elif "hani." in link:
            selector = "#contents-article .text"
        elif "hankyung." in link:
            selector = "#articletxt"
        elif "hankookilbo." in link: #BigKinds 주소오류
            selector = "#article_story"
        elif "heraldcorp." in link:
            selector = "#articleText > p"
        elif "kbs." in link:
            selector = "#cont_newstext"
        elif "imbc." in link:
            selector = ".txt"
        elif "obsnews." in link:
            selector = "#CmAdContent"
        elif "sbs." in link:
            selector = ".text_area"
        elif "ytn." in link:
            selector = "#CmAdContent > span"
        elif "naver." in link:
            selector = "#articleBodyContents"
        else:
            self.error_cnt['parse'] += 1
            return "ERR"
        text = ""
        for node in HTMLParser(html).css(selector):
            text += node.html
        return re.sub('\xa0', '', text)

    def MultiParseWrapper(self, newsitem):
        if newsitem['Content'] == "":
            self.error_cnt['data'] += 1
            return
        self.NewsData.append(NewsData(title=newsitem['Title'], press=newsitem['Press'], date=newsitem['Date'], content=self.multi_parser(newsitem['Content'], newsitem['Link']), id=newsitem['ID'], journalist=newsitem['Journalist']))

    def SmartFetch(self, url):
        content = self.FetchNews(url)
        #print(content)
        if content == "":
            self.error_cnt['data'] += 1
            return None
        content = self.multi_parser(content, url)
        if content == "ERR":
            return ""
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
        #self.NewsData_K.append(news)
        
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
        return self.NewsData_K
    
    def ParseFromBigKinds(self, fileName="/Users/sjk/Desktop/뉴스/Fasttrack-NewsResult_20180101-20191029.xlsx"):
        wb = xlrd.open_workbook(fileName)
        xl_sheet = wb.sheet_by_index(0)
        for row_idx in range(1, xl_sheet.nrows):
            self.NewsLink.append({
                'OriginalLink': xl_sheet.cell(row_idx, 17).value,
                'Title': xl_sheet.cell(row_idx, 4).value,
                'Date': xl_sheet.cell(row_idx, 1).value,
                'Press':  xl_sheet.cell(row_idx, 2).value,
                'ID' : xl_sheet.cell(row_idx, 0).value,
                'Journalist': xl_sheet.cell(row_idx, 3).value
            })
        return self.NewsLink


if __name__ == "__main__":
    api = NaverNewsAPI()
    # api.RequestNewsLink("19대 대선", 1, 1) #제안 : '이번 대선' 등으로 나타내는 경우도 있으므로 '대선' 이라고 찾은 뒤에 날짜로 필터링
    # api.RequestNewsByDate("19대 대선", datetime.datetime(2019, 6, 5), pages=30, display=100)
    #api.RequestNewsByDate("19대 대선", datetime.datetime(2019, 6, 5), pages=1, display=10)
    #crawler = NewsArticleCrawler(api.LinkData)
    crawler = NewsArticleCrawler()
    #crawler.LinkData = api.LinkData

    #threadCount = int(input("Thread Count?"))
    threadCount = 4

    #PARSE NEWS LINK
    print("OBTAINING LINK FROM EXCEL FILE...")
    files = glob.glob("./Test/Data/BigKinds/조국/*.xlsx")
    #files = glob.glob("/Users/sjk/Desktop/*.xlsx")
    print(files)
    results = list()
    for file in tqdm(files, unit=" Sheet"):
        crawler.ParseFromBigKinds(file)
    with open("NewsParseLink.dat", 'wb') as f:
        pickle.dump(crawler.NewsLink, f)

    #DOWNLOAD FROM LINK
    print("DOWNLOADING FROM LINK...")
    with open("NewsParseLink.dat", 'rb') as f:
        newslinklist = pickle.load(f)
        pool = Pool(threadCount*2)
        with tqdm(total=len(newslinklist)) as pbar:
            for i, _ in tqdm(enumerate(pool.imap_unordered(crawler.FetchNewsWrapper, newslinklist)), unit=" Articles"):
                pbar.update()
    with open("NewsRawData.dat", 'wb') as f:
        pickle.dump(crawler.NewsRaw, f)

    #PARSE FROM DOWNLOADS
    print("PARSING DOWNLOADS...")
    with open("NewsRawData.dat", 'rb') as f:
        newslist = pickle.load(f)
        pool = Pool(threadCount)
        with tqdm(total=len(newslist)) as pbar:
            for i, _ in tqdm(enumerate(pool.imap_unordered(crawler.MultiParseWrapper, newslist)), unit=" Articles"):
                pbar.update()
    with open("NewsData.dat", 'wb') as f:
        pickle.dump(crawler.NewsData, f)
    print("처리 끗")
    print("(펑)한 개수:", crawler.error_cnt)


    #crawler.ReadNewsFromFolder()
    #print(crawler.SmartFetch(input("URL :")))
