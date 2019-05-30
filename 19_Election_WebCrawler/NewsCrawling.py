import urllib.request
import json
import csv
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class NaverNewsAPI:
    Client_ID = 'Mo_tHONZPPs7OeNzZQAE'
    Client_Secret = 'vVve0WqXE5'
    LinkData = [] #Title, Link, OriginalLink

    def RequestNewsLink(self, query, n =1, display=100, sort="sim"): #CHANGE THE DISPLAY DEFAULT # TO 100
        if n < 1 or n > 1000:
            return "Error (invalid n)"
        if display < 1 or display > 100:
            return "Error (invalid display)"

        q = urllib.parse.quote(query)
        url = "https://openapi.naver.com/v1/search/news?query=" + q + \
            "&display="+str(display)+"&sort=" + sort + "&start="+str(n)
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.Client_ID)
        request.add_header("X-Naver-Client-Secret", self.Client_Secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode != 200):
            return "Error (http)" + rescode
        response_body = response.read()
        jsonData = response_body.decode('utf-8')

        json_data = json.loads(jsonData)
        json_items = json_data['items']
        for item in json_items:
            title = self.MakePlainText(item['title'])
            link = item['link']
            originalLink = item['originallink']
            self.LinkData.append({"Title": title, "Link": link, "OriginalLink": originalLink})
        return "Success"

    def MakePlainText(self, title):
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
        try:
            f = open(fileName, 'w', encoding='utf-8', newline='')
            csvFile = csv.writer(f)
            for item in self.LinkData:
                title = item['Title']
                link = item['Link']
                originalLink = item['OriginalLink']
                csvFile.writerow([title, link, originalLink])
                f.close()
            return "Success"
        except:
            f.close()
            return "Error"


class NewsArticleCrawler:
    LinkData = [] #Title, Link, OriginalLink
    NewsData = [] #Title, Press, Date, Content

    UserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1"

    def GetNews(self):
        for item in self.LinkData:
            url = item["Link"]
            request = urllib.request.Request(url)
            request.add_header("User-Agent",self.UserAgent)
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            if(rescode != 200):
                return "Error (http)" + rescode
            content = response.read()
            if "news.naver.com" in url: #네이버뉴스 모바일 - "dic_area"
                self.NewsData.append(self.Format_Naver(content, item))
            else:
                pass

    def Format_Naver(self, content, item): 
        soup = BeautifulSoup(content, 'html.parser')
        content = soup.find("div", {"id": "dic_area"}).text
        date = soup.find("span", {"class": "media_end_head_info_datestamp_time"}).text
        #print(content, date)
        return (item["Title"], urlparse(item["OriginalLink"]).netloc, date, content)

    def OpenLink(self, fileName="LinkData.csv"):
        pass

    def SaveNews(self, fileName="NewsData.csv"):
        self.GetNews()
        csvwriter = csv.writer(open("test1.csv", "w"))
        csvwriter.writerow(("제목","언론사","날짜","기사원문"))
        for item in self.NewsData:
            csvwriter.writerow(item)
        

if __name__ == "__main__":
    api = NaverNewsAPI()
    api.RequestNewsLink("19대 대선", 1) #제안 : '이번 대선' 등으로 나타내는 경우도 있으므로 '대선' 이라고 찾은 뒤에 날짜로 필터링 
    crawler = NewsArticleCrawler() 
    crawler.LinkData = api.LinkData
    crawler.SaveNews()
    
