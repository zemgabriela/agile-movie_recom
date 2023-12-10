#importing needed libraries
import streamlit as st
import pypyodbc as odbc
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

import DatabaseRelatedFunctions
import Shared_Variables

st.subheader("Create New Account")
new_user = st.text_input("Username")
new_password = st.text_input("Password", type= 'password')

if st.button("Signup"):

    if(checkUserId(new_user)==False):
        st.success("You have successfully created an account")
        addUser(new_user, new_password)
        Shared_Variables.userName = new_user
        Shared_Variables.loggedIn = True
        if (getUserId(new_user)<=Shared_Variables.max_id_user_model):
            switch_page('registered_user')
        else:
            switch_page('new_user')
    else:
        st.warning("This user ID already exists. Please try a new one.")
