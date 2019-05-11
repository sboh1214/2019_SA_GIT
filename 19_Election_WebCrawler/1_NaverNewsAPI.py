import urllib.request
import json
import csv
import re
#import beautifulsoup4 as bs


Client_ID = 'Mo_tHONZPPs7OeNzZQAE'
Client_Secret = 'vVve0WqXE5'

class NaverNewsAPI:

    def RequestNewsLink(query, n, display=100, sort="sim"):
        q = urllib.parse.quote(query)
        url = "https://openapi.naver.com/v1/search/news?query=" + q + "&display="+str(display)+"&sort=" + sort
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", Client_ID)
        request.add_header("X-Naver-Client-Secret", Client_Secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode != 200):
            print("Error Code:" + rescode)
            return "Error" + rescode
        else:
            response_body = response.read()
            return response_body.decode('utf-8')
    
    def SaveNewsLinkCSV(jsonData, fileName = "NewsLink.csv"):
        json_data = json.loads(jsonData)
        json_items = json_data['items']
        f = open(fileName, 'w', encoding='utf-8', newline='')
        csvFile = csv.writer(f)
        for item in json_items:
            title = NaverNewsAPI.MakePlainText(item['title'])
            link = item['link']
            originalLink = item['originallink']
            csvFile.writerow([title, link, originalLink])
        return True

    def MakePlainText(title):
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

    def LoadNewsLinkCSV(jsonData):
        jsonData

if __name__ == "__main__":
    jsonData = NaverNewsAPI.RequestNewsLink("19대 대선",1)
    NaverNewsAPI.SaveNewsLinkCSV(jsonData)

# TODO : Beautifulsoup 활용해서 내용 추출
