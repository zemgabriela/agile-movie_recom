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


if (Shared_Variables.loggedIn == True) and (DatabaseRelatedFunctions.getUserId(userName)<= Shared_Variables.max_id_user_model):
    switch_page('registered_user')
else:        
    st.title("""
    Recommendation System for Agile
     """)

    st.text("")
    st.text("")
    par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">Welcome to our film recomender!😎.</p>'
    st.markdown(par2, unsafe_allow_html=True)
    st.text("")
    st.text("")

    par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">If you are already in our database, please sign in. If you aren\'t, you can create an account.</p>'
    st.markdown(par2, unsafe_allow_html=True)
    if st.button("You don't have an account? Register here!"):
        switch_page('user_registration')

    if st.button("You already have an account? Log in here!"):
        switch_page('user_login')
        
    par2= '<p style="font-family:sans-serif; color:Grey; font-size: 18px;">If you just want a recommendation, click the next button</p>'
    st.markdown(par2, unsafe_allow_html=True)
    st.text("")

    if st.button("I just want to get a recomendation!"):
        switch_page('new_user')
       
    st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )




