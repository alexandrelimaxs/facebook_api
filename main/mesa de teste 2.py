import mysql.connector

mydb = mysql.connector.connect(
    host = '127.0.0.1',
    user = 'root',
    password = 'erdnaxela',
    database = 'facebook'
)

mycursor = mydb.cursor()

mycursor.execute('SELECT * FROM dados')

myresult = mycursor.fetchall()

for x in myresult:
  print(x)