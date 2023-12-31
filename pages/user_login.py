#importing needed libraries
import streamlit as st
import pypyodbc as odbc
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

import DatabaseRelatedFunctions
import Shared_Variables

st.set_page_config(
    page_title="Movie Reccomender",
    page_icon=":movie_camera:",
    initial_sidebar_state='collapsed',
)
col1, col2 = st.columns([12, 2])
with col2:
    if st.button('Home'):
        switch_page('Home')
with col1:
    st.subheader("Login Section :lock:")
username = st.text_input("User Name")
password = st.text_input("Password", type='password')
#st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )

if st.checkbox("Login"):
# The next line should check the password is correct
    result = DatabaseRelatedFunctions.login_user(username, password)
    if result:
        st.success("Logged In as {}".format(username))
        Shared_Variables.userName = username
        Shared_Variables.loggedIn = True
        if (DatabaseRelatedFunctions.getUserId(username)<=Shared_Variables.max_id_user_model):
            st.session_state.is_clicked = False
            switch_page('registered_user')
        else:
            switch_page('new_user')
    else:
        st.warning("Incorrect Username/Password")
