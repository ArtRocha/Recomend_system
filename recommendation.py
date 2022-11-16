import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
# Compute the Cosine Similarity matrix based on the count_matrix
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId
import argparse
from ast import literal_eval
import pprint
parser = argparse.ArgumentParser()
parser.add_argument("-uid", '--userId',type=str)
args = parser.parse_args()

id = args.userId
id= ObjectId(id)

#MONGO CONECCTION
client = MongoClient()
db = client.liber
books = db.books
users = db.users
ads = db.ads

user_id = users.find_one({'_id': id})
id = user_id['_id']


#PIPELINES
pipeline_books = [
    {
        '$lookup': {
            'from': 'genres', 
            'localField': 'genre', 
            'foreignField': '_id', 
            'as': 'result'
        }
    }
]

pipeline_users = [
    {
        '$match': {
            '_id': id
        }
    }, {
        '$lookup': {
            'from': 'genres', 
            'localField': 'genres', 
            'foreignField': '_id', 
            'as': 'result'
        }
    }
]



def take_genre(x):
    if isinstance(x,list):
        return [i['name'] for i in x]
    return np.nan


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
    return ' '.join(x['key_words']) + ' ' + ' '.join(x['authors']) + ' ' + ' '.join(x['result'])

def get_books_recommendations(user_id, cosine_sim):
    # Get the index of the movie that matches the title
    idx = indices[user_id]

    # Get the pairwsie similarity scores of all movies with that movie
    # Sort the movies based on the similarity scores
    sim_scores = df2[idx].rank(ascending=0, method='first')

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores

    # Get the movie indices
    movie_indices = [i for i in sim_scores.index]

    # Return the top 10 most similar movies
    return movie_indices


bank = []
for user in users.aggregate(pipeline_users):
    user['result'] = take_genre(user['result'])
    user['result'] = clean_data(user['result'])
    user['sopa'] = ' '.join(user['result'])
    user['title'] = user['name']
    bank.append(user)

for a in (books.aggregate(pipeline_books)):
    genre_list=[]
    features = [ 'key_words', 'authors', 'result']

    for feature in features:
        if feature == 'result':
            a[feature] =  take_genre(a[feature])
        a[feature] = clean_data(a[feature])
    a['sopa'] = create_soup(a)
    bank.append(a)

df = pd.json_normalize(bank, max_level=0)
df = df.set_index('_id')

count = CountVectorizer(stop_words='english')
#matriz que atribui peso as palavras
count_matrix = count.fit_transform(df['sopa'])

#calculando a similaridade entre os filmes baseando-se nas palavras passadas
cosine_sim2 = cosine_similarity(count_matrix)
indices = pd.Series(df.index, index=df.index)
df2 = pd.DataFrame(cosine_sim2, columns=df.index, index=df.index)

movie_id = get_books_recommendations(id, df2)

ads_pipeline = [
    {
        '$lookup': {
            'from': 'users', 
            'localField': 'id_user', 
            'foreignField': '_id', 
            'as': 'user'
        }
    }, {
        '$match': {
            'id_book': {
                '$in': movie_id
            }
        }
    }, {
        '$match': {
            '$or': [
                {
                    'user.account_type': 'premium'
                }, {
                    'user.account_type': 'standard'
                }
            ]
        }
    }
]

def get_ads_recommendations(query=ads.aggregate(ads_pipeline)):
    premium_recommend = []
    recommendation =[]
    for  ad in query:
        if len(premium_recommend) <=14:
            if ad['user'][0]['account_type']=='premium':
                premium_recommend.append(ad)
        elif ad['user'][0]['account_type']=='standard' or ad['user'][0]['account_type']=='premium':
            recommendation.append(a)     
    return {'premium': premium_recommend, 'recommend':recommendation}

reco = get_ads_recommendations()
pprint.pprint(reco['premium'])
print("___"*30)
pprint.pprint(reco['recommend'])
