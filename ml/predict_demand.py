import sqlite3
import pandas as pd
import joblib

MODEL_PATH = "ml/medicine_demand_model.pkl"

# Load the ML model only once
model = joblib.load(MODEL_PATH)


def predict_medicine_demand(medicine_id):

    connection = sqlite3.connect("medipredict.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            lead_time,
            minimum_stock,
            daily_usage
        FROM medicines
        WHERE id = ?
    """, (medicine_id,))

    medicine = cursor.fetchone()

    if medicine is None:
        connection.close()
        return None

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

    # If there is not enough history,
    # use the stored daily usage
    if len(history) < 7:
        return medicine["daily_usage"]

    data = pd.DataFrame(
        history,
        columns=["usage_date", "quantity_used"]
    )

    data["usage_date"] = pd.to_datetime(data["usage_date"])
    data = data.sort_values("usage_date")

    previous_usage = data["quantity_used"].iloc[-1]
    previous_usage_2 = data["quantity_used"].iloc[-2]

    average_3_days = data["quantity_used"].tail(3).mean()
    average_7_days = data["quantity_used"].tail(7).mean()

    last_date = data["usage_date"].iloc[-1]
    day_of_week = last_date.dayofweek

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

    prediction = model.predict(input_data)

    predicted_usage = float(prediction[0])

    predicted_usage = max(0, predicted_usage)

    return round(predicted_usage, 2)