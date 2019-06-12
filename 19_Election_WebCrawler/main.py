from NewsCrawling import *
from NewsEvaluating import *
from NewsLearning import *

Keyword = "대선"
for i in range(1, 101):
    api = NaverNewsAPI()
    print("Request ("+str(i)+") : "+api.RequestNewsLink(Keyword, i))
    