import pickle
import pandas as pd
import streamlit as st
from streamlit import session_state as session
#from src.recommend.recommend import recommend_table
import pandas as pd
import numpy as np
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nltk.download('stopwords')
nltk.download('punkt')
from nltk import word_tokenize
from nltk.corpus import stopwords
import time
start_time = time.time()

movies_df = pd.read_csv('ml-latest-small/movies.csv', sep=',', names=['item_id', 'title', 'genres'], engine='python',skiprows=1)
tags_df = pd.read_csv('ml-latest-small/tags.csv', sep=',', names=['user_id', 'item_id', 'tag', 'timestamp'], engine='python',skiprows=1)
ratings_df = pd.read_csv('ml-latest-small/ratings.csv', sep=',', names=['user_id', 'item_id', 'rating', 'timestamp'], engine='python',skiprows=1)


ratings_df['user_id']=ratings_df['user_id'].astype('int32')
ratings_df['item_id']=ratings_df['item_id'].astype('int32')
ratings_df['timestamp']=ratings_df['timestamp'].astype('int32') #It is required by the model

movies_df[['title', 'year']] = movies_df['title'].str.extract(r'(.+) \((\d{4})\)')

movies_df['title']=movies_df['title'].str.replace(', The', '')
movies_df['genres']=movies_df['genres'].str.replace('|',', ')


from spotlight.interactions import Interactions
from spotlight.factorization.explicit import ExplicitFactorizationModel
from spotlight.cross_validation import random_train_test_split
from spotlight.evaluation import rmse_score
# Step 2: Create the Interactions object
interaction_data = Interactions(
    user_ids=ratings_df['user_id'].values,
    item_ids=ratings_df['item_id'].values,
    ratings=ratings_df['rating'].values,
    timestamps=ratings_df['timestamp'].values
)

# Split the interaction data into training and test sets
train, test = random_train_test_split(interaction_data)

# Initialize the model
model = ExplicitFactorizationModel(
    n_iter=5,           # Number of epochs of training
    embedding_dim=32,   # Latent factors (embedding size)
    use_cuda=False      # If you have a CUDA capable GPU, set to True to speed up training
)

# Fit the model on the training data
model.fit(train, verbose=True)

train_rmse = rmse_score(model, train)
test_rmse = rmse_score(model, test)

elapsed_time = time.time() - start_time
print(elapsed_time)

def recommended_movies_by_user(model, user_id, n_movies):
    pred=model.predict(user_ids=user_id)
    sorted_indices = np.argsort(pred)[::-1] #we sort the indices 
    top_indices = sorted_indices[:n_movies]+1 #we extract the top n_movies. Now we have to extract the title of the associated movies to give the recommendation
    recommended_movies = movies_df[movies_df['item_id'].isin(top_indices)]['title'].values.tolist() #we extract the movies with that id
    
    #
    df_recommended=pd.DataFrame(recommended_movies)
    df_recommended.columns=["Title"]
    df_recommended["User ID"]=user_id

    return df_recommended

df_final=pd.DataFrame()
for user in ratings_df['user_id'].unique():
    aux_x=recommended_movies_by_user(model=model, user_id=user, n_movies=5)
    df_final=pd.concat([df_final,aux_x])
df_final.columns=["Title","User ID"]
df_final.to_csv("recommended_movies2.csv")
print(len(ratings_df['user_id'].unique()))

