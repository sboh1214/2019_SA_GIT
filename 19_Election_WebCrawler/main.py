from NewsCrawling import *
from NewsEvaluating import *
from NewsLearning import *

from tqdm import tqdm

Keyword = ["대선"]
for keyword in Keyword:
    for i in tqdm(range(1, 101)):
        api = NaverNewsAPI()
        print(f"Request {str(i)} : {api.RequestNewsLink(keyword, i)}")
    