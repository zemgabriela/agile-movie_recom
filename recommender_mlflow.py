from spotlight.interactions import Interactions
from spotlight.factorization.explicit import ExplicitFactorizationModel
from spotlight.cross_validation import random_train_test_split
from spotlight.evaluation import rmse_score
import os
import pandas as pd
import numpy as np
import mlflow

movies_df = pd.read_csv('ml-latest-small/movies.csv', sep=',', names=['item_id', 'title', 'genres'], engine='python',skiprows=1)
tags_df = pd.read_csv('ml-latest-small/tags.csv', sep=',', names=['user_id', 'item_id', 'tag', 'timestamp'], engine='python',skiprows=1)
ratings_df = pd.read_csv('ml-latest-small/ratings.csv', sep=',', names=['user_id', 'item_id', 'rating', 'timestamp'], engine='python',skiprows=1)

def preprocessing(ratings_df,movies_df):
    ratings_df['user_id']=ratings_df['user_id'].astype('int32')
    ratings_df['item_id']=ratings_df['item_id'].astype('int32')
    ratings_df['timestamp']=ratings_df['timestamp'].astype('int32')
    movies_df[['title', 'year']] = movies_df['title'].str.extract(r'(.+) \((\d{4})\)')
    movies_df['title']=movies_df['title'].str.replace(', The', '')
    movies_df['genres']=movies_df['genres'].str.replace('|',', ') 
    nan_values = movies_df[movies_df.isna().any(axis=1)]
    movies_df=movies_df.dropna(axis=0)
    return ratings_df, movies_df

def training(ratings_df):
    interaction_data = Interactions(
        user_ids=ratings_df['user_id'].values,
        item_ids=ratings_df['item_id'].values,
        ratings=ratings_df['rating'].values,
        timestamps=ratings_df['timestamp'].values
    )
    train, test = random_train_test_split(interaction_data)

    model = ExplicitFactorizationModel(
        n_iter=5,          
        embedding_dim=32,
        learning_rate=0.01,  
        use_cuda=False      
    )
    model.fit(train, verbose=True)
    #here we save the parameters
    
    mlflow.log_param('factors', 32)
    mlflow.log_param('iterations', 5)
    mlflow.log_param('regularization', 0.01)
    mlflow.log_param('use_gpu', False)
    
    return model,train,test

def evaluation_model(model,train,test):
    train_rmse = rmse_score(model, train)
    test_rmse = rmse_score(model, test)
    return train_rmse,test_rmse


import os
with mlflow.start_run():
    #HERE WE CAN OPTIONALLY READ THE DATA
    movies_df = pd.read_csv('ml-latest-small/movies.csv', sep=',', names=['item_id', 'title', 'genres'], engine='python',skiprows=1)
    tags_df = pd.read_csv('ml-latest-small/tags.csv', sep=',', names=['user_id', 'item_id', 'tag', 'timestamp'], engine='python',skiprows=1)
    ratings_df = pd.read_csv('ml-latest-small/ratings.csv', sep=',', names=['user_id', 'item_id', 'rating', 'timestamp'], engine='python',skiprows=1)
    ratings_df, movies_df = preprocessing(ratings_df, movies_df)

    ratings_df.to_csv('temp_ratings.csv', index=False)
    movies_df.to_csv('temp_movies.csv', index=False)

    mlflow.log_artifact('temp_ratings.csv', artifact_path='preprocessed_data')
    mlflow.log_artifact('temp_movies.csv', artifact_path='preprocessed_data')

    os.remove('temp_ratings.csv')
    os.remove('temp_movies.csv')

    model,train,test=training(ratings_df)
    mlflow.sklearn.log_model(model, 'model')
    #mlflow.log_param('', ) here if we use parameters to check the best model
    
    train_rmse,test_rmse = evaluation_model(model,train,test)

    mlflow.log_metrics({'rmse train': train_rmse, 'rmse test': test_rmse})
