import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

# Compute the Cosine Similarity matrix based on the count_matrix
from sklearn.metrics.pairwise import cosine_similarity
from pandas.io.json import json_normalize
import pandas as pd
import pymongo
from pymongo import MongoClient
import pprint


client = MongoClient()
db = client.liber
books = db.books

def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        #Check if director exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ''

def create_soup(x):
    return ' '.join(x['key_words']) + ' ' + ' '.join(x['authors']  )#+ ' ' + ' '.join(x['genre'])
# books = books.find_one({})

for a in books.find():
    features = [ 'key_words', 'authors']

    for feature in features:
        a[feature] = clean_data(a[feature])
    print('o')
    # limpeza = clean_data(a)
    sopa = create_soup(a)
    print(sopa)
# director = get_director(cursor)
# print(director)
# testando= cursor['authors'].apply(clean_data)
# print(testando)
# soup_list = ['key_words', 'authors', 'genre']
# for x in soup_list:
# for y in cursor:
#     testando= y['authors'].apply(clean_data)
#     print(testando)
df = pd.json_normalize(books.find_one(), max_level=0)

# director = df['authors'].values
# print(director)