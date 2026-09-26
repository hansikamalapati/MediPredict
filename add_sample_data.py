from database import get_connection


connection = get_connection()

cursor = connection.cursor()


medicines = [
    ("Paracetamol", 1200, 300, "ABC Pharma", 5, 50),
    ("Amoxicillin", 150, 200, "MediSupply", 8, 30),
    ("Insulin", 500, 100, "HealthCare Ltd", 10, 12),
    ("Ceftriaxone", 100, 150, "PharmaCorp", 7, 25),
    ("Azithromycin", 800, 200, "MediSupply", 5, 20)
]


cursor.executemany("""
INSERT INTO medicines
(name, current_stock, minimum_stock, supplier, lead_time, daily_usage)
VALUES (?, ?, ?, ?, ?, ?)
""", medicines)


connection.commit()

connection.close()


print("Sample medicines added successfully!")