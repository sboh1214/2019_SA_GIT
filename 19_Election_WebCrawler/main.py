from NewsCrawling import *
#from NewsEvaluating import *
from NewsLearning import *

from tqdm import tqdm

Keyword = ["대선"]
for keyword in Keyword:
    for i in range(1, 101):
        api = NaverNewsAPI()
        api.RequestNewsByDate(keyword)
    