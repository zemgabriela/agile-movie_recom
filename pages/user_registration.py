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
    st.subheader("Create New Account")
#st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )


new_user = st.text_input("Username")
new_password = st.text_input("Password", type= 'password')

if st.button("Signup"):

    if(DatabaseRelatedFunctions.checkUserId(new_user)==False):
        st.success("You have successfully created an account")
        DatabaseRelatedFunctions.addUser(new_user, new_password)
        Shared_Variables.userName = new_user
        Shared_Variables.loggedIn = True
        if (DatabaseRelatedFunctions.getUserId(new_user)<=Shared_Variables.max_id_user_model):
            st.session_state.is_clicked = False
            switch_page('registered_user')
        else:
            switch_page('new_user')
    else:
        st.warning("This user ID already exists. Please try a new one.")
