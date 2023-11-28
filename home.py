import pickle
import pandas as pd
import streamlit as st
from streamlit import session_state as session
import requests
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page



user_ids=([str(elem) for elem in list(range(1,611))])

st.title("""
Recommendation System for Agile
 """)

st.text("")
st.text("")
par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">This is an Content Based Recommender System for each user and customize quantity of recommendations 😎.</p>'
st.markdown(par2, unsafe_allow_html=True)
st.text("")
st.text("")

par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">If you are already in our database, please write your used id and click on the button.</p>'
st.markdown(par2, unsafe_allow_html=True)
session.user_id=st.text_input(label="Write your user id")


if st.button('Go'):
    print("GO")
    if str(session.user_id) in user_ids:
        switch_page('registered_user')

st.text("")


par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">If you are a new user, click into the next button</p>'
st.markdown(par2, unsafe_allow_html=True)
st.text("")

if st.button("I'm a new a User"):
    switch_page('new_user')


 
st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )


