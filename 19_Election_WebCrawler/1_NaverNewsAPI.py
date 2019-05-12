import urllib.request
import json
import csv
import re
#import beautifulsoup4 as bs


Client_ID = 'Mo_tHONZPPs7OeNzZQAE'
Client_Secret = 'vVve0WqXE5'

class NaverNewsAPI:

    Data = []
    
    def RequestNewsLink(self, query, n=1, display=100, sort="sim"):
        if n<1 or n>1000:
            return "Error (invalid n)"
        if display<1 or display>100:
            return "Error (invalid display)"

        q = urllib.parse.quote(query)
        url = "https://openapi.naver.com/v1/search/news?query=" + q + "&display="+str(display)+"&sort=" + sort + "&start="+str(n)
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", Client_ID)
        request.add_header("X-Naver-Client-Secret", Client_Secret)
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
            self.Data.append({"Title":title,"Link": link, "OriginalLink":originalLink})

    def SaveNewsLinkCSV(self, fileName = "NewsLink.csv"):
        f = open(fileName, 'w', encoding='utf-8', newline='')
        csvFile = csv.writer(f)
        for item in self.Data:
            title = item['title']
            link = item['link']
            originalLink = item['originallink']
            csvFile.writerow([title, link, originalLink])
        return "Success"

    def MakePlainText(self, title):
        print(title)
        title = re.sub('\"\'','',title)
        #html 태그 제거
        title = re.sub('<[/A-Za-z]*>','',title)
        title = re.sub('&[A-Za-z]*;','',title)
        #한자 변경
        title = re.sub('與', '여당', title)
        title = re.sub('野','야당', title)
        title = re.sub('朴', '박근혜', title)
        title =re.sub('文','문재인', title)
        title = re.sub('號', '호', title)
        return title

    def OpenNewsLinkCSV(self, fileName):
        pass

class NewsArticleCrawler:
    Data=[]
    def GetNews(self):
        
    

if __name__ == "__main__":
    naverNewsAPI = NaverNewsAPI()
    naverNewsAPI.RequestNewsLink("19대 대선",1)
    naverNewsAPI.SaveNewsLinkCSV()


# TODO : Beautifulsoup 활용해서 내용 추출
