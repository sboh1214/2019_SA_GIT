from tensorflow import keras
import keras
from tqdm import tqdm
import csv
import keras
from khaiii import KhaiiiApi

def GetMorpheme(sentence):
    api = KhaiiiApi()
    dic = {}
    for word in api.analyze(sentence): 
        morphs_str = ' + '.join([(m.lex + '/' + m.tag) for m in word.morphs])
        print(f'{word.lex}\t{morphs_str}')

class NewsML:
    Title = []
    Press = []
    Date = []
    Content = []

    Model = None

    def GetNewsData(fileName):
        f = open(fileName+'.csv', 'r', encoding='utf-8')
        rdr = csv.reader(f)
        for line in tqdm(rdr):
            Title.append(line['Title'])
            Press.append(line['Press'])
            Date.append(line['Date'])
            Content.append(line['Content'])
        f.close()

    def BuildModel(vocab_size, embedding_dim, rnn_units, batch_size):
        model = keras.Sequential([
            keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape=[batch_size, None]),
            keras.layers.LSTM(rnn_units, return_sequences=True, stateful=True, recurrent_initializer='glorot_uniform'),
            keras.layers.Dense(vocab_size)
            ])
        return model

    def FitModel(model):
        model.compile()
        model.fit()
