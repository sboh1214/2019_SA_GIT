from .NewsCrawling.NewsCrawling import NaverNewsAPI, NewsArticleCrawler

from multiprocessing import Pool

Keyword = ["대선"]
Processes = 8

pool = Pool()
for keyword in Keyword:
    print(f"Request Keyword : {keyword}")
    for i in range(1, 101):
        api = NaverNewsAPI()
        api.RequestNewsByDate(keyword)
        crawler = NewsArticleCrawler(api.LinkData)
        crawler.SaveNews()
