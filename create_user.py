from database import get_connection
from werkzeug.security import generate_password_hash

username = input("Enter username: ")
password = input("Enter password: ")

password_hash = generate_password_hash(password)

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    INSERT INTO users (username, password)
    VALUES (?, ?)
""", (username, password_hash))

connection.commit()
connection.close()

print("User created successfully!")