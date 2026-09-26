import sqlite3
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split


# ---------------------------------------
# 1. Connect to MediPredict database
# ---------------------------------------

connection = sqlite3.connect("medipredict.db")

query = """
SELECT
    u.medicine_id,
    u.usage_date,
    u.quantity_used,
    m.lead_time,
    m.minimum_stock,
    m.daily_usage
FROM usage_history u
JOIN medicines m
ON u.medicine_id = m.id
ORDER BY u.medicine_id, u.usage_date
"""

data = pd.read_sql_query(query, connection)

connection.close()


# ---------------------------------------
# 2. Check the data
# ---------------------------------------

print("Total usage records:", len(data))

if data.empty:
    print("No usage data found.")
    exit()


# ---------------------------------------
# 3. Convert date
# ---------------------------------------

data["usage_date"] = pd.to_datetime(data["usage_date"])

data = data.sort_values(
    ["medicine_id", "usage_date"]
)


# ---------------------------------------
# 4. Create features
# ---------------------------------------

# Previous day's usage
data["previous_usage"] = (
    data.groupby("medicine_id")["quantity_used"]
    .shift(1)
)

# Usage from two days before
data["previous_usage_2"] = (
    data.groupby("medicine_id")["quantity_used"]
    .shift(2)
)

# Average usage of previous 3 days
data["average_3_days"] = (
    data.groupby("medicine_id")["quantity_used"]
    .transform(
        lambda x: x.shift(1).rolling(3).mean()
    )
)

# Average usage of previous 7 days
data["average_7_days"] = (
    data.groupby("medicine_id")["quantity_used"]
    .transform(
        lambda x: x.shift(1).rolling(7).mean()
    )
)

# Day of week
data["day_of_week"] = data["usage_date"].dt.dayofweek


# ---------------------------------------
# 5. Remove rows without enough history
# ---------------------------------------

data = data.dropna()


# ---------------------------------------
# 6. Select input features
# ---------------------------------------

features = [
    "medicine_id",
    "lead_time",
    "minimum_stock",
    "daily_usage",
    "previous_usage",
    "previous_usage_2",
    "average_3_days",
    "average_7_days",
    "day_of_week"
]

X = data[features]

# What we want the model to predict
y = data["quantity_used"]


# ---------------------------------------
# 7. Split data into training/testing
# ---------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ---------------------------------------
# 8. Create Machine Learning model
# ---------------------------------------

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# ---------------------------------------
# 9. Train the model
# ---------------------------------------

print("Training ML model...")

model.fit(X_train, y_train)


# ---------------------------------------
# 10. Test the model
# ---------------------------------------

predictions = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions
)

print()
print("===================================")
print("MediPredict ML Model")
print("===================================")
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Mean Absolute Error:", round(mae, 2))
print("===================================")


# ---------------------------------------
# 11. Save the trained model
# ---------------------------------------

model_path = "ml/medicine_demand_model.pkl"

joblib.dump(
    model,
    model_path
)

print()
print("ML model saved successfully!")
print("Model location:", model_path)