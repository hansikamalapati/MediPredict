import sqlite3
import pandas as pd
import joblib


MODEL_PATH = "ml/medicine_demand_model.pkl"


def predict_medicine_demand(medicine_id):
    # Load trained ML model
    model = joblib.load(MODEL_PATH)

    # Connect to database
    connection = sqlite3.connect("medipredict.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Get medicine information
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

    # Get usage history
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

    if len(history) < 7:
        return medicine["daily_usage"]

    # Convert history to DataFrame
    data = pd.DataFrame(
        history,
        columns=["usage_date", "quantity_used"]
    )

    data["usage_date"] = pd.to_datetime(data["usage_date"])

    data = data.sort_values("usage_date")

    # Previous usage
    previous_usage = data["quantity_used"].iloc[-1]

    previous_usage_2 = data["quantity_used"].iloc[-2]

    # Recent averages
    average_3_days = data["quantity_used"].tail(3).mean()

    average_7_days = data["quantity_used"].tail(7).mean()

    # Day of week
    last_date = data["usage_date"].iloc[-1]

    day_of_week = last_date.dayofweek

    # Create input for ML model
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

    # Predict next-day demand
    prediction = model.predict(input_data)

    predicted_usage = float(prediction[0])

    # Make sure prediction is not negative
    predicted_usage = max(0, predicted_usage)

    return round(predicted_usage, 2)
if __name__ == "__main__":
    result = predict_medicine_demand(1)

    print("Predicted demand:", result)