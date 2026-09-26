from database import get_connection
import math


# ==========================================================
# CONNECT TO DATABASE
# ==========================================================

connection = get_connection()
cursor = connection.cursor()


# ==========================================================
# GET ALL MEDICINES
# ==========================================================

cursor.execute("""
SELECT
    id,
    name,
    current_stock,
    minimum_stock,
    supplier,
    lead_time,
    daily_usage,
    maximum_stock
FROM medicines
""")

medicines = cursor.fetchall()


print()
print("==============================================")
print("        MEDIPREDICT STOCKOUT ANALYSIS")
print("==============================================")
print()


# ==========================================================
# ANALYZE EACH MEDICINE
# ==========================================================

for medicine in medicines:

    medicine_id = medicine["id"]

    name = medicine["name"]

    current_stock = medicine["current_stock"]

    minimum_stock = medicine["minimum_stock"]

    supplier = medicine["supplier"]

    lead_time = medicine["lead_time"]

    daily_usage = medicine["daily_usage"]

    maximum_stock = medicine["maximum_stock"]


    # ------------------------------------------------------
    # GET LAST 30 DAYS USAGE
    # ------------------------------------------------------

    cursor.execute("""
    SELECT
        quantity_used
    FROM usage_history
    WHERE medicine_id = ?
    ORDER BY usage_date DESC
    LIMIT 30
    """, (medicine_id,))


    usage_records = cursor.fetchall()


    # ------------------------------------------------------
    # CALCULATE AVERAGE DAILY USAGE
    # ------------------------------------------------------

    if usage_records:

        total_usage = sum(
            row["quantity_used"]
            for row in usage_records
        )

        average_usage = total_usage / len(usage_records)

    else:

        average_usage = daily_usage


    # ------------------------------------------------------
    # CALCULATE DAYS UNTIL STOCKOUT
    # ------------------------------------------------------

    if average_usage > 0:

        days_remaining = current_stock / average_usage

    else:

        days_remaining = 999


    # ------------------------------------------------------
    # CALCULATE EXPECTED USAGE DURING DELIVERY
    # ------------------------------------------------------

    delivery_demand = average_usage * lead_time


    # ------------------------------------------------------
    # DETERMINE RISK LEVEL
    # ------------------------------------------------------

    if days_remaining <= lead_time:

        risk = "HIGH"

    elif days_remaining <= lead_time + 7:

        risk = "MEDIUM"

    else:

        risk = "LOW"


    # ------------------------------------------------------
    # CALCULATE REORDER QUANTITY
    # ------------------------------------------------------

    safety_stock = average_usage * 7


    recommended_stock = (
        delivery_demand
        + safety_stock
    )


    reorder_quantity = (
        recommended_stock
        - current_stock
    )


    if reorder_quantity < 0:

        reorder_quantity = 0


    reorder_quantity = math.ceil(
        reorder_quantity
    )


    # ------------------------------------------------------
    # DISPLAY RESULTS
    # ------------------------------------------------------

    print("----------------------------------------------")

    print("Medicine       :", name)

    print("Current Stock  :", current_stock)

    print(
        "Avg Daily Use  :",
        round(average_usage, 2)
    )

    print(
        "Days Remaining :",
        round(days_remaining, 1)
    )

    print(
        "Delivery Time  :",
        lead_time,
        "days"
    )

    print(
        "Supplier       :",
        supplier
    )

    print(
        "Risk Level     :",
        risk
    )

    print(
        "Reorder Qty    :",
        reorder_quantity
    )


print("----------------------------------------------")

connection.close()