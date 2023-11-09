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









def recommend_table2(user_id,tfidf_data, movie_count=20):
    #print(tfidf_data,"OK")
    
    
    tfidf_data=tfidf_data.loc[tfidf_data["Id"].astype(str)==user_id]

    
    return  tfidf_data[:movie_count]


#@st.cache(persist=True, show_spinner=False, suppress_st_warning=True)



def load_data2():
    """
    load and cache data
    :return: tfidf data
    """
    tfidf_data = pd.read_csv("recommended_movies2.csv",delimiter=",")
    print(tfidf_data)
    tfidf_data.columns=["Number","Title","Id"]
    tfidf_data["Id"]=tfidf_data["Id"].astype(str)
    return tfidf_data

#tfidf = load_data()
tfidf = load_data2()
#with open("movie_list.pickle", "rb") as f:
#    movies = pickle.load(f)

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

#session.options = st.multiselect(label="Select Movies", options=movies)
session.user_id=st.text_input(label="Write your user id")
st.text("")
st.text("")

session.slider_count = st.slider(label="movie_count", min_value=1, max_value=5)

st.text("")
st.text("")

buffer1, col1, buffer2 = st.columns([1.45, 1, 1])

is_clicked = col1.button(label="Recommend")

#if is_clicked:
#    dataframe = recommend_table(session.options, movie_count=session.slider_count, tfidf_data=tfidf)


if is_clicked:
    dataframe = recommend_table2(session.user_id,movie_count=session.slider_count, tfidf_data=tfidf)

st.text("")
st.text("")
st.text("")
st.text("")

if dataframe is not None:

    #st.table(dataframe)
    if str(session.user_id) in user_ids:
        st.write(dataframe.to_html(index=False), unsafe_allow_html=True)
    else:
        st.write("Sorry, it seems that your User ID is not correct")
