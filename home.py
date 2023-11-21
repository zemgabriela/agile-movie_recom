import pickle
import pandas as pd
import streamlit as st
from streamlit import session_state as session
import requests
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page


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


st.title("""
Recommendation System for Agile
This is an Content Based Recommender System for each user and customize quantity of recommendations 😎.
 """)

st.text("")
st.text("")

st.text("""If you are already in our database, please write your used id and click on the button.""")

session.user_id=st.text_input(label="Write your user id")


if st.button('Go'):
    if str(session.user_id) in user_ids:
        switch_page('registered_user')

st.text("")
st.text("")

st.text("""If you are a new user, click into the next button""")

st.text("")

if st.button("I'm a new a User"):
    switch_page('new_user')


 
st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )


