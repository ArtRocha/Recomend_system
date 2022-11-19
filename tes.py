from pymongo import MongoClient
import os

path = os.path.dirname(os.path.realpath('__file__'))+os.sep

# #MONGO CONECCTION
# client = MongoClient()
# db = client.liber
# books = db.books
# users = db.users
# ads = db.ads

# user_id = db.users.find_one({})
# id = user_id['_id']
# id = str(id)
ads='F'
book='T'
user='F'
string_cmd = (f'python {path}reports.py -ads {ads} -use {user} -boo {book}')
os.system(string_cmd)
