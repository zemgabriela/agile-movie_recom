#importing needed libraries
import streamlit as st
import pypyodbc as odbc
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from DatabaseRelatedFunctions import *

connectToDatabase()

st.subheader("Create New Account")
new_user = st.text_input("Username")
new_password = st.text_input("Password", type= 'password')

if st.button("Signup"):

    if(checkUserId(new_user)==False):
        st.success("You have successfully created an account")
        addUser(new_user, new_password)
        switch_page('home')
    else:
        st.warning("This user ID already exists. Please try a new one.")
