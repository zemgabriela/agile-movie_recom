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

def connectToDatabase():
    connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:agiledsproject.database.windows.net,1433;Database=MovieRatings;Uid=ProjectDataBase;Pwd=Agile2023;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    global conn 
    conn = odbc.connect(connection_string)
    global cursor 
    cursor = conn.cursor()

# Improvements still to be done, e.g, checking the username doesn't already exists
def addUser(newUser, newPassword):
     cursor.execute("INSERT INTO Users (userName, password) VALUES (?, ?)", (newUser, newPassword))
     conn.commit()
     
def login_user(userName, password):
    cursor.execute('SELECT * FROM Users WHERE userName =? AND password = ?', (userName, password))
    data = cursor.fetchall()
    return data

def checkUserId(userName):
    cursor.execute('SELECT count(distinct userName) FROM Users WHERE userName=?', (userName,))
    count = cursor.fetchone()[0]
    return count > 0
def get_table(tableName):
   cursor.execute(f"SELECT * FROM {tableName}")
    #data will be a list of tuples
   data = cursor.fetchall()
   # These part of the code transforms it in a dataframe
   column_names = [description[0] for description in cursor.description]
   # Create a DataFrame using fetched rows and column names
   data = pd.DataFrame(data, columns=column_names)
   return data
    
def closeConnectionToDatabase():
    cursor.close()
    conn.close()
    
