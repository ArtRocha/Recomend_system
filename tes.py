from pymongo import MongoClient
import os

path = os.path.dirname(os.path.realpath('__file__'))+os.sep

#MONGO CONECCTION
client = MongoClient()
db = client.liber
books = db.books
users = db.users
ads = db.ads

user_id = db.users.find_one({})
id = user_id['_id']
id = str(id)

string_cmd = (f'python {path}recommendation.py -uid {id}')
os.system(string_cmd)
