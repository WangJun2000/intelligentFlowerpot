import sqlite3
import os

dir=os.path.dirname(__file__)
print(dir)
conn = sqlite3.connect(dir+'\\myApp.db')
print ("Opened database successfully")
conn.close()