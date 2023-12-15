import pickle
import pandas as pd
import streamlit as st
from streamlit import session_state as session
import requests
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page
import DatabaseRelatedFunctions
import Shared_Variables

st.set_page_config(
    page_title="Movie Reccomender",
    page_icon=":movie_camera:",
    initial_sidebar_state='collapsed',
)

image_path = ["MOVIE.png"]

# Define a custom style with @font-face
custom_style = """
    <style>
        @import url('https://fonts.googleapis.com/css?family=Carme&display=swap');
        .custom-font {
            font-family: 'Carme', sans-serif;
        }
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

image_path = ["MOVIE.png"]
if "is_clicked" not in st.session_state:
    st.session_state.is_clicked = False
    
if (Shared_Variables.loggedIn == True) and (DatabaseRelatedFunctions.getUserId(Shared_Variables.userName) <= Shared_Variables.max_id_user_model):
    st.session_state.is_clicked = False
    switch_page('registered_user')
else:
    st.image(image_path, use_column_width='always')

    st.text("")
    st.text("")
    st.markdown('<p class="custom-font" style="font-size: 20px;text-align:center;">🎬Welcome to our film recommender! Discover your next favorite movie!🎬</p>', unsafe_allow_html=True)
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.markdown('<p class="custom-font" style="font-size: 17px;text-align:center;">Sign in and continue discovering. If you new here, register and create an account.</p>', unsafe_allow_html=True)
    st.text("")   
    col1, col2, col3 = st.columns([6, 3, 9])
    with col2:
        if st.button("Log in :lock:"):
            switch_page('user_login')
    with col3:
        if st.button("Register here"):
            switch_page('user_registration')
    
    st.text("") 
    st.text("")
    st.text("")  
    st.markdown('<p class="custom-font" style="font-size: 17px;text-align:center;">Coming here only for a recommendation? Click the next button.</p>', unsafe_allow_html=True)
    st.text("") 
    
    col4, col5 = st.columns([2, 5])
    with col5:
        if st.button("I just want to get a recommendation!"):
            switch_page('new_user')

    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.text("""// This Content-Based Recommender System was created for Agile Data Project(2023) //""")
