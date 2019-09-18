import urllib.request
import json
import csv
import re
import datetime
import dateutil.parser  # pip install python-dateutil
import pytz
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from multiprocessing.dummy import Pool

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
                return f"Error : File {fileName} does not exist."

    def RequestNewsByDate(self, query, begin=datetime.datetime(1900, 1, 1), end=datetime.datetime.today(),
                          pages=1000):  # 날짜를 기준으로 거르기
        """

        """
        utc = pytz.UTC
        for x in tqdm(range(1, pages + 1), desc='Grabbing Links'):
            self.RequestNewsLink(query, x, sort='date')
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
    LinkData = []  # Title, Link, OriginalLink
    NewsData = []  # Title, Press, Date, Content

    UserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) " \
                "Version/12.0 Mobile/15E148 Safari/604.1 "

    threadCount = 6

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
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
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

    @staticmethod
    def Format_Naver(content, item):
        """

        """
        soup = BeautifulSoup(content, 'html.parser')
        content_html = soup.find("div", {"id": "dic_area"})
        if content_html is None:
            return None
        content = soup.find("div", {"id": "dic_area"}).text
        date = soup.find("span", {"class": "media_end_head_info_datestamp_time"}).text
        # print(content, date)
        return item["Title"], urlparse(item["OriginalLink"]).netloc, date, content.split('.')

    def SaveNews(self, fileName="NewsData"):
        """

        """

        self.GetNewsMultithread()
        news_list = list()
        for item in self.NewsData:
            if item is not None:
                news_list.append(NewsData(title=item[0], press=item[1], date=item[2], content=item[3]))
        news_list = NewsList(news_list)
        news_list.printCell()
        news_list.exportPickle(fileName)
        return "Success"


"""
    UNUSED FUNCTION FOR LATER USE
    def OpenLink(self, fileName="LinkData.csv"):
        pass
"""

if __name__ == "__main__":
    api = NaverNewsAPI()
    # api.RequestNewsLink("19대 대선", 1, 1) #제안 : '이번 대선' 등으로 나타내는 경우도 있으므로 '대선' 이라고 찾은 뒤에 날짜로 필터링
    api.RequestNewsByDate("19대 대선", datetime.datetime(2019, 6, 5), pages=1)
    crawler = NewsArticleCrawler(api.LinkData)
    crawler.LinkData = api.LinkData
    crawler.SaveNews()
