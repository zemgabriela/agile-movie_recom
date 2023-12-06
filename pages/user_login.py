#importing needed libraries
import streamlit as st
import pypyodbc as odbc
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from DatabaseRelatedFunctions import *

connectToDatabase()

st.subheader("Login Section")
username = st.text_input("User Name")
password = st.text_input("Password", type='password')
if st.checkbox("Login"):
# The next line should check the password is correct
    result = login_user(username, password)
    if result:
        st.success("Logged In as {}".format(username))
        switch_page('home')
    else:
        st.warning("Incorrect Username/Password")
