import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import check_password_hash

from database import get_connection
from ml.predict_demand import predict_medicine_demand


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "medipredict-development-secret-key"
)


# =========================================================
# FLASK LOGIN
# =========================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# =========================================================
# USER CLASS
# =========================================================

class User(UserMixin):

    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password


# =========================================================
# LOAD USER
# =========================================================

@login_manager.user_loader
def load_user(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, username, password
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    connection.close()

    if user:
        return User(
            user["id"],
            user["username"],
            user["password"]
        )

    return None


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, username, password
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            logged_user = User(
                user["id"],
                user["username"],
                user["password"]
            )

            login_user(logged_user)

            return redirect(
                url_for("dashboard")
            )

        error = "Invalid username or password."

    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# =========================================================
# CREATE PREDICTION DATA
# =========================================================

def get_prediction_data():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
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
        """
    )

    medicines = cursor.fetchall()

    connection.close()

    prediction_list = []

    for medicine in medicines:

        medicine_id = medicine["id"]

        # =================================================
        # ML PREDICTION
        # =================================================

        try:

            predicted_demand = predict_medicine_demand(
                medicine_id
            )

            if (
                predicted_demand is None
                or predicted_demand <= 0
            ):
                predicted_demand = medicine["daily_usage"]

        except Exception:

            predicted_demand = medicine["daily_usage"]

        # Safety fallback
        if (
            predicted_demand is None
            or predicted_demand <= 0
        ):
            predicted_demand = 1

        # =================================================
        # DAYS REMAINING
        # =================================================

        days_remaining = (
            medicine["current_stock"]
            / predicted_demand
        )

        # Display whole number of days
        days_remaining_display = round(
            days_remaining
        )

        # =================================================
        # SUPPLIER DELIVERY DEMAND
        # =================================================

        delivery_demand = (
            predicted_demand
            * medicine["lead_time"]
        )

        # =================================================
        # SAFETY STOCK
        # =================================================

        safety_stock = (
            predicted_demand * 7
        )

        # =================================================
        # RECOMMENDED STOCK
        # =================================================

        recommended_stock = (
            delivery_demand
            + safety_stock
        )

        # =================================================
        # REORDER QUANTITY
        # =================================================

        reorder_quantity = max(
            0,
            round(
                recommended_stock
                - medicine["current_stock"]
            )
        )

        # =================================================
        # RISK
        # =================================================

        if days_remaining <= medicine["lead_time"]:

            risk = "HIGH"

        elif days_remaining <= (
            medicine["lead_time"] + 7
        ):

            risk = "MEDIUM"

        else:

            risk = "LOW"

        # =================================================
        # CREATE PREDICTION DICTIONARY
        # =================================================

        prediction_list.append({

            "id": medicine["id"],

            "name": medicine["name"],

            "current_stock": medicine["current_stock"],

            "minimum_stock": medicine["minimum_stock"],

            "supplier": medicine["supplier"],

            "lead_time": medicine["lead_time"],

            "daily_usage": medicine["daily_usage"],

            "category": medicine["category"],

            "dosage_form": medicine["dosage_form"],

            "strength": medicine["strength"],

            "maximum_stock": medicine["maximum_stock"],

            "unit_price": medicine["unit_price"],

            "expiry_date": medicine["expiry_date"],

            "last_restocked": medicine["last_restocked"],

            "predicted_demand": round(
                predicted_demand,
                1
            ),

            "days_remaining": days_remaining_display,

            "risk": risk,

            "reorder_quantity": reorder_quantity

        })

    return prediction_list


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
@login_required
def dashboard():

    medicines = get_prediction_data()

    total_medicines = len(
        medicines
    )

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
# MEDICINE INVENTORY
# =========================================================

@app.route("/medicines")
@login_required
def medicines():

    medicine_list = get_prediction_data()

    total_medicines = len(
        medicine_list
    )

    high_risk = sum(
        1
        for medicine in medicine_list
        if medicine["risk"] == "HIGH"
    )

    medium_risk = sum(
        1
        for medicine in medicine_list
        if medicine["risk"] == "MEDIUM"
    )

    low_risk = sum(
        1
        for medicine in medicine_list
        if medicine["risk"] == "LOW"
    )

    return render_template(
        "medicines.html",
        medicines=medicine_list,
        total_medicines=total_medicines,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk
    )


# =========================================================
# ADD MEDICINE
# =========================================================

@app.route(
    "/add-medicine",
    methods=["GET", "POST"]
)
@login_required
def add_medicine():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        current_stock = request.form.get(
            "current_stock",
            0
        )

        minimum_stock = request.form.get(
            "minimum_stock",
            0
        )

        supplier = request.form.get(
            "supplier",
            ""
        ).strip()

        lead_time = request.form.get(
            "lead_time",
            0
        )

        daily_usage = request.form.get(
            "daily_usage",
            0
        )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO medicines
            (
                name,
                current_stock,
                minimum_stock,
                supplier,
                lead_time,
                daily_usage
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                float(current_stock),
                float(minimum_stock),
                supplier,
                int(lead_time),
                float(daily_usage)
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("medicines")
        )

    return render_template(
        "add_medicine.html"
    )


# =========================================================
# PREDICTIONS
# =========================================================

@app.route("/predictions")
@login_required
def predictions():

    medicine_list = get_prediction_data()

    # Send the same data using BOTH names.
    # This keeps compatibility with either
    # predictions.html version.

    return render_template(
        "predictions.html",
        medicines=medicine_list,
        predictions=medicine_list
    )


# =========================================================
# ANALYTICS
# =========================================================

@app.route("/analytics")
@login_required
def analytics():

    medicines = get_prediction_data()

    total_medicines = len(
        medicines
    )

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

    total_stock = sum(
        medicine["current_stock"]
        for medicine in medicines
    )

    total_reorder = sum(
        medicine["reorder_quantity"]
        for medicine in medicines
    )

    return render_template(
        "analytics.html",
        medicines=medicines,
        total_medicines=total_medicines,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        total_stock=total_stock,
        total_reorder=total_reorder
    )


# =========================================================
# ALERTS
# =========================================================

@app.route("/alerts")
@login_required
def alerts():

    medicines = get_prediction_data()

    high_risk_medicines = [
        medicine
        for medicine in medicines
        if medicine["risk"] == "HIGH"
    ]

    medium_risk_medicines = [
        medicine
        for medicine in medicines
        if medicine["risk"] == "MEDIUM"
    ]

    return render_template(
        "alerts.html",
        medicines=medicines,
        high_risk_medicines=high_risk_medicines,
        medium_risk_medicines=medium_risk_medicines
    )


# =========================================================
# API - PREDICT ONE MEDICINE
# =========================================================

@app.route(
    "/api/predict/<int:medicine_id>"
)
@login_required
def api_predict(medicine_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            current_stock,
            minimum_stock,
            supplier,
            lead_time,
            daily_usage
        FROM medicines
        WHERE id = ?
        """,
        (medicine_id,)
    )

    medicine = cursor.fetchone()

    connection.close()

    if medicine is None:

        return {
            "error": "Medicine not found"
        }, 404

    try:

        predicted_demand = (
            predict_medicine_demand(
                medicine_id
            )
        )

    except Exception:

        predicted_demand = (
            medicine["daily_usage"]
        )

    if (
        predicted_demand is None
        or predicted_demand <= 0
    ):

        predicted_demand = (
            medicine["daily_usage"]
        )

    if predicted_demand <= 0:

        predicted_demand = 1

    days_remaining = (
        medicine["current_stock"]
        / predicted_demand
    )

    if days_remaining <= medicine["lead_time"]:

        risk = "HIGH"

    elif days_remaining <= (
        medicine["lead_time"] + 7
    ):

        risk = "MEDIUM"

    else:

        risk = "LOW"

    delivery_demand = (
        predicted_demand
        * medicine["lead_time"]
    )

    safety_stock = (
        predicted_demand * 7
    )

    recommended_stock = (
        delivery_demand
        + safety_stock
    )

    reorder_quantity = max(
        0,
        round(
            recommended_stock
            - medicine["current_stock"]
        )
    )

    return {

        "medicine_id": medicine["id"],

        "medicine_name": medicine["name"],

        "current_stock": medicine["current_stock"],

        "predicted_demand": round(
            predicted_demand,
            2
        ),

        "days_remaining": round(
            days_remaining
        ),

        "lead_time": medicine["lead_time"],

        "risk": risk,

        "reorder_quantity": reorder_quantity

    }


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )