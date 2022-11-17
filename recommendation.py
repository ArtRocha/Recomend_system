import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
# Compute the Cosine Similarity matrix based on the count_matrix
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId
import argparse
import json

#RECEBE O ID DO USUÁRIO
    #O id do usuário deve ser passado como string 
    #EXEMPLO DE CHAMADA "python recommendation.py -uid {id_usuario}"
# parser = argparse.ArgumentParser()
# parser.add_argument("-uid", "--userId",type=str)
# args = parser.parse_args()

# id = args.userId
# id= ObjectId(id)

id= ObjectId('63729f16011783b55d9423f5')

#MONGO CONECCTION
client = MongoClient()
db = client.liber
books = db.books
users = db.users
ads = db.ads

# user_id = users.find_one({"_id": id})
# id = user_id["_id"]


#PIPELINES
pipeline_books = [
    {
        "$lookup": {
            "from": "genres", 
            "localField": "genre", 
            "foreignField": "_id", 
            "as": "result"
        }
    }, {
        '$project': {
            'createdAt': 0, 
            'updatedAt': 0, 
            'result.createdAt': 0, 
            'result.updatedAt': 0
        }
    }
]

pipeline_users = [
    {
        "$match": {
            "_id": id
        }
    }, {
        "$lookup": {
            "from": "genres", 
            "localField": "genres", 
            "foreignField": "_id", 
            "as": "result"
        }
    }, {
        '$project': {
            'createdAt': 0, 
            'updatedAt': 0, 
            'result.createdAt': 0, 
            'result.updatedAt': 0
        }
    }
]



def take_genre(x):
    if isinstance(x,list):
        return [i["name"] for i in x]
    return np.nan


def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        #Check if director exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ""

def create_soup(x):
    return " ".join(x["key_words"]) + " " + " ".join(x["authors"]) + " " + " ".join(x["result"])

def get_books_recommendations(user_id, cosine_sim):
    # Get the index of the movie that matches the title
    idx = indices[user_id]

    # Get the pairwsie similarity scores of all movies with that movie
    # Sort the movies based on the similarity scores
    sim_scores = df2[idx].sort_values(ascending=False)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:60]

    # Get the movie indices
    books_indices = [i for i in sim_scores.index]

    # Return the top 10 most similar movies
    return books_indices


bank = []
for user in users.aggregate(pipeline_users):
    user["result"] = take_genre(user["result"])
    user["result"] = clean_data(user["result"])
    user["sopa"] = " ".join(user["result"])
    user["title"] = user["name"]
    bank.append(user)

for a in (books.aggregate(pipeline_books)):
    genre_list=[]
    features = [ "key_words", "authors", "result"]

    for feature in features:
        if feature == "result":
            a[feature] =  take_genre(a[feature])
        a[feature] = clean_data(a[feature])
    a["sopa"] = create_soup(a)
    bank.append(a)

df = pd.json_normalize(bank, max_level=0)
df = df.set_index("_id")

count = CountVectorizer(stop_words="english")
#matriz que atribui peso as palavras
count_matrix = count.fit_transform(df["sopa"])

#calculando a similaridade entre os filmes baseando-se nas palavras passadas
cosine_sim2 = cosine_similarity(count_matrix)
indices = pd.Series(df.index, index=df.index)
df2 = pd.DataFrame(cosine_sim2, columns=df.index, index=df.index)

book_id = get_books_recommendations(id, df2)

ads_pipeline = [
    {
        '$lookup': {
            'from': 'users', 
            'localField': 'id_user', 
            'foreignField': '_id', 
            'as': 'user'
        }
    }, {
        '$lookup': {
            'from': 'books', 
            'localField': 'id_book', 
            'foreignField': '_id', 
            'as': 'book'
        }
    }, {
        '$match': {
            'id_book': {
                '$in': book_id
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
    rest_recommendation =[]
    for  ad in query:
        ad['_id'] = str(ad['_id'])
        ad['id_user'] = str(ad['id_user'])
        ad['id_book'] = str(ad['id_book'])
        ad['user'][0]['_id'] = str(ad['user'][0]['_id'])
        if "id_user_buy" in ad != None: ad['id_user_buy'] = str(ad['id_user_buy'])
        for key,adUser in enumerate(ad['user'][0]['genres']):
            ad['user'][0]['genres'][key] = str(adUser)
        if len(premium_recommend) <=14:
            if ad["user"][0]["account_type"]=="premium":
                premium_recommend.append(ad)
        elif ad["user"][0]["account_type"]=="standard" or ad["user"][0]["account_type"]=="premium":
            rest_recommendation.append(ad)     
    return {"premium": premium_recommend, "res_recommend":rest_recommendation}


# get_ads_recommendations()

reco = get_ads_recommendations()



print(json.dumps(reco))
# print("___"*30)
# print(json.dumps(reco["res_recommend"]))