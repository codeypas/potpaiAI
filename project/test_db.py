import pymysql

connection = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="Root@123",
    database="potpai"
)

print("Connected successfully!")
