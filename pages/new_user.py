import pickle
import pandas as pd
import streamlit as st
from streamlit import session_state as session
import requests
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from joblib import dump, load
import numpy as np
def recommend_table(user_id,tfidf_data, movie_count=20):
 
    
    tfidf_data=tfidf_data.loc[tfidf_data["Id"].astype(str)==user_id]
    print(tfidf_data)
    
    return  tfidf_data[:movie_count]


#@st.cache(persist=True, show_spinner=False, suppress_st_warning=True)

def load_data():

    tfidf_data =  pd.read_csv('ml-latest-small/movies.csv', sep=',', names=['item_id', 'title', 'genres'], engine='python',skiprows=1)

    #tfidf_data['title'] = tfidf_data['title'].str.replace(r'\(\d{4}(?:–\d{4})?\)', '', regex=True).str.strip()
    return tfidf_data

movies_df = load_data()
def recommend_next_movies(list_of_movies, model, n_movies, genre=None):
    # We first check if the titles are in the movie list and remove the ones that are not present.
    # We also convert the titles in order to avoid case sensitivity (e.g., 'Spiderman' vs. 'spiderman').
    list_of_movies = [title.lower() for title in list_of_movies]
    list_of_movies = [title for title in list_of_movies if title in movies_df['title'].str.lower().tolist()]
    if not list_of_movies:  # Check if it is empty.
        return 'The list of films provided is not in the catalogue'
    # Get the indices for the movies.
    indices_movies = movies_df[movies_df['title'].str.lower().isin(list_of_movies)]['item_id']
    # Predict the next movies.
    pred = model.predict(sequences=np.array(indices_movies))
    sorted_indices = np.argsort(pred)[::-1]
    
    # Filter out the movies that have already been seen
    sorted_indices = [idx for idx in sorted_indices if idx not in indices_movies.values]
    
    # Apply genre filtering if genre is specified.
    if genre:
        genre_mask = movies_df['genres'].str.contains(genre, case=False, na=False)
        # Use the mask to filter indices
        filtered_indices = genre_mask.index[genre_mask].intersection(sorted_indices)
        # Get the top n_movies indices from the filtered list
        top_indices = filtered_indices[:n_movies]
    else:
        # If no genre filter is applied, simply take the top n_movies indices
        top_indices = sorted_indices[:n_movies]
        
    # Get the recommended movie titles.
    recommended_movies = movies_df[movies_df['item_id'].isin(top_indices)]['title'].values.tolist()

    return recommended_movies


tfidf = load_data()

movies=list(tfidf["title"].unique())






@st.cache_data()
def load_model():
    model = load('model_seq.pkl') 

    return model


model=load_model()




col1, col2= st.columns([3, 1])
with col1:
    st.title("""
    Welcome new user """)

    st.text("")
with col2:
    st.text("")
    st.text("")
    if st.button('Home'):
        switch_page('Home')



movies.sort()
par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">Select your favorites movies.</p>'
st.markdown(par2, unsafe_allow_html=True)

list_of_movies = st.multiselect(label="", options=movies)

#session.user_id=st.text_input(label="Write your user id")

st.text("")


st.text("")
par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">Choose how many movie recommendations do you want.</p>'
st.markdown(par2, unsafe_allow_html=True)
n_movies  = st.slider(label="",min_value=1, max_value=5)

st.text("")
st.text("")

buffer1, col1, buffer2 = st.columns([1.45, 1, 1])

is_clicked = col1.button(label="Recommend")
st.text("")
st.text("")
st.text("")
st.text("")


#st.set_page_config(initial_sidebar_state="collapsed") 
st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )



from PIL import Image

url = "http://api.themoviedb.org/3/genre/movie/list?api_key=8dd915995c815307e7dd3dd84482e7b7"

headers = {"accept": "application/json"}

list_genres = requests.get(url, headers=headers).json()['genres']




import re


if is_clicked:
    dataframe = recommend_next_movies(list_of_movies, model, n_movies, genre=None)




    for title in dataframe:


        title=title.replace(" ","+")
        title=re.sub(r'\(\d{4}(?:–\d{4})?\)', '', title).strip()
        url = "https://api.themoviedb.org/3/search/movie?query="+title+"&api_key=8dd915995c815307e7dd3dd84482e7b7"

        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers).json()['results'][0]

        photo_path="https://image.tmdb.org/t/p/w185/"+response['poster_path']

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

            st.write(name_genre[1:])
            if len(description)>225:
                st.write(description[:225]+"...")
            else:
                st.write(description[:230])


