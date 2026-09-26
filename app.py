from flask import Flask, render_template
from database import get_connection


app = Flask(__name__)


# =========================================================
# FUNCTION: GET MEDICINE PREDICTIONS
# =========================================================

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

        medicine_id = medicine["id"]


        # ---------------------------------------------
        # Get last 30 days of usage
        # ---------------------------------------------

        cursor.execute("""
            SELECT quantity_used
            FROM usage_history
            WHERE medicine_id = ?
            ORDER BY usage_date DESC
            LIMIT 30
        """, (medicine_id,))

        usage_records = cursor.fetchall()


        # ---------------------------------------------
        # Calculate average daily usage
        # ---------------------------------------------

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


        # ---------------------------------------------
        # Calculate days remaining
        # ---------------------------------------------

        if average_usage > 0:

            days_remaining = (
                medicine["current_stock"]
                / average_usage
            )

        else:

            days_remaining = 999


        # ---------------------------------------------
        # Calculate demand during delivery time
        # ---------------------------------------------

        delivery_demand = (
            average_usage * medicine["lead_time"]
        )


        # ---------------------------------------------
        # Safety stock
        # We keep 7 days of extra stock
        # ---------------------------------------------

        safety_stock = (
            average_usage * 7
        )


        # ---------------------------------------------
        # Recommended stock
        # ---------------------------------------------

        recommended_stock = (
            delivery_demand + safety_stock
        )


        # ---------------------------------------------
        # Recommended reorder quantity
        # ---------------------------------------------

        reorder_quantity = max(
            0,
            recommended_stock -
            medicine["current_stock"]
        )


        # ---------------------------------------------
        # Calculate stockout risk
        # ---------------------------------------------

        if days_remaining <= medicine["lead_time"]:

            risk = "HIGH"

        elif days_remaining <= (
            medicine["lead_time"] + 7
        ):

            risk = "MEDIUM"

        else:

            risk = "LOW"


        # ---------------------------------------------
        # Store result
        # ---------------------------------------------

        results.append({

            "id":
                medicine["id"],

            "name":
                medicine["name"],

            "current_stock":
                medicine["current_stock"],

            "minimum_stock":
                medicine["minimum_stock"],

            "supplier":
                medicine["supplier"],

            "lead_time":
                medicine["lead_time"],

            "daily_usage":
                medicine["daily_usage"],

            "average_usage":
                round(average_usage, 1),

            "days_remaining":
                round(days_remaining, 1),

            "risk":
                risk,

            "reorder_quantity":
                round(reorder_quantity),

            "category":
                medicine["category"],

            "dosage_form":
                medicine["dosage_form"],

            "strength":
                medicine["strength"],

            "maximum_stock":
                medicine["maximum_stock"],

            "unit_price":
                medicine["unit_price"],

            "expiry_date":
                medicine["expiry_date"],

            "last_restocked":
                medicine["last_restocked"]

        })


    connection.close()

    return results


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    medicines = get_medicine_predictions()


    # ---------------------------------------------
    # Calculate statistics
    # ---------------------------------------------

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


# =========================================================
# MEDICINES PAGE
# =========================================================

@app.route("/medicines")
def medicines_page():

    medicines = get_medicine_predictions()

    return render_template(
        "medicines.html",
        medicines=medicines
    )


# =========================================================
# PREDICTIONS PAGE
# =========================================================

@app.route("/predictions")
def predictions():

    medicines = get_medicine_predictions()


    # ---------------------------------------------
    # Calculate statistics
    # ---------------------------------------------

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

# =========================================================
# ANALYTICS PAGE
# =========================================================

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

# =========================================================
# ALERTS PAGE
# =========================================================

@app.route("/alerts")
def alerts():

    medicines = get_medicine_predictions()


    # Calculate statistics

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
# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
