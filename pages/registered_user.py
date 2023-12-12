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

# Load movies.csv
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


def load_users():
    df_users=DatabaseRelatedFunctions.get_table('Users')
    #st.write(df_users.columns)
    n_users=df_users['userid'].nunique()
    return(n_users)
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
            movies_df['year'] = pd.to_numeric(movies_df['year'], errors='coerce').astype('Int64')
            movies_df = movies_df[(movies_df['year'] >= start_year) & (movies_df['year'] <= end_year)]
        else:
            # Convert 'year' column to numeric before filtering
            movies_df['year'] = pd.to_numeric(movies_df['year'], errors='coerce').astype('Int64')
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
    recommended_movies = movies_df.iloc[top_indices][['title','genres','year']].to_dict(orient='records')
    predicted_ratings = pred[top_indices]

    return recommended_movies





def recommended_movies_by_user_last(model, user_id, n_movies, movies_df, w_vector=np.ones(9742), genres=None, start_year=None, end_year=None,): 
    #here w_vector is the weight vector of that user. If nothing is just the vector of ones.
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


    w_vector=w_vector[list(movies_df.index)]
    pred = model.predict(user_ids=np.array([user_id]*len(filtered_movie_ids)), item_ids=filtered_movie_ids)
    pred=pred*w_vector #according to our idea, in this way we remove movies with the bad feedback.

    # Sort predicted ratings in descending order
    sorted_indices = np.argsort(pred)[::-1]
    # Select the top n_movies
    top_indices = sorted_indices[:n_movies]
    recommended_movies = movies_df.iloc[top_indices][['title','genres','year']].to_dict(orient='records')
    predicted_ratings = pred[top_indices]

    return recommended_movies

unique_movies = movies_df['item_id'].nunique()
unique_users= load_users()


#let's create the function that change the weights according to the star feedback

def update_weights(user_id,list_titles,feedbacks,W_matrix,movies_df):
    i=0
    #titles contains the list of titles that has a feedback, while feedbacks is a vector that is of the form [4/5,5/5,1/5,...]

    for title in list_titles:
        index=movies_df.index[movies_df['title']==title] 
        W_matrix[index,user_id]=feedbacks[i]
        i+=1
    return W_matrix

# Unique Genres df

# !!! Gotta Change this part so it can dynamically adapt

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
def fetch_movie_info(movie_title, year_release):
    ia = IMDb()

    # Search for the movie using both title and year
    movies = ia.search_movie(movie_title)
    
    if movies:
        # Filter movies based on the provided year
        matching_movies = [movie for movie in movies if str(year_release) in str(movie.get('year', ''))]

        if matching_movies:
            selected_movie = ia.get_movie(matching_movies[0].movieID)
            ia.update(selected_movie, info=['main', 'vote details'])
            return selected_movie
        else:
            # If no matching movie found for the specified year, return None
            return None
    else:
        return None

# Display Movie Information
def display_movie_info(selected_movie, ownDB_movie):
    # Title
    if selected_movie is None: # If movie recommendation is not found in IMDB, we will retrieve info from our DB
        st.write(f"**Title:** {ownDB_movie['title']}")
    else:
        st.write(f"**Title:** {selected_movie['title']}")

    # Year
    if selected_movie is None:
        st.write(f"**Year:** {ownDB_movie['year']}")
    else:
        st.write(f"**Year:** {selected_movie['year']}")

    # Genres (now retrieving genres from our DB to match user optional genre filtering)
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




col1, col2= st.columns([3, 1])
with col1:
    st.title("""
    Welcome back, {0}!
    """.format(Shared_Variables.userName))

    st.text("")
with col2:
    st.text("")
    st.text("")
    if st.button('Log Off'):
        Shared_Variables.loggedIn = False
        Shared_Variables.userName = None
        switch_page('Home')

user_id=DatabaseRelatedFunctions.getUserId(Shared_Variables.userName)

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
l_titles,l_feedbacks=[],[]
if is_clicked or Shared_Variables.W_matrix!=[]:



    if Shared_Variables.W_matrix==[]:

        Shared_Variables.W_matrix=np.ones((unique_movies,unique_users)) #weight matrix
        if not selected_genres:
            recommendations = recommended_movies_by_user(model, user_id, movie_count, movies_df, start_year = min_year, end_year = max_year)
        else:
            recommendations = recommended_movies_by_user(model, user_id, movie_count, movies_df, selected_genres, min_year, max_year)
        
    else:

        recommendations = recommended_movies_by_user_last(model, user_id, movie_count, movies_df, Shared_Variables.W_matrix[:,user_id], selected_genres,start_year = min_year, end_year = max_year)
    movie_info_list = [fetch_movie_info(movie['title'], movie['year']) for movie in recommendations]   
    # Fetch movie information
    


    # Check if any movies were found, print warnings if necessary
    if movie_info_list:

        for selected_movie, ownDB_movie in zip(movie_info_list, recommendations): #Now iterating over IMDB info and our own DB for each movie recommendation!
            st.markdown("---")
            col1, col2= st.columns(2)
            with col1:
                display_poster(selected_movie)     
            with col2:
                display_movie_info(selected_movie, ownDB_movie)

        with st.form("Feedback"):
            for selected_movie, ownDB_movie in zip(movie_info_list, recommendations):
                st.write(f"Do you like {ownDB_movie['title']} as a movie recommendation?")
    
                # Use the movie title as a key to get the feedback status
                feedback_key = f"feedback_{ownDB_movie['title']}"
    
                # Radio buttons for thumbs up and thumbs down
                feedback_status = st.radio("", ["👍 Yes, I like it!", "👎 No, I don't like it!"], key=feedback_key)

                if feedback_status == "👍 Yes, I like it!":
                    l_feedbacks.append(1)
                else:
                    l_feedbacks.append(-1)
                l_titles.append(ownDB_movie['title'])


            st.write("🌟 We appreciate your feedback! "
                "Based on your preferences, we will provide "
                "you with even better movie recommendations in the next set. Enjoy your movies!")
            
            # Submit button
            if st.form_submit_button("Submit"):

                Shared_Variables.W_matrix=update_weights(user_id,l_titles,l_feedbacks,Shared_Variables.W_matrix,movies_df)


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


