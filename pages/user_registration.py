#importing needed libraries
import streamlit as st
import pypyodbc as odbc
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

import DatabaseRelatedFunctions
import Shared_Variables


if st.button('Home'):
    switch_page('Home')

st.subheader("Create New Account")
new_user = st.text_input("Username")
new_password = st.text_input("Password", type= 'password')

#st.set_page_config(initial_sidebar_state="collapsed") 
st.markdown( """ <style> [data-testid="stSidebarContent"] { display: none } </style> """, unsafe_allow_html=True, )

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
