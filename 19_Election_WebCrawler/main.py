from NewsCrawling import *
from NewsEvaluating import *
from NewsLearning import *

from tqdm import tqdm

Keyword = ["대선"]
for keyword in Keyword:
    for i in tqdm(range(1, 101), desc=f" {keyword}"):
        api = NaverNewsAPI()
        api.RequestNewsLink(keyword, i)
    