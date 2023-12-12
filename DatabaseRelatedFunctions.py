#steps to follow in order to connect to the database

# 1) Install the pypyodbc library (!pip install pypyodbc)
# 2) Install the required drivers.
# You can do so in the following link: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
# 3) Execute the connectToDatabase function of this file.
#    You can try to add a new user using the function addUser that you have connected succesfully to the database
#    You can check that the user has been added to the table by getting the table using get_table("Users") [The function returns a pandas dataframe containing the table]

#importing needed libraries
import pypyodbc as odbc
import pandas as pd
import Shared_Variables
from faker import Faker
import random
import string 

def connectToDatabase():
    
    global conn 
    conn = odbc.connect(Shared_Variables.connection_string)
    global cursor 
    cursor = conn.cursor()
    
def closeConnectionToDatabase():
    cursor.close()
    conn.close()
    
def addUser(newUser, newPassword):
     connectToDatabase()
     cursor.execute("SELECT COUNT(*) FROM Users")
     count = cursor.fetchone()[0]
     newUserId = count + 1
     cursor.execute("INSERT INTO Users (userID, userName, password) VALUES (?, ?, ?)", (newUserId, newUser, newPassword))
     conn.commit()
     closeConnectionToDatabase()
     
def login_user(userName, password):
    connectToDatabase()
    cursor.execute('SELECT userName, password FROM Users WHERE userName =? AND password = ?', (userName, password))
    data = cursor.fetchall()
    closeConnectionToDatabase()
    return data
# Returns false if the UserName doesn't exist, true otherwise
def checkUserId(userName):
    connectToDatabase()
    cursor.execute('SELECT count(distinct userName) FROM Users WHERE userName=?', (userName,))
    count = cursor.fetchone()[0]
    closeConnectionToDatabase()
    return count > 0

def get_table(tableName):
    connectToDatabase()
    cursor.execute(f"SELECT * FROM {tableName}")
    #data will be a list of tuples
    data = cursor.fetchall()
    # These part of the code transforms it in a dataframe
    column_names = [description[0] for description in cursor.description]
    # Create a DataFrame using fetched rows and column names
    data = pd.DataFrame(data, columns=column_names)
    closeConnectionToDatabase()
    return data

#Given a userName returns its userID
def getUserId(userName):
    #if userName equals none the functions returns infinity (This will be useful to code if statements related with in which we'll use this function)
    if userName == None:
        return float('inf')
    else:
        connectToDatabase()
        cursor.execute(f"SELECT userID FROM Users WHERE username = '{userName}'")
        result = cursor.fetchone()
        if result:
            userID = result[0]
            closeConnectionToDatabase()
            return int(userID)
        else:
            closeConnectionToDatabase()
            return None

def addRandomUser():
    fake = Faker()
    userName = fake.name()
    if (checkUserId(userName)==False):
        password = fake.password()
        addUser(userName, password)
    else:
        addRandomUser()
# Adds a new observation of a recomendation a userId has disliked
def addDislikedRecommendation(userId, movie):
    connectToDatabase()
    sqlQuery = "INSERT INTO dislikedRecommendations (userId, movie) VALUES (?,?)"
    cursor.execute(sqlQuery, (userId, movie))
    conn.commit()
    closeConnectionToDatabase()

#Given a userId returns a list of the recommendations he has disliked
def getDislikedRecommendations(userId):
    connectToDatabase()
    sqlQuery = "SELECT DISTINCT movie FROM dislikedRecommendations WHERE userId = ?"
    cursor.execute(sqlQuery, (userId, ))
    rows =  cursor.fetchall()
    dislikedRecommendationsByUser = [row[0] for row in rows]
    closeConnectionToDatabase()
    return dislikedRecommendationsByUser

addDislikedRecommendation(1, "Hola")
addDislikedRecommendation(1, "Adeu")
print(getDislikedRecommendations(2))
print(type(getDislikedRecommendations(2)))
