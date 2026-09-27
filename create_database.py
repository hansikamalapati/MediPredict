from database import get_connection


connection = get_connection()

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    current_stock INTEGER NOT NULL,
    minimum_stock INTEGER NOT NULL,
    supplier TEXT,
    lead_time INTEGER NOT NULL,
    daily_usage REAL NOT NULL
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS usage_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id INTEGER,
    usage_date TEXT,
    quantity_used INTEGER,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
)
""")


connection.commit()

connection.close()


print("Database created successfully!")
connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_usage_medicine_date
ON usage_history (medicine_id, usage_date)
""")

connection.commit()
connection.close()

print("Database index created successfully!")