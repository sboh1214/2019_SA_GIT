
import re
import time
import glob
import pickle
from functools import partial
from multiprocessing.pool import ThreadPool as Pool
#from multiprocessing.dummy import Pool

from tqdm import tqdm
import xlrd
from selectolax.parser import HTMLParser
import requests

from data import NewsData, NewsList

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
    processed = 0

    def FetchNews(self, url):
        if url == '':
            self.error_cnt['url'] += 1
            return ""
        elif url.startswith('http:www.'): #아시아경제 나뻐
            url = 'http://' + url[5:]
        elif url.startswith('www.'): #빅카인즈 에휴
            url = 'http://' + url
        if "khan" not in url:
            pass
        elif "kmib" not in url:
            pass
        elif "kookje" not in url:
            pass
        elif "naeil" not in url:
            pass
        elif "donga" not in url:
            pass
        elif "dt.co.kr" not in url:
            pass
        elif "imaeil" not in url:
            pass
        elif "munhwa" not in url:
            pass
        elif "sedaily" not in url:
            pass
        elif "segye" not in url:
            pass
        elif "asiae." not in url:
            pass
        elif "ajunews." not in url:
            pass
        elif "etnews." not in url:
            pass
        elif "chosun." not in url:
            pass
        elif "joins." not in url:
            pass
        elif "fnnews." not in url:
            pass
        elif "hani." not in url:
            pass
        elif "hankyung." not in url:
            pass
        elif "heraldcorp." not in url:
            pass
        elif "kbs." not in url:
            pass
        elif "imbc." not in url:
            pass
        elif "obsnews." not in url:
            pass
        elif "sbs." not in url:
            pass
        elif "ytn." not in url:
            pass
        elif "naver." not in url:
            pass
        else:
            return ""

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
        try:
            content = self.multi_parser(self.FetchNews(newslink['OriginalLink']), newslink['OriginalLink'])
            if content == "":
                return ""
            self.NewsData.append({
                'Content': content,
                'Title': newslink['Title'],
                'Link': newslink['OriginalLink'],
                'ID': newslink['ID'],
                'Journalist': newslink['Journalist'],
                'Press': newslink['Press'],
                'Date': newslink['Date']
            })
        except:  # Oops
            return ""

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
            text += node.text()
        result = re.sub('\xa0', '', text)
        return result.split(".")

    def MultiParseWrapper(self, newsitem):
        if newsitem['Content'] == "":
            self.error_cnt['data'] += 1
            return
        try:
            parsed = self.multi_parser(newsitem['Content'], newsitem['Link'])
            self.NewsData.append(NewsData(title=newsitem['Title'], press=newsitem['Press'], date=newsitem['Date'], content=self.multi_parser(newsitem['Content'], newsitem['Link']), id=newsitem['ID'], journalist=newsitem['Journalist']))
        except: #Oops
            return
        return NewsData(title=newsitem['Title'], press=newsitem['Press'], date=newsitem['Date'], content=self.multi_parser(newsitem['Content'], newsitem['Link']), id=newsitem['ID'], journalist=newsitem['Journalist'])

    def SmartFetch(self, url):
        content = self.FetchNews(url)
        #print(content)
        if content == "":
            self.error_cnt['data'] += 1
            return None
        content = self.multi_parser(content, url)
        if content == "ERR":
            return ""
        return content.text()
    
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
        #for row_idx in range(1, xl_sheet.nrows):
        for row_idx in range(1, 1000):
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
    #api = NaverNewsAPI()
    # api.RequestNewsLink("19대 대선", 1, 1) #제안 : '이번 대선' 등으로 나타내는 경우도 있으므로 '대선' 이라고 찾은 뒤에 날짜로 필터링
    # api.RequestNewsByDate("19대 대선", datetime.datetime(2019, 6, 5), pages=30, display=100)
    #api.RequestNewsByDate("19대 대선", datetime.datetime(2019, 6, 5), pages=1, display=10)
    #crawler = NewsArticleCrawler(api.LinkData)
    crawler = NewsArticleCrawler()
    #crawler.LinkData = api.LinkData

    threadCount = int(input("Thread Count?"))
    #threadCount = 4
    start_num = 0
    s = "o"
    """
    s = input("Press o to continue from Link Operation.\nPress d to Download Link.\nPress p to parse downloads.")
    if s == "d":
        start_num = int(input("Place to start from?"))
    """
    if s == "o":
        #PARSE NEWS LINK
        print("OBTAINING LINK FROM EXCEL FILE...")
        files = glob.glob("./Test/Data/BigKinds/*/*.xlsx")
        #files = glob.glob("/Users/sjk/Desktop/*.xlsx")
        print(files)
        results = list()
        for file in tqdm(files, unit=" Sheet"):
            crawler.ParseFromBigKinds(file)
        with open("NewsParseLink.dat", 'wb') as f:
            pickle.dump(crawler.NewsLink, f)

    # DOWNLOAD FROM LINK
    print("DOWNLOADING FROM LINK...")
    with open("NewsParseLink.dat", 'rb') as f:
        newslinklist = pickle.load(f)
        pool = Pool(threadCount * 2)
        n = 1000
        for i in tqdm(range(0, len(newslinklist), n)):
            crawler_temp = NewsArticleCrawler()
            with tqdm(total=len(newslinklist[i:i + n])) as pbar:
                for i, _ in tqdm(enumerate(
                        pool.imap_unordered(crawler_temp.FetchNewsWrapper, newslinklist[i:i + n], chunksize=8)),
                                 unit=" Articles"):
                    pbar.update()
            with open("NewsRawData.dat", 'ab') as f:
                for news in crawler_temp.NewsData:
                    pickle.dump(news, f)
            print('')
            del crawler_temp
    """
    # PARSE FROM DOWNLOADS
    print("PARSING DOWNLOADS...")
    with open("NewsRawData.dat", 'rb') as f:
        newslist = []
        while 1:
            try:
                newslist.append(pickle.load(f))
            except EOFError:
                break
        pool = Pool(threadCount)
        with tqdm(total=len(newslist)) as pbar:
            for i, _ in tqdm(enumerate(pool.imap_unordered(crawler.MultiParseWrapper, newslist, chunksize=8)),
                             unit=" Articles"):
                pbar.update()
    with open("NewsData.dat", 'wb') as f:
        pickle.dump(crawler.NewsData, f)
    """
    print("PARSING DOWNLOADS...")
    with open("NewsRawData.dat", 'rb') as f:
        newslist = []
        while 1:
            try:
                newslist.append(pickle.load(f))
            except EOFError:
                break
    with open("NewsData.dat", 'wb') as f:
        pickle.dump(newslist, f)
    print("처리 끗")
    print("(펑)한 개수:", crawler.error_cnt)


    print("처리 끗")
    print("(펑)한 개수:", crawler.error_cnt)


    #crawler.ReadNewsFromFolder()
    #print(crawler.SmartFetch(input("URL :")))
