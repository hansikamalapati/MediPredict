from database import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
SELECT
    m.name,
    h.usage_date,
    h.quantity_used
FROM usage_history h
JOIN medicines m
ON h.medicine_id = m.id
ORDER BY h.usage_date DESC
LIMIT 20
""")

history = cursor.fetchall()

print("Recent Medicine Usage")
print("=====================")

for row in history:
    print(
        row["name"],
        "| Date:",
        row["usage_date"],
        "| Used:",
        row["quantity_used"]
    )

connection.close()