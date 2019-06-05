import json

class KnuSL():

    def data_list(wordname):
        with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
			data = json.load(f)
        result=[None,None]