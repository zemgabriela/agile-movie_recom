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
nltk.download('stopwords')
nltk.download('punkt')
from nltk import word_tokenize
from nltk.corpus import stopwords


def recommend_table(user_id,tfidf_data, movie_count=20):
 
    
    tfidf_data=tfidf_data.loc[tfidf_data["Id"].astype(str)==user_id]
    print(tfidf_data)
    
    return  tfidf_data[:movie_count]


#@st.cache(persist=True, show_spinner=False, suppress_st_warning=True)

def load_data():
    """
    load and cache data
    :return: tfidf data
    """
    tfidf_data = pd.read_csv("data/recommended_movies2.csv",delimiter=",")

    tfidf_data.columns=["Number","Title","Id"]
    tfidf_data["Id"]=tfidf_data["Id"].astype(str)
    return tfidf_data

tfidf = load_data()
user_ids=list(tfidf["Id"])
dataframe = None

st.title("""
Recommendation System for Agile
This is an Content Based Recommender System for each user and customize quantity of recommendations 😎.
 """)

st.text("")
st.text("")
st.text("")
st.text("")

session.user_id=st.text_input(label="Write your user id")
st.text("")
st.text("")

session.slider_count = st.slider(label="movie_count", min_value=1, max_value=5)

st.text("")
st.text("")

buffer1, col1, buffer2 = st.columns([1.45, 1, 1])

is_clicked = col1.button(label="Recommend")

if is_clicked:
    dataframe = recommend_table(session.user_id,movie_count=session.slider_count, tfidf_data=tfidf)

st.text("")
st.text("")
st.text("")
st.text("")


from PIL import Image

url = "http://api.themoviedb.org/3/genre/movie/list?api_key=8dd915995c815307e7dd3dd84482e7b7"

headers = {"accept": "application/json"}

#st.write("This is :blue[test]")
#r = requests.post(url, headers=headers, files=files)
list_genres = requests.get(url, headers=headers).json()['genres']
df_genres=pd.DataFrame(list_genres)
#http://api.themoviedb.org/3/genre/movie/list?api_key=####
if dataframe is not None:

    if str(session.user_id) in user_ids:
        #st.write(df_genres.to_html(index=False), unsafe_allow_html=True)
        for title in dataframe["Title"]:
            print(list_genres)

            #original_title = '<p style="font-family:Courier; color:Blue; font-size: 20px;">"++'</p>'
            #st.markdown(original_title, unsafe_allow_html=True)
            #title="Jack Reacher"

            title=title.replace(" ","+")
            url = "https://api.themoviedb.org/3/search/movie?query="+title+"&api_key=8dd915995c815307e7dd3dd84482e7b7"

            headers = {"accept": "application/json"}


            #r = requests.post(url, headers=headers, files=files)
            response = requests.get(url, headers=headers).json()['results'][0]
    
            photo_path="https://image.tmdb.org/t/p/w185/"+response['poster_path']
            print(photo_path)
            title=response['title']
            description=response['overview']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(
                    photo_path,
                    width=200, 
                )
            with col2:
                st.write("Title")
                st.write("Genres")
                st.write("Overview")

            with col3:
                st.write(title)
                
                name_genre=""
                for genre_id in response['genre_ids']:
                    aux_=df_genres.loc[df_genres["id"]==genre_id,"name"].iloc[0]
                    name_genre=name_genre+", "+aux_
                st.write(name_genre[1:])
                if len(description)>225:
                    st.write(description[:225]+"...")
                else:
                    st.write(description[:230])

                


            
            #st.image(image, caption='Sunrise by the mountains')
    else:
        st.write("Sorry, it seems that your User ID is not correct")
