import NewsCrawling as NC
import NewsEvaluating as NE
import NewsLearning as NL

Keyword = "대선"
for i in range(1, 100):
    api = NC.NaverNewsAPI()
    print("Request ("+str(i+1)+") : "+api.RequestNewsLink(Keyword, i))