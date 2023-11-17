import pickle
import pandas as pd
import streamlit as st
from streamlit import session_state as session
import requests
import pandas as pd
import numpy as np
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#nltk.download('stopwords')
#nltk.download('punkt')
from nltk import word_tokenize
from nltk.corpus import stopwords
from joblib import load


# function for loading the movie dataset
def load_movie_data():
    """
    load and cache data
    :return: tfidf data
    """
    movies_df = pd.read_csv('ml-latest-small/movies.csv', sep=',', names=['item_id', 'title', 'genres'], engine='python',skiprows=1)

    movies_df['year'] = movies_df['title'].str.extract(r'\((\d{4}(?:–\d{4})?)\)')  # Extracting the year or year range into a new column
    movies_df['year'] = movies_df['year'].where(movies_df['year'].str.len() == 4, None)  # Set to None if not a single year
    movies_df['title'] = movies_df['title'].str.replace(r'\(\d{4}(?:–\d{4})?\)', '', regex=True).str.strip()  # Removing the year from the title

    movies_df['title']=movies_df['title'].str.replace(', The', '')
    movies_df['genres']=movies_df['genres'].str.replace('|',', ')

    return movies_df

movies_df = load_movie_data()

# function for loading the model stored 
def load_model():
    model = load('model.pkl')
    return model

model = load_model()

unique_genres=['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX', 'Musical', 
                'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'] 

min_year=movies_df['year'].min()
max_year=movies_df['year'].max()
years=np.unique(movies_df['year']) #list of years
#if you need to sort them: years=sorted(years, reverse=True)

def recommended_movies_by_user(model, user_id, n_movies, movies_df, genres=None, start_year=None, end_year=None):
    # Apply genre/year filters before making predictions
    if genres is not None:
        filter_condition = lambda x: any(genre.lower() in x.lower() for genre in genres)
        movies_df = movies_df[movies_df['genres'].apply(filter_condition)]
    if start_year is not None:
        if end_year is not None:
            movies_df = movies_df[(movies_df['year'] >= start_year) & (movies_df['year'] <= end_year)]
        else:
            movies_df = movies_df[movies_df['year'] >= start_year]

    # Now predict scores for the (optionally) filtered items for the user
    filtered_movie_ids = movies_df['item_id'].values
    pred = model.predict(user_ids=np.array([user_id]*len(filtered_movie_ids)), item_ids=filtered_movie_ids)

    # Sort predicted ratings in descending order
    sorted_indices = np.argsort(pred)[::-1]
    #print(len(sorted_indices))
    # Select the top n_movies
    top_indices = sorted_indices[:n_movies]
    recommended_movies = movies_df.iloc[top_indices]['title'].tolist()
    predicted_ratings = pred[top_indices]

    # Create DataFrame with rating, movie title, and user_id
    results_df = pd.DataFrame({
        'Number': predicted_ratings,
        'Title': recommended_movies['title'],
        'Id': user_id
    })

    return results_df

dataframe = None
user_ids=list()

st.title("""
Recommendation System for Agile
This is a Content Based Recommender System for each user and it customizes the quantity of recommendations 😎.
 """)

st.text("")
st.text("")
st.text("")
st.text("")

session.user_id = st.text_input(label="Write your user id")
st.text("")
st.text("")

session.slider_count = st.slider(label="movie_count", min_value=1, max_value=10)

st.text("")
st.text("")

buffer1, col1, buffer2 = st.columns([1.45, 1, 1])

is_clicked = col1.button(label="Recommend")

if is_clicked:
    # Ensure user_id is converted to the correct type
    user_id = int(session.user_id) if session.user_id.isdigit() else None
    if user_id is not None:
        dataframe = recommended_movies_by_user(model=model, user_id=user_id, n_movies=session.slider_count, movies_df=movies_df)
        st.write(dataframe)
