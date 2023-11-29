# Agile DS - Movie Recommender Project

### Connect to SQL Database

To be able to connect to the SQL Database of the project, you must follow the next steps:

1. **Download an ODBC Driver for SQL Server**: Download the last version (v18) in the next link - the download will be by executing code in the terminal:
   https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16

2. **Check the driver installation**: Open a terminal and run **'odbcinst -j'** and **odbcinst -q -d** (in Mac, look for the equivalence in your system). The first command displays information about the ODBC driver manager, including the locations of the *odbc.ini* and *odbcinst.ini* files. The second command should display something like: [ODBC Driver 18 for SQL Server]

4. **Install pypyodbc library**: Install the library **pypyodbc**, which will be used to connect to the SQL Database, using the following command in terminal:
   ```pip install pypyodbc ```
   
5. **Check installation of the library**: Check that you can correctly use the library *pypyodbc*. For that, execute this code in terminal:
   ```python -c "import pypyodbc"```

   If you encounter an error like this one [OdbcNoLibrary: 'ODBC Library is not found. Is LD_LIBRARY_PATH set?'] when trying to import the library, follow the next steps:
     - Finding the Path of ODBC Driver Manager Library
         - First, locate the ODBC driver manager library (like libodbc.dylib for UnixODBC). You can use the find command in the terminal to locate it. For example: ```find / -name libodbc.dylib 2>/dev/null```
     - Setting DYLD_LIBRARY_PATH
         - Once you find the path to libodbc.dylib, you can set DYLD_LIBRARY_PATH to include this path
         - Open the shell configuration file. To do so you must use some of these commands in the terminal (for me it worked the one with .zprofile, but you can change them all): ```nano ~/.zprofile```, ```nano ~/.zshrc```, ```nano ~/.bash_profile```
         - Edit your shell configuration file and add the path with this command: ```export DYLD_LIBRARY_PATH=<path_to_odbc_library>:$DYLD_LIBRARY_PATH```
     - Apply the Changes
         - After saving the file, run source ~/.zprofile (or the relevant file for your shell) to apply the changes.

   With these steps you should be able to import the library, and so connect to the SQL Database.
____

### Git commit and push

#### To update your branch with the contents of the main branch:
1. Swith to your branch: ```git checkout your_branch```
2. Fetch the latest changes from remote: ```git fetch origin```
3. Merge main into your branch: ```git merge origin/main```
4. Git commit and push for updating the repository

#### To add a file of your branch in the main branch:
1. Swith to the main branch: ```git checkout main```
2. Bring the specific file from your branch: ```git checkout your_branch -- path/to/yourfile.ext```
3. Git commit and push for updating the repository

