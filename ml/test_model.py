import sqlite3
import pandas as pd
import joblib


# ---------------------------------------
# 1. Load the trained ML model
# ---------------------------------------

model = joblib.load("ml/medicine_demand_model.pkl")

print("ML model loaded successfully!")


# ---------------------------------------
# 2. Connect to the database
# ---------------------------------------

connection = sqlite3.connect("medipredict.db")
connection.row_factory = sqlite3.Row

cursor = connection.cursor()


# ---------------------------------------
# 3. Select one medicine
# ---------------------------------------

cursor.execute("""
    SELECT
        id,
        name,
        lead_time,
        minimum_stock,
        daily_usage
    FROM medicines
    LIMIT 1
""")

medicine = cursor.fetchone()

if medicine is None:
    print("No medicine found in database.")
    connection.close()
    exit()


medicine_id = medicine["id"]

print()
print("Medicine:", medicine["name"])


# ---------------------------------------
# 4. Get usage history
# ---------------------------------------

cursor.execute("""
    SELECT
        usage_date,
        quantity_used
    FROM usage_history
    WHERE medicine_id = ?
    ORDER BY usage_date
""", (medicine_id,))

history = cursor.fetchall()

connection.close()


# ---------------------------------------
# 5. Convert history to DataFrame
# ---------------------------------------

data = pd.DataFrame(
    history,
    columns=["usage_date", "quantity_used"]
)

data["usage_date"] = pd.to_datetime(data["usage_date"])

data = data.sort_values("usage_date")


# ---------------------------------------
# 6. Get recent usage values
# ---------------------------------------

previous_usage = data["quantity_used"].iloc[-1]

previous_usage_2 = data["quantity_used"].iloc[-2]

average_3_days = data["quantity_used"].tail(3).mean()

average_7_days = data["quantity_used"].tail(7).mean()

last_date = data["usage_date"].iloc[-1]

day_of_week = last_date.dayofweek


# ---------------------------------------
# 7. Create input for ML model
# ---------------------------------------

input_data = pd.DataFrame([{
    "medicine_id": medicine["id"],
    "lead_time": medicine["lead_time"],
    "minimum_stock": medicine["minimum_stock"],
    "daily_usage": medicine["daily_usage"],
    "previous_usage": previous_usage,
    "previous_usage_2": previous_usage_2,
    "average_3_days": average_3_days,
    "average_7_days": average_7_days,
    "day_of_week": day_of_week
}])


# ---------------------------------------
# 8. Predict next-day demand
# ---------------------------------------

prediction = model.predict(input_data)

predicted_usage = prediction[0]


# ---------------------------------------
# 9. Display result
# ---------------------------------------

print()
print("==============================")
print("MediPredict ML Prediction")
print("==============================")

print("Medicine:", medicine["name"])

print(
    "Previous day usage:",
    previous_usage
)

print(
    "Average usage (7 days):",
    round(average_7_days, 2)
)

print(
    "Predicted next-day demand:",
    round(predicted_usage, 2)
)

print("==============================")