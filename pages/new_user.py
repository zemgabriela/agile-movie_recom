import pandas as pd
import streamlit as st
from streamlit import session_state as session
import requests
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page
from joblib import dump, load
from imdb import IMDb
import DatabaseRelatedFunctions
import Shared_Variables

# Load movies data from the sql database


st.set_page_config(
    page_title="Movie Reccomender",
    page_icon=":movie_camera:",
    initial_sidebar_state='collapsed',
)

def load_movie_data():

    movies_df = DatabaseRelatedFunctions.get_table('Movies')
    movies_df.columns = ['item_id', 'title', 'genres']

    movies_df['year'] = movies_df['title'].str.extract(r'\((\d{4}(?:–\d{4})?)\)')  
    movies_df['year'] = movies_df['year'].where(movies_df['year'].str.len() == 4, None)  
    movies_df['title'] = movies_df['title'].str.replace(r'\(\d{4}(?:–\d{4})?\)', '', regex=True).str.strip()

    movies_df['title']=movies_df['title'].str.replace(', The', '')
    movies_df['genres']=movies_df['genres'].str.replace('|',', ')

    return movies_df

movies_df = load_movie_data()


@st.cache_data()
def load_model():
    model_seq = load('model_seq.pkl') 

    return model_seq


def recommend_next_movies(model_seq, list_of_movies, n_movies, movies_df, genres=None, start_year=None, end_year=None):
    
    indices_movies = movies_df[movies_df['title'].isin(list_of_movies)]['item_id']
    
    # Check if indices_movies is not empty
    if not indices_movies.empty:
        # Apply genre/year filters before making predictions
        if genres is not None:
            filter_condition = lambda x: any(genre.lower() in x.lower() for genre in genres)
            movies_df = movies_df[movies_df['genres'].apply(filter_condition)]
        if start_year is not None:
            if end_year is not None:
                movies_df = movies_df[(movies_df['year'] >= start_year) & (movies_df['year'] <= end_year)]
            else:
                movies_df = movies_df[movies_df['year'] >= start_year]

        # END OF FILTERING PART

        # Check if item_ids is not empty
        item_ids = movies_df['item_id'].values.reshape(-1, 1)
        if not item_ids.size == 0:
            # Perform the predictions
            pred = model_seq.predict(sequences=np.array(indices_movies), item_ids=item_ids)

            sorted_indices = np.argsort(pred)[::-1]
            top_indices = sorted_indices[:n_movies]

            recommended_movies = movies_df.iloc[top_indices][['title', 'genres', 'year']].to_dict(orient='records')

            return recommended_movies
        else:
            return []  # Return an empty list if item_ids is empty - no movies found with the selected year range and genres
    else:
        return []  # Return an empty list if indices_movies is empty - no favourite movies were selected


# Unique Genres df
unique_genres=['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX', 'Musical', 
                'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'] 

# Min and Max Year df / Converting year to int
movies_df['year'] = pd.to_numeric(movies_df['year'], errors='coerce').astype('Int64')
min_year_df=int(movies_df['year'].min())
max_year_df=int(movies_df['year'].max())

# Movies list for input
movies=list(movies_df["title"].unique())

# Load pkl model
model_seq=load_model()


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
def display_movie_info(selected_movie, ownDB_movie):
    # Title (now retrieving from our DB to decrease runtime)
    #if selected_movie is None: # If movie recommendation is not found in IMDB, we will retrieve info from our DB
    st.write(f"**Title:** {ownDB_movie['title']}")
    #else:
        #st.write(f"**Title:** {selected_movie['title']}")

    # Year (now retrieving from our DB to decrease runtime)
    st.write(f"**Year:** {ownDB_movie['year']}")

    # Genres (now retrieving genres from our DB to match user optional genre filtering and decrease runtime)
    st.write(f"**Genres:** {ownDB_movie['genres']}")

    # Directors
    if selected_movie is None:
         st.write(f"**Director(s):** No information available")
    else:
        directors = selected_movie.get('director', [])
        st.write(f"**Director(s):** {', '.join([director['name'] for director in directors])}")

    # Cast
    if selected_movie is None:
        st.write(f"**Cast:** No information available")
    else:
        actors = selected_movie.get('cast', [])
        st.write(f"**Cast:** {', '.join([actor['name'] for actor in actors[:3]])}")

    # IMDB Rating
    if selected_movie is None:
        st.write(f"**IMDB Rating** No information available")
    else:
        st.write(f"**IMDB Rating:** {selected_movie.get('rating', 'N/A')}")
   
    # Overview
    if selected_movie is not None:
        ## Check if 'plot' is a list and convert it to a string
        overview = selected_movie.get('plot', ['N/A'])
        if isinstance(overview, list):
            overview = ', '.join(overview)

    ## Remove brackets from the overview
    if selected_movie is not None:
        overview = overview.strip('[]')

    ## Limit overview length
    if selected_movie is None:
         st.write(f"**Overview:** No information available")
    else:
        if len(overview)>225:
                    st.write(f"**Overview:** {overview[:225]}...")
        else:
                    st.write(f"**Overview:** {overview}")

# Display Poster Image
def display_poster(selected_movie, width = 200):
    if selected_movie is not None:
        if 'cover url' in selected_movie.keys():
            poster_url = selected_movie.get('full-size cover url', None)
            if poster_url:
                st.image(poster_url, width = width)
            else:
                st.write("No poster found for the selected movie")


# Main function
def main():               

    if(Shared_Variables.userName != None):
         st.title("""
            Welcome back, {0}!
                """.format(Shared_Variables.userName))
         st.text("")
        

    col1, col2= st.columns([12, 2])
    with col1:
        st.title("""
        Discover Your Next Favorite Movie! :popcorn:""")

        st.text("")
    with col2:
        st.text("")
        st.text("")
        if Shared_Variables.loggedIn == True:
            if st.button('Log out'):
                Shared_Variables.loggedIn = False
                Shared_Variables.userName = None
                switch_page('Home')
        else:    
            if st.button('Home'):
                switch_page('Home')

    #st.set_page_config(initial_sidebar_state="collapsed") 
    #st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )
        

    #st.set_page_config(initial_sidebar_state="collapsed") 
    #st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )



    movies.sort()
    par2= '<p style="font-family:sans-serif;font-size: 18px;">Select your favorites movies.</p>'
    st.markdown(par2, unsafe_allow_html=True)

    list_of_movies = st.multiselect(label="", options=movies)

    #session.user_id=st.text_input(label="Write your user id")

    st.text("")


    st.text("")
    par2= '<p style="font-family:sans-serif; font-size: 18px;">Choose how many movie recommendations do you want.</p>'
    st.markdown(par2, unsafe_allow_html=True)
    movie_count  = st.slider(label="",min_value=1, max_value=5)

    st.text("")
    st.text("")

    # User input for filtering by year
    par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">Filter by Year</p>'
    st.markdown(par2, unsafe_allow_html=True)
    min_year, max_year = st.slider("", min_year_df, max_year_df, (min_year_df, max_year_df))

    # User input for genre selection
    st.text("")
    par2= '<p style="font-family:sans-serif;  font-size: 18px;">Select Genres</p>'
    st.markdown(par2, unsafe_allow_html=True)
    selected_genres = st.multiselect("", unique_genres)

    # Button recommendation
    buffer1, col1, buffer2 = st.columns([1.45, 1, 1])
    is_clicked = col1.button(label="Recommend")

    # Call recommender model after clicking "Recommend"
    if is_clicked:
        if not list_of_movies:  # Check if the user hasn't selected any favorite movies
            st.warning("💡 Hold on! It seems you forgot to pick your favorite movies. "
            "Select at least one favorite movie to get personalized recommendations. 🎬")
        else:
            if not selected_genres:
                recommendations = recommend_next_movies(model_seq, list_of_movies, movie_count, movies_df, start_year = min_year, end_year = max_year)
            else:
                recommendations = recommend_next_movies(model_seq, list_of_movies, movie_count, movies_df, selected_genres, min_year, max_year)

            # Fetch movie information
            movie_info_list = [fetch_movie_info(movie['title']) for movie in recommendations]

            # Check if any movies were found, print warnings if necessary
            if movie_info_list:
                for selected_movie, ownDB_movie in zip(movie_info_list, recommendations): #Now iterating over IMDB info and our own DB for each movie recommendation!
                    st.markdown("---")
                    col1, col2= st.columns(2)
                    with col1:
                        display_poster(selected_movie)
                    with col2:
                        display_movie_info(selected_movie, ownDB_movie)

            # Show a warning when no recommendations match the applied filters
            else:
                st.warning("💬 Oops! It looks like we couldn't find any movies with the entered filters. "
                           "No worries, though! You can enhance your search experience by tweaking your filters. "
                           "Consider trying a different year, exploring a new genre, or expanding your search criteria. "
                        "Happy searching! 😊")
        
            # Show a warning when the number of recommendations is less than the requested count
            if len(recommendations) < movie_count and len(recommendations) != 0:
                st.warning("💬 Uh-oh! We couldn't find enough movies to meet your request. "
                           "Consider adjusting your filters for more options. "
                           "Happy searching! 😊")



# Run the app
if __name__ == "__main__":
    main()
