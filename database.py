#let's do it
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user='root',
    password='mySQL',
    database='mysql'

)
mycursor = mydb.cursor()
#1. need to convert nondigital value into digital value, such as comfortness
#2. hotel name can be url
#3. one table for car rental, one table for plane tickets

mycursor.execute("CREATE TABLE website (id INT AUTO_INCREMENT PRIMARY KEY, hotelname VARCHAR(255), price VARCHAR(255), convinience VARCHAR(255), comfortness VARCHAR(255))")
sql = "INSERT INTO website (hotelname,price,convinience,comfortness) VALUES ('Hilton', '200', 'yes', 'yes')"
sql = "INSERT INTO website (hotelname,price,convinience,comfortness) VALUES ('Sheraton', '250', 'No', 'No')"
sql = "INSERT INTO website (hotelname,price,convinience,comfortness) VALUES ('Hampton', '300', 'No', 'yes')"
sql = "INSERT INTO website (hotelname,price,convinience,comfortness) VALUES ('Hampton', '500', 'yes', 'yes')"

mycursor.execute(sql)
mydb.commit()
mycursor.execute("SELECT * FROM website ORDER BY hotelname , comfortness ")

for x in mycursor.fetchall():
    print(x)
