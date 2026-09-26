from database import get_connection
from datetime import date, timedelta


# ==========================================================
# CONNECT TO DATABASE
# ==========================================================

connection = get_connection()
cursor = connection.cursor()


print("Updating MediPredict database...")


# ==========================================================
# 1. ADD EXTRA COLUMNS TO MEDICINES TABLE
# ==========================================================

columns = [
    ("category", "TEXT"),
    ("dosage_form", "TEXT"),
    ("strength", "TEXT"),
    ("maximum_stock", "INTEGER"),
    ("unit_price", "REAL"),
    ("expiry_date", "TEXT"),
    ("last_restocked", "TEXT")
]


cursor.execute("PRAGMA table_info(medicines)")

existing_columns = [
    row["name"]
    for row in cursor.fetchall()
]


for column_name, column_type in columns:

    if column_name not in existing_columns:

        cursor.execute(
            f"ALTER TABLE medicines ADD COLUMN {column_name} {column_type}"
        )


# ==========================================================
# 2. UPDATE THE ORIGINAL 5 MEDICINES
# ==========================================================

existing_data = [

    (
        "Paracetamol",
        "Pain Relief",
        "Tablet",
        "500 mg",
        2000,
        2.50,
        "2027-08-15",
        "2026-09-10"
    ),

    (
        "Amoxicillin",
        "Antibiotic",
        "Capsule",
        "500 mg",
        1000,
        5.00,
        "2027-04-20",
        "2026-09-12"
    ),

    (
        "Insulin",
        "Diabetes",
        "Injection",
        "100 IU/ml",
        800,
        35.00,
        "2027-01-15",
        "2026-09-15"
    ),

    (
        "Ceftriaxone",
        "Antibiotic",
        "Injection",
        "1 g",
        600,
        18.00,
        "2027-06-30",
        "2026-09-13"
    ),

    (
        "Azithromycin",
        "Antibiotic",
        "Tablet",
        "500 mg",
        1200,
        8.00,
        "2027-09-10",
        "2026-09-11"
    )
]


for medicine in existing_data:

    cursor.execute(
        """
        UPDATE medicines
        SET
            category = ?,
            dosage_form = ?,
            strength = ?,
            maximum_stock = ?,
            unit_price = ?,
            expiry_date = ?,
            last_restocked = ?
        WHERE name = ?
        """,
        (
            medicine[1],
            medicine[2],
            medicine[3],
            medicine[4],
            medicine[5],
            medicine[6],
            medicine[7],
            medicine[0]
        )
    )


# ==========================================================
# 3. ADD 15 MORE MEDICINES
# ==========================================================

new_medicines = [

    (
        "Metformin",
        700,
        300,
        "MediSupply",
        6,
        35,
        "Diabetes",
        "Tablet",
        "500 mg",
        1500,
        3.00,
        "2027-05-20",
        "2026-09-14"
    ),

    (
        "Omeprazole",
        900,
        250,
        "HealthCare Ltd",
        5,
        25,
        "Gastric",
        "Capsule",
        "20 mg",
        1400,
        2.50,
        "2027-07-18",
        "2026-09-10"
    ),

    (
        "Ibuprofen",
        400,
        250,
        "ABC Pharma",
        7,
        45,
        "Pain Relief",
        "Tablet",
        "400 mg",
        1200,
        4.00,
        "2027-03-15",
        "2026-09-08"
    ),

    (
        "Atorvastatin",
        650,
        200,
        "PharmaCorp",
        6,
        20,
        "Cardiovascular",
        "Tablet",
        "20 mg",
        1200,
        6.00,
        "2027-11-12",
        "2026-09-11"
    ),

    (
        "Amlodipine",
        500,
        200,
        "MediSupply",
        5,
        25,
        "Cardiovascular",
        "Tablet",
        "5 mg",
        1000,
        2.00,
        "2027-08-30",
        "2026-09-09"
    ),

    (
        "Pantoprazole",
        850,
        250,
        "ABC Pharma",
        4,
        40,
        "Gastric",
        "Tablet",
        "40 mg",
        1400,
        3.50,
        "2027-10-10",
        "2026-09-13"
    ),

    (
        "Cetirizine",
        300,
        180,
        "HealthCare Ltd",
        6,
        35,
        "Allergy",
        "Tablet",
        "10 mg",
        800,
        1.50,
        "2027-05-05",
        "2026-09-12"
    ),

    (
        "Doxycycline",
        250,
        180,
        "PharmaCorp",
        8,
        25,
        "Antibiotic",
        "Capsule",
        "100 mg",
        700,
        5.50,
        "2027-02-25",
        "2026-09-07"
    ),

    (
        "Salbutamol",
        450,
        150,
        "MediSupply",
        5,
        30,
        "Respiratory",
        "Inhaler",
        "100 mcg",
        900,
        12.00,
        "2027-09-20",
        "2026-09-14"
    ),

    (
        "Losartan",
        550,
        200,
        "ABC Pharma",
        7,
        30,
        "Cardiovascular",
        "Tablet",
        "50 mg",
        1100,
        4.50,
        "2027-06-15",
        "2026-09-10"
    ),

    (
        "Levothyroxine",
        600,
        200,
        "HealthCare Ltd",
        5,
        20,
        "Thyroid",
        "Tablet",
        "50 mcg",
        1000,
        2.50,
        "2027-12-10",
        "2026-09-15"
    ),

    (
        "Diclofenac",
        220,
        180,
        "PharmaCorp",
        7,
        30,
        "Pain Relief",
        "Tablet",
        "50 mg",
        700,
        3.00,
        "2027-04-12",
        "2026-09-08"
    ),

    (
        "Ondansetron",
        350,
        120,
        "MediSupply",
        6,
        20,
        "Anti-Nausea",
        "Tablet",
        "4 mg",
        600,
        5.00,
        "2027-08-05",
        "2026-09-12"
    ),

    (
        "Aspirin",
        1000,
        300,
        "ABC Pharma",
        4,
        50,
        "Cardiovascular",
        "Tablet",
        "75 mg",
        1800,
        1.50,
        "2027-09-25",
        "2026-09-14"
    ),

    (
        "Furosemide",
        280,
        150,
        "HealthCare Ltd",
        8,
        25,
        "Diuretic",
        "Tablet",
        "40 mg",
        700,
        2.50,
        "2027-03-30",
        "2026-09-06"
    )
]


for medicine in new_medicines:

    cursor.execute(
        """
        INSERT OR IGNORE INTO medicines
        (
            name,
            current_stock,
            minimum_stock,
            supplier,
            lead_time,
            daily_usage,
            category,
            dosage_form,
            strength,
            maximum_stock,
            unit_price,
            expiry_date,
            last_restocked
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        medicine
    )


# ==========================================================
# 4. CLEAR OLD DEMO HISTORY
# ==========================================================

cursor.execute("DELETE FROM usage_history")


# ==========================================================
# 5. GET ALL MEDICINES
# ==========================================================

cursor.execute(
    """
    SELECT id, name, daily_usage
    FROM medicines
    """
)

medicines = cursor.fetchall()


# ==========================================================
# 6. CREATE 30 DAYS OF HISTORICAL USAGE
# ==========================================================

print("Creating historical usage data...")


today = date.today()


for medicine in medicines:

    medicine_id = medicine["id"]

    daily_usage = medicine["daily_usage"]


    for days_ago in range(30):

        usage_date = today - timedelta(days=days_ago)


        # Create realistic variation in medicine usage
        pattern = days_ago % 7


        if pattern == 0:

            multiplier = 0.90

        elif pattern == 1:

            multiplier = 1.00

        elif pattern == 2:

            multiplier = 1.10

        elif pattern == 3:

            multiplier = 1.05

        elif pattern == 4:

            multiplier = 1.15

        elif pattern == 5:

            multiplier = 1.20

        else:

            multiplier = 0.95


        quantity_used = round(
            daily_usage * multiplier
        )


        # Make sure usage is at least 1
        if quantity_used < 1:

            quantity_used = 1


        cursor.execute(
            """
            INSERT INTO usage_history
            (
                medicine_id,
                usage_date,
                quantity_used
            )
            VALUES (?, ?, ?)
            """,
            (
                medicine_id,
                usage_date.isoformat(),
                quantity_used
            )
        )


# ==========================================================
# 7. SAVE EVERYTHING
# ==========================================================

connection.commit()


# ==========================================================
# 8. CLOSE DATABASE
# ==========================================================

connection.close()


# ==========================================================
# DONE
# ==========================================================

print()
print("========================================")
print("MediPredict database updated!")
print("========================================")
print("20 medicines available.")
print("30 days of usage history created.")
print("========================================")