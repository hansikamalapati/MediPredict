import os

from flask import Flask, render_template
from database import get_connection
from ml.predict_demand import predict_medicine_demand


app = Flask(__name__)


# ============================================================
# GET MEDICINE PREDICTIONS
# ============================================================

def get_medicine_predictions():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
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
        FROM medicines
        ORDER BY name
    """)

    medicines = cursor.fetchall()

    results = []

    for medicine in medicines:

        # Get recent usage history
        cursor.execute("""
            SELECT quantity_used
            FROM usage_history
            WHERE medicine_id = ?
            ORDER BY usage_date DESC
            LIMIT 30
        """, (medicine["id"],))

        usage_records = cursor.fetchall()

        # ----------------------------------------------------
        # ML PREDICTION
        # ----------------------------------------------------

        try:

            predicted_usage = predict_medicine_demand(
                medicine["id"]
            )

            if predicted_usage is not None and predicted_usage > 0:

                average_usage = predicted_usage

            else:

                average_usage = medicine["daily_usage"]

        except Exception as error:

            print(
                f"ML prediction error for "
                f"{medicine['name']}: {error}"
            )

            # Fallback to historical average
            if usage_records:

                total_usage = sum(
                    row["quantity_used"]
                    for row in usage_records
                )

                average_usage = (
                    total_usage / len(usage_records)
                )

            else:

                average_usage = medicine["daily_usage"]

        # ----------------------------------------------------
        # STOCKOUT CALCULATION
        # ----------------------------------------------------

        if average_usage > 0:

            days_remaining = (
                medicine["current_stock"]
                / average_usage
            )

        else:

            days_remaining = 999

        # ----------------------------------------------------
        # REORDER CALCULATION
        # ----------------------------------------------------

        delivery_demand = (
            average_usage
            * medicine["lead_time"]
        )

        # Keep 7 days as safety stock
        safety_stock = average_usage * 7

        recommended_stock = (
            delivery_demand
            + safety_stock
        )

        reorder_quantity = max(
            0,
            recommended_stock
            - medicine["current_stock"]
        )

        # ----------------------------------------------------
        # RISK LEVEL
        # ----------------------------------------------------

        if days_remaining <= medicine["lead_time"]:

            risk = "HIGH"

        elif days_remaining <= (
            medicine["lead_time"] + 7
        ):

            risk = "MEDIUM"

        else:

            risk = "LOW"

        # ----------------------------------------------------
        # STORE RESULT
        # ----------------------------------------------------

        results.append({

            "id": medicine["id"],

            "name": medicine["name"],

            "current_stock": medicine["current_stock"],

            "minimum_stock": medicine["minimum_stock"],

            "supplier": medicine["supplier"],

            "lead_time": medicine["lead_time"],

            "daily_usage": medicine["daily_usage"],

            # ML predicted daily demand
            "average_usage": round(
                average_usage,
                1
            ),

            "days_remaining": round(
                days_remaining,
                1
            ),

            "risk": risk,

            "reorder_quantity": round(
                reorder_quantity
            ),

            "category": medicine["category"],

            "dosage_form": medicine["dosage_form"],

            "strength": medicine["strength"],

            "maximum_stock": medicine["maximum_stock"],

            "unit_price": medicine["unit_price"],

            "expiry_date": medicine["expiry_date"],

            "last_restocked": medicine["last_restocked"]

        })

    connection.close()

    return results


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    medicines = get_medicine_predictions()

    total_medicines = len(medicines)

    high_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "HIGH"
    )

    medium_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "MEDIUM"
    )

    low_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "LOW"
    )

    return render_template(
        "index.html",
        medicines=medicines,
        total_medicines=total_medicines,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk
    )


# ============================================================
# MEDICINES PAGE
# ============================================================

@app.route("/medicines")
def medicines_page():

    medicines = get_medicine_predictions()

    return render_template(
        "medicines.html",
        medicines=medicines
    )


# ============================================================
# PREDICTIONS PAGE
# ============================================================

@app.route("/predictions")
def predictions():

    medicines = get_medicine_predictions()

    total_medicines = len(medicines)

    high_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "HIGH"
    )

    medium_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "MEDIUM"
    )

    low_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "LOW"
    )

    return render_template(
        "predictions.html",
        medicines=medicines,
        total_medicines=total_medicines,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk
    )


# ============================================================
# ANALYTICS PAGE
# ============================================================

@app.route("/analytics")
def analytics():

    medicines = get_medicine_predictions()

    total_medicines = len(medicines)

    high_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "HIGH"
    )

    medium_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "MEDIUM"
    )

    low_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "LOW"
    )

    return render_template(
        "analytics.html",
        medicines=medicines,
        total_medicines=total_medicines,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk
    )


# ============================================================
# ALERTS PAGE
# ============================================================

@app.route("/alerts")
def alerts():

    medicines = get_medicine_predictions()

    total_medicines = len(medicines)

    high_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "HIGH"
    )

    medium_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "MEDIUM"
    )

    low_risk = sum(
        1
        for medicine in medicines
        if medicine["risk"] == "LOW"
    )

    return render_template(
        "alerts.html",
        medicines=medicines,
        total_medicines=total_medicines,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk
    )


# ============================================================
# ML PREDICTION API
# ============================================================

@app.route("/api/predict/<int:medicine_id>")
def api_predict(medicine_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            current_stock
        FROM medicines
        WHERE id = ?
    """, (medicine_id,))

    medicine = cursor.fetchone()

    connection.close()

    # Medicine not found
    if medicine is None:

        return {
            "success": False,
            "message": "Medicine not found"
        }, 404

    try:

        predicted_demand = predict_medicine_demand(
            medicine_id
        )

        return {

            "success": True,

            "medicine_id": medicine["id"],

            "medicine_name": medicine["name"],

            "current_stock": medicine["current_stock"],

            "predicted_daily_demand": predicted_demand

        }

    except Exception as error:

        return {

            "success": False,

            "message": str(error)

        }, 500


# ============================================================
# RUN APPLICATION
# GOOGLE CLOUD RUN READY
# ============================================================

if __name__ == "__main__":

    # Cloud Run provides the PORT environment variable.
    # Locally, it will use port 5000.

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(

        host="0.0.0.0",

        port=port,

        debug=False

    )