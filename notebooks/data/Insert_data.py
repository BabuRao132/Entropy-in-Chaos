import random
import numpy as np
import mysql.connector
from datetime import datetime, timedelta

# -------------------------------
# ✅ EDIT THESE VALUES
# -------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Db@17022001",   # 🔥 change this
    "database": "credit_risk_db"   # 🔥 change if your DB name is different
}

# -----------------------------
# RAW / Dirty Data Helpers
# -----------------------------
def maybe_missing(value, p=0.05):
    return None if random.random() < p else value

def dirty_money(num):
    r = random.random()
    if r < 0.10:
        return f"{num:,}"               # 1,20,000
    elif r < 0.15:
        return f"₹{num:,}"              # ₹1,20,000
    elif r < 0.18:
        return "--"
    elif r < 0.20:
        return "N/A"
    return str(num)

def dirty_gender():
    return random.choice(["M", "F", "Male", "Female", "male", "female", None])

def dirty_employment():
    return random.choice([
        "Salaried", "SALARIED", "job",
        "Self Employed", "self-employed", "SELF_EMP", "business",
        "Student", "STUDENT", None
    ])

def dirty_date(dt: datetime):
    r = random.random()
    if r < 0.05:
        return "2025-13-40"             # invalid date
    elif r < 0.10:
        return dt.strftime("%d/%m/%Y")  # different format
    return dt.strftime("%Y-%m-%d")

def dirty_credit_score():
    r = random.random()
    if r < 0.04:
        return random.choice(["50", "1200", None])
    return str(random.randint(300, 900))

def dirty_utilization():
    r = random.random()
    if r < 0.04:
        return random.choice(["-0.5", "1.5", None])
    return str(round(random.uniform(0.0, 1.0), 2))

def dirty_delinquency_count():
    r = random.random()
    if r < 0.05:
        return random.choice(["NA", "two", None])
    return str(random.randint(0, 6))

# -----------------------------
# Insert Data into MySQL
# -----------------------------
def insert_data(
    n_customers=500,
    min_txn_per_customer=5,
    max_txn_per_customer=20,
    seed=42
):
    random.seed(seed)
    np.random.seed(seed)

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # ✅ Generate customer_ids
    customer_ids = list(range(100000, 100000 + n_customers))

    # -----------------------------
    # 1) Insert into customers
    # -----------------------------
    customers_data = []
    for cid in customer_ids:
        created_at = datetime.now() - timedelta(days=random.randint(1, 200))
        customers_data.append((cid, created_at.strftime("%Y-%m-%d %H:%M:%S")))

    cursor.executemany(
        "INSERT IGNORE INTO customers (customer_id, created_at) VALUES (%s, %s)",
        customers_data
    )
    conn.commit()
    print("✅ Inserted customers")

    # -----------------------------
    # 2) Insert into loan_applications
    # -----------------------------
    loan_purposes = ["Home", "Education", "Personal", "Car", "Medical", "Business"]
    loan_apps_data = []

    for cid in customer_ids:
        age = maybe_missing(random.randint(21, 60), 0.03)
        gender = maybe_missing(dirty_gender(), 0.05)
        employment_type = maybe_missing(dirty_employment(), 0.06)

        income_val = random.randint(150000, 1200000)
        declared_income = maybe_missing(dirty_money(income_val), 0.07)

        loan_amt_val = random.randint(50000, 800000)
        loan_amount = maybe_missing(dirty_money(loan_amt_val), 0.06)

        loan_tenure_months = random.choice([6, 12, 18, 24, 36, 48, 60, 0, -12])
        loan_purpose = random.choice(loan_purposes)
        existing_loans = maybe_missing(random.randint(0, 5), 0.03)

        delinquency_count_6m = maybe_missing(dirty_delinquency_count(), 0.05)
        delinquency_count_12m = maybe_missing(dirty_delinquency_count(), 0.05)

        last_delinq = datetime(2025, 1, 1) + timedelta(days=random.randint(1, 365))
        last_delinquency_date = maybe_missing(dirty_date(last_delinq), 0.05)

        created_at = datetime.now() - timedelta(days=random.randint(1, 200))

        loan_apps_data.append((
            cid,
            age,
            gender,
            employment_type,
            declared_income,
            loan_amount,
            loan_tenure_months,
            loan_purpose,
            existing_loans,
            delinquency_count_6m,
            delinquency_count_12m,
            last_delinquency_date,
            created_at.strftime("%Y-%m-%d %H:%M:%S")
        ))

    cursor.executemany("""
        INSERT INTO loan_applications (
            customer_id, age, gender, employment_type, declared_income,
            loan_amount, loan_tenure_months, loan_purpose, existing_loans,
            delinquency_count_6m, delinquency_count_12m, last_delinquency_date,
            created_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, loan_apps_data)
    conn.commit()
    print("✅ Inserted loan_applications")

    # -----------------------------
    # 3) Insert into transactions
    # -----------------------------
    transactions_data = []
    base_date = datetime(2025, 1, 1)

    for cid in customer_ids:
        txn_count = random.randint(min_txn_per_customer, max_txn_per_customer)
        balance = random.randint(1000, 50000)

        for _ in range(txn_count):
            txn_date = base_date + timedelta(days=random.randint(1, 365))
            txn_type = random.choice(["credit", "debit", None])

            amount_val = random.randint(200, 20000)

            # outlier
            if random.random() < 0.01:
                amount_val *= 25

            if txn_type == "credit":
                balance += amount_val
            elif txn_type == "debit":
                balance -= amount_val

            transaction_amount = maybe_missing(dirty_money(amount_val), 0.03)
            account_balance = maybe_missing(dirty_money(max(balance, 0)), 0.03)

            created_at = datetime.now() - timedelta(days=random.randint(1, 200))

            transactions_data.append((
                cid,
                dirty_date(txn_date),
                txn_type,
                transaction_amount,
                account_balance,
                created_at.strftime("%Y-%m-%d %H:%M:%S")
            ))

    cursor.executemany("""
        INSERT INTO transactions (
            customer_id, transaction_date, transaction_type,
            transaction_amount, account_balance, created_at
        )
        VALUES (%s,%s,%s,%s,%s,%s)
    """, transactions_data)
    conn.commit()
    print("✅ Inserted transactions")

    # -----------------------------
    # 4) Insert into credit_bureau_reports
    # -----------------------------
    bureau_data = []
    for cid in customer_ids:
        credit_score = maybe_missing(dirty_credit_score(), 0.04)
        enquiries_last_6m = random.randint(0, 12)
        credit_utilization_ratio = maybe_missing(dirty_utilization(), 0.04)

        total_outstanding_loans = random.randint(0, 5)
        outstanding_amt_val = total_outstanding_loans * random.randint(5000, 150000)
        total_outstanding_amount = maybe_missing(dirty_money(outstanding_amt_val), 0.05)

        created_at = datetime.now() - timedelta(days=random.randint(1, 200))

        bureau_data.append((
            cid,
            credit_score,
            enquiries_last_6m,
            credit_utilization_ratio,
            total_outstanding_loans,
            total_outstanding_amount,
            created_at.strftime("%Y-%m-%d %H:%M:%S")
        ))

    cursor.executemany("""
        INSERT INTO credit_bureau_reports (
            customer_id, credit_score, enquiries_last_6m,
            credit_utilization_ratio, total_outstanding_loans,
            total_outstanding_amount, created_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, bureau_data)
    conn.commit()
    print("✅ Inserted credit_bureau_reports")

    cursor.close()
    conn.close()

    print("\n✅ ALL DATA INSERTED SUCCESSFULLY INTO MYSQL 🎉")


if __name__ == "__main__":
    insert_data(n_customers=500)
