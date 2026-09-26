from database import get_connection


connection = get_connection()

cursor = connection.cursor()

cursor.execute("SELECT * FROM medicines")

medicines = cursor.fetchall()


for medicine in medicines:
    print(
        medicine["id"],
        medicine["name"],
        medicine["current_stock"],
        medicine["daily_usage"]
    )


connection.close()