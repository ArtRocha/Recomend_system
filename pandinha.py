import pandas as pd
from pandas_profiling import ProfileReport
from pymongo import MongoClient

#MONGO CONECCTION
client = MongoClient()
db = client.liber
books = db.books
users = db.users
ads = db.ads


take_books = books.find({})
df_books = pd.json_normalize(take_books, max_level=0)
profile_books = ProfileReport(df_books, title='Books overview')

take_users = users.find({})
df_users = pd.json_normalize(take_users, max_level=0)
profile_users = ProfileReport(df_users, title='Users overview')

take_ads = users.find({})
df_ads = pd.json_normalize(take_ads, max_level=0)
profile_ads = ProfileReport(df_ads , title='Ads overview')

# profile_books.to_file('booksReport.html')
profile_users.to_file('usersReport.html')
profile_ads.to_file('adsReport.html')
