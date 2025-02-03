import streamlit as st
import sqlite3
from datetime import datetime

def createUploadedFileTable():
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS fileTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                filetype TEXT,
                filesize INTEGER,
                uploadDate TIMESTAMP,
                UNIQUE(filename, filetype, filesize)
            );
        ''')
        conn.commit()

def addFileDetails(filename, filetype, filesize, uploadDate):
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO fileTable (filename, filetype, filesize, uploadDate)
                VALUES (?, ?, ?, ?)
            ''', (filename, filetype, filesize, uploadDate))
            conn.commit()
            st.success("File details added successfully!")
        except sqlite3.IntegrityError:
            st.warning("This file record already exists in the database.")

@st.cache_data
def viewAllData():
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM fileTable")
        data = c.fetchall()
    return data

# In your main app logic
def main():
    createUploadedFileTable()
    # Rest of your app code...

if __name__ == "__main__":
    main()


# import sqlite3
# from datetime import datetime

# #-------------- Database Functions:
# ## Function to connect to database:
# CONN = sqlite3.connect('data.db')
# C = CONN.cursor()

# ## Table to store details:
# def createUploadedFileTable():
#     # C.execute("CREATE TABLE IF NOT EXISTS fileTable(filename TEXT, filetype TEXT, filesize TEXT, uploadDate TIMESTAMP)")
#     # Create the table with a UNIQUE constraint (if not exists)
#     C.execute('''
#         CREATE TABLE IF NOT EXISTS fileTable (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             filename TEXT,
#             filetype TEXT,
#             filesize INTEGER,
#             uploadDate TIMESTAMP,
#             UNIQUE(filename, filetype, filesize)
#         );
#     ''')
#     # CONN.commit()


# # Function to Add details to table:
# # st.cache_data is used to make our app run faster when caching databases
# def addFileDetails(filename, filetype, filesize, uploadDate):
#     C.execute("""
#               INSERT INTO fileTable (filename, filetype, filesize, uploadDate)
#               VALUES (?, ?, ?, ?)
#               """, (filename, filetype, filesize, uploadDate))
#     CONN.commit()
    
# ## Function to view records from database:
# def viewAllData():
#     C.execute("SELECT DISTINCT * FROM fileTable;")
#     data = C.fetchall()
#     return data

