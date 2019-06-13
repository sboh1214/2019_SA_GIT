from NewsCrawling import *
#from NewsEvaluating import *
from NewsLearning import *

from tqdm import tqdm

Keyword = ["대선"]
for keyword in Keyword:
    print(f"Request Keyword : {keyword}")
    for i in range(1, 101):
        api = NaverNewsAPI()
        api.RequestNewsByDate(keyword)
        crawler = NewsArticleCrawler()
        crawler.LinkData = api.LinkData
        crawler.SaveNews()
