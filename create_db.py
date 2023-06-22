import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password"
)

# cursor is automated that does the commands
my_cursor = mydb.cursor()

# my_cursor.execute("CREATE DATABASE our_users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)

#fix:
# update pip or install `pip install mysql-connector-python==8.0.17`
