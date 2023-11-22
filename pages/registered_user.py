import pandas as pd
import streamlit as st
from streamlit import session_state as session
import requests
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page
from joblib import dump, load
from imdb import IMDb

# Load movies.csv
def load_movie_data():
    movies_df = pd.read_csv('ml-latest-small/movies.csv', sep=',', names=['item_id', 'title', 'genres'], engine='python',skiprows=1)

    movies_df['year'] = movies_df['title'].str.extract(r'\((\d{4}(?:–\d{4})?)\)')  
    movies_df['year'] = movies_df['year'].where(movies_df['year'].str.len() == 4, None)  
    movies_df['title'] = movies_df['title'].str.replace(r'\(\d{4}(?:–\d{4})?\)', '', regex=True).str.strip()

    movies_df['title']=movies_df['title'].str.replace(', The', '')
    movies_df['genres']=movies_df['genres'].str.replace('|',', ')

    return movies_df

movies_df = load_movie_data()


@st.cache_data()
def load_model():
    model = load('model.pkl') 

    return model


def recommended_movies_by_user(model, user_id, n_movies, movies_df, genres=None, start_year=None, end_year=None):
    # Apply genre/year filters before making predictions
    if genres is not None:
        filter_condition = lambda x: any(genre.lower() in x.lower() for genre in genres)
        movies_df = movies_df[movies_df['genres'].apply(filter_condition)]
    if start_year is not None:
        if end_year is not None:
            # Convert 'year' column to numeric before filtering
            movies_df['year'] = pd.to_numeric(movies_df['year'], errors='coerce')
            movies_df = movies_df[(movies_df['year'] >= start_year) & (movies_df['year'] <= end_year)]
        else:
            # Convert 'year' column to numeric before filtering
            movies_df['year'] = pd.to_numeric(movies_df['year'], errors='coerce')
            movies_df = movies_df[movies_df['year'] >= start_year]

    # Now predict scores for the (optionally) filtered items for the user
    filtered_movie_ids = movies_df['item_id'].values
    if len(filtered_movie_ids) == 0:
        return []  # No movies after filtering, return an empty list
    pred = model.predict(user_ids=np.array([user_id]*len(filtered_movie_ids)), item_ids=filtered_movie_ids)
    
    # Sort predicted ratings in descending order
    sorted_indices = np.argsort(pred)[::-1]

    # Select the top n_movies
    top_indices = sorted_indices[:n_movies]
    recommended_movies = movies_df.iloc[top_indices]['title'].tolist()
    predicted_ratings = pred[top_indices]

    return recommended_movies

# Unique Genres df
unique_genres=['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX', 'Musical', 
                'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'] 

# Min and Max Year df
movies_df['year'] = pd.to_numeric(movies_df['year'], errors='coerce')
min_year_df=int(movies_df['year'].min())
max_year_df=int(movies_df['year'].max())


model = load_model()
user_ids=([str(elem) for elem in list(range(1,611))])

#st.set_page_config(initial_sidebar_state="collapsed") 
st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )



#############################
###### STREAMLIT APP ########
#############################

# Fetch Movie Information
def fetch_movie_info(movie_title):
    ia = IMDb()
    movies = ia.search_movie(movie_title)
    if movies:
        selected_movie = ia.get_movie(movies[0].movieID)
        ia.update(selected_movie, info=['main', 'vote details'])
        return selected_movie
    else:
        return None

# Display Movie Information
def display_movie_info(selected_movie):
    # Title
    st.write(f"**Title:** {selected_movie['title']}")
    # Year
    st.write(f"**Year:** {selected_movie['year']}")
    # Genres
    genres = selected_movie.get('genres', [])
    st.write(f"**Genres:** {', '.join(genres)}")

    # Directors
    directors = selected_movie.get('director', [])
    st.write(f"**Director(s):** {', '.join([director['name'] for director in directors])}")
    # Cast
    actors = selected_movie.get('cast', [])
    st.write(f"**Cast:** {', '.join([actor['name'] for actor in actors[:3]])}")

    # IMDB Rating
    st.write(f"**IMDB Rating:** {selected_movie.get('rating', 'N/A')}")
    # Overview
    ## Check if 'plot' is a list and convert it to a string
    overview = selected_movie.get('plot', ['N/A'])
    if isinstance(overview, list):
        overview = ', '.join(overview)

    ## Remove brackets from the overview
    overview = overview.strip('[]')

    ## Limit overview length
    if len(overview)>225:
                    st.write(f"**Overview:** {overview[:225]}...")
    else:
                    st.write(f"**Overview:** {overview}")

# Display Poster Image
def display_poster(selected_movie, width = 200):
    if 'cover url' in selected_movie.keys():
        poster_url = selected_movie.get('full-size cover url', None)
        if poster_url:
            st.image(poster_url, width = width)
        else:
            st.warning("No poster found for the selected movie")

# Main function
def main():


    col1, col2= st.columns([3, 1])
    with col1:
        st.title("""
        Welcome user {0}
        """.format(session.user_id))

        st.text("")
    with col2:
        st.text("")
        st.text("")
        if st.button('Home'):
            switch_page('Home')
    user_id=int(session.user_id)

    par1 = '<p style="font-family:sans-serif; color:Grey; font-size: 28px;">Please choose your preferences</p>'
    st.markdown(par1, unsafe_allow_html=True)


    st.text("")


    st.text("")
    par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">Choose how many movie recommendations do you want.</p>'
    st.markdown(par2, unsafe_allow_html=True)
    movie_count = st.slider(label="",min_value=1, max_value=5)

    st.text("")
    st.text("")

    # User input for filtering by year
    par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">Filter by Year</p>'
    st.markdown(par2, unsafe_allow_html=True)
    min_year, max_year = st.slider("", min_year_df, max_year_df, (min_year_df, max_year_df))

    # User input for genre selection
    st.text("")
    par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">Select Genres</p>'
    st.markdown(par2, unsafe_allow_html=True)
    selected_genres = st.multiselect("", unique_genres)

    # Button recommendation
    buffer1, col1, buffer2 = st.columns([1.45, 1, 1])
    is_clicked = col1.button(label="Recommend")

    if is_clicked:
        #user_id = int(st.text_input("Enter User ID:"))
        if not selected_genres:
            recommendations = recommended_movies_by_user(model, user_id, movie_count, movies_df, start_year = min_year, end_year = max_year)
        else:
            recommendations = recommended_movies_by_user(model, user_id, movie_count, movies_df, selected_genres, min_year, max_year)

        # Fetch movie information
        movie_info_list = [fetch_movie_info(title) for title in recommendations if fetch_movie_info(title) is not None]

        # Check if any movies were found
        if movie_info_list:
            for selected_movie in movie_info_list:
                st.markdown("---")
                col1, col2= st.columns(2)
                with col1:
                    display_poster(selected_movie)
                with col2:
                    display_movie_info(selected_movie)

        else:
            st.warning("No movies found with the entered titles")

# Run the app
if __name__ == "__main__":
    main()



