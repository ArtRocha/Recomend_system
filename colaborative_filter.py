from sklearn.neighbors import NearestNeighbors
import pandas as pd

'''
PASSO A PASSO

# get the index for 'movie_0'
index_for_movie = df.index.tolist().index('movie_0')

# find the indices for the similar movies
sim_movies = indices[index_for_movie].tolist()

# distances between 'movie_0' and the similar movies
movie_distances = distances[index_for_movie].tolist()

# the position of 'movie_0' in the list sim_movies
id_movie = sim_movies.index(index_for_movie)

# remove 'movie_0' from the list sim_movies
sim_movies.remove(index_for_movie)

# remove 'movie_0' from the list movie_distances
movie_distances.pop(id_movie)
print('The Nearest Movies to movie_0:', sim_movies)
print('The Distance from movie_0:', movie_distances)

'''
def recommend_movies(user, num_recommended_movies):
    
  print('The list of the Movies {} Has Watched \n'.format(user))

  #loop que pega os livros lidos
  for m in df[df[user] > 0][user].index.tolist():
    print(m)
  
  print('\n')

  recommended_movies = []

  #loop que pega os livros não lidos para recomendar
  for m in df[df[user] == 0].index.tolist():

    index_df = df.index.tolist().index(m)
    predicted_rating = df1.iloc[index_df, df1.columns.tolist().index(user)]
    recommended_movies.append((m, predicted_rating))

  sorted_rm = sorted(recommended_movies, key=lambda x:x[1], reverse=True)
  
  print('The list of the Recommended Movies \n')
  rank = 1
  for recommended_movie in sorted_rm[:num_recommended_movies]:
    
    print('{}: {} - predicted rating:{}'.format(rank, recommended_movie[0], recommended_movie[1]))
    rank = rank + 1

# store the original dataset in 'df', and create the copy of df, df1 = df.copy().
def movie_recommender(user, num_neighbors, num_recommendation):

  number_neighbors = num_neighbors

  knn = NearestNeighbors(metric='cosine', algorithm='brute')
  knn.fit(df.values)
  distances, indices = knn.kneighbors(df.values, n_neighbors=number_neighbors)

  user_index = df.columns.tolist().index(user)

  for m,t in list(enumerate(df.index)):
    if df.iloc[m, user_index] == 0:
      sim_movies = indices[m].tolist()
      movie_distances = distances[m].tolist()
    
      if m in sim_movies:
        id_movie = sim_movies.index(m)
        sim_movies.remove(m)
        movie_distances.pop(id_movie) 

      else:
        sim_movies = sim_movies[:number_neighbors-1]
        movie_distances = movie_distances[:number_neighbors-1]
           
      movie_similarity = [1-x for x in movie_distances]
      movie_similarity_copy = movie_similarity.copy()
      nominator = 0

      for s in range(0, len(movie_similarity)):
        if df.iloc[sim_movies[s], user_index] == 0:
          if len(movie_similarity_copy) == (number_neighbors - 1):
            movie_similarity_copy.pop(s)
          
          else:
            movie_similarity_copy.pop(s-(len(movie_similarity)-len(movie_similarity_copy)))
            
        else:
          nominator = nominator + movie_similarity[s]*df.iloc[sim_movies[s],user_index]
          
      if len(movie_similarity_copy) > 0:
        if sum(movie_similarity_copy) > 0:
          predicted_r = nominator/sum(movie_similarity_copy)
        
        else:
          predicted_r = 0

      else:
        predicted_r = 0
        
      df1.iloc[m,user_index] = predicted_r
  recommend_movies(user, num_recommendation)

ratings = pd.read_csv('ratings.csv', usecols=['userId','movieId','rating'])
movies = pd.read_csv('movies.csv', usecols=['movieId','title'])
ratings2 = pd.merge(ratings, movies, how='inner', on='movieId')

df = ratings2.pivot_table(index='title',columns='userId',values='rating').fillna(0)
df1 = df.copy()



# recommend_movies('u9', 4)
movie_recommender(15, 10, 400)