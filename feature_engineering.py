import os
import pandas as pd
import numpy as np
import mysql.connector
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# ✅ UPDATE THIS
# -----------------------------
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "Db@17022001",     # 🔥 change this
    "database": "credit_risk_db",    # 🔥 change if needed
    "port": 3306
}

TABLES = ["loan_applications", "transactions", "credit_bureau_reports"]

# Folder to store plots
PLOT_DIR = "dq_plots"


# -----------------------------
# Helpers
# -----------------------------
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_table_as_df(table_name: str) -> pd.DataFrame:
    conn = connect_db()
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def convert_to_numeric(series: pd.Series) -> pd.Series:
    """
    Converts raw strings like:
    '₹1,20,000' -> 120000
    '--', 'N/A' -> NaN
    """
    cleaned = (
        series.astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .replace({"--": np.nan, "N/A": np.nan, "None": np.nan})
    )
    return pd.to_numeric(cleaned, errors="coerce")

def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df)) * 100
    rep = pd.DataFrame({
        "missing_count": missing_count,
        "missing_pct": missing_pct.round(2)
    }).sort_values("missing_pct", ascending=False)
    return rep

def duplicate_report(df: pd.DataFrame, subset_cols=None) -> dict:
    full_dups = int(df.duplicated().sum())
    subset_dups = int(df.duplicated(subset=subset_cols).sum()) if subset_cols else None
    return {"full_row_duplicates": full_dups, "subset_duplicates": subset_dups}

def remove_duplicates(df: pd.DataFrame, subset_cols=None) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset_cols, keep="first")

def zscore_outlier_count(x: pd.Series, threshold=3.0) -> int:
    x = x.dropna()
    if len(x) < 10:
        return 0
    mean = x.mean()
    std = x.std()
    if std == 0:
        return 0
    z = (x - mean) / std
    return int((np.abs(z) > threshold).sum())

def iqr_outlier_count(x: pd.Series) -> int:
    x = x.dropna()
    if len(x) < 10:
        return 0
    q1 = x.quantile(0.25)
    q3 = x.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((x < lower) | (x > upper)).sum())

def save_outlier_plots(series: pd.Series, table_name: str, col_name: str):
    """
    Saves:
    1) Histogram (normal distribution view)
    2) Box plot (outlier view)
    """
    os.makedirs(PLOT_DIR, exist_ok=True)

    x = series.dropna()
    if len(x) < 10:
        return None

    # Histogram plot
    plt.figure()
    plt.hist(x, bins=30)
    plt.title(f"{table_name} | {col_name} | Histogram")
    plt.xlabel(col_name)
    plt.ylabel("Frequency")
    hist_path = os.path.join(PLOT_DIR, f"{table_name}_{col_name}_hist.png")
    plt.savefig(hist_path, bbox_inches="tight")
    plt.close()

    # Box plot
    plt.figure()
    plt.boxplot(x, vert=False)
    plt.title(f"{table_name} | {col_name} | Boxplot")
    plt.xlabel(col_name)
    box_path = os.path.join(PLOT_DIR, f"{table_name}_{col_name}_box.png")
    plt.savefig(box_path, bbox_inches="tight")
    plt.close()

    return hist_path, box_path


# -----------------------------
# Main function
# -----------------------------
def run_data_quality_validation():
    os.makedirs(PLOT_DIR, exist_ok=True)

    report_lines = []
    report_lines.append("✅ DATA QUALITY VALIDATION REPORT (with Plots)")
    report_lines.append(f"Generated at: {datetime.now()}")
    report_lines.append("")

    for table in TABLES:
        df = fetch_table_as_df(table)

        report_lines.append("=" * 70)
        report_lines.append(f"TABLE: {table}")
        report_lines.append("=" * 70)
        report_lines.append(f"Rows: {len(df)} | Columns: {len(df.columns)}")
        report_lines.append("")

        # ✅ 1) Column Data Types
        report_lines.append("📌 Column Data Types:")
        dtypes_df = pd.DataFrame({"column": df.columns, "dtype": df.dtypes.astype(str).values})
        report_lines.append(dtypes_df.to_string(index=False))
        report_lines.append("")

        # ✅ 2) Missing Values
        report_lines.append("📌 Missing Values (Top 15):")
        mv = missing_value_report(df)
        report_lines.append(mv.head(15).to_string())
        report_lines.append("")

        # ✅ 3) Duplicate Check
        subset_key = ["customer_id"]
        if table == "transactions":
            subset_key = ["customer_id", "transaction_date", "transaction_type", "transaction_amount"]

        dup_info = duplicate_report(df, subset_cols=subset_key)
        report_lines.append("📌 Duplicate Check:")
        report_lines.append(f"Full row duplicates: {dup_info['full_row_duplicates']}")
        report_lines.append(f"Subset duplicates ({subset_key}): {dup_info['subset_duplicates']}")
        report_lines.append("")

        # ✅ Remove duplicates (Optional output)
        cleaned_df = remove_duplicates(df, subset_cols=subset_key)
        cleaned_df.to_csv(f"cleaned_{table}.csv", index=False)
        report_lines.append(f"✅ Saved duplicates-removed file: cleaned_{table}.csv")
        report_lines.append("")

        # ✅ 4) Numeric Describe
        report_lines.append("📌 Numeric Summary (describe):")

        numeric_cols = []
        temp_df = df.copy()

        # Convert important raw columns to numeric for analysis
        convert_cols = []
        if table == "loan_applications":
            convert_cols = ["declared_income", "loan_amount", "loan_tenure_months", "existing_loans"]
        elif table == "transactions":
            convert_cols = ["transaction_amount", "account_balance"]
        elif table == "credit_bureau_reports":
            convert_cols = ["credit_score", "credit_utilization_ratio", "total_outstanding_amount",
                            "enquiries_last_6m", "total_outstanding_loans"]

        for col in convert_cols:
            if col in temp_df.columns:
                temp_df[col + "_num"] = convert_to_numeric(temp_df[col])
                numeric_cols.append(col + "_num")

        # Add already numeric columns too
        for col in temp_df.columns:
            if pd.api.types.is_numeric_dtype(temp_df[col]) and col not in numeric_cols:
                numeric_cols.append(col)

        numeric_cols = list(dict.fromkeys(numeric_cols))  # unique preserve order

        if len(numeric_cols) == 0:
            report_lines.append("No numeric columns found.\n")
        else:
            desc = temp_df[numeric_cols].describe().T
            report_lines.append(desc.to_string())
            report_lines.append("")

        # ✅ 5) Outlier Detection + Plots
        report_lines.append("📌 Outlier Detection (Z-score & IQR) + Plot paths:")

        outlier_rows = []
        for col in numeric_cols:
            s = temp_df[col]
            z_out = zscore_outlier_count(s)
            iqr_out = iqr_outlier_count(s)

            plot_paths = save_outlier_plots(s, table, col)
            if plot_paths:
                hist_path, box_path = plot_paths
            else:
                hist_path, box_path = None, None

            outlier_rows.append([col, z_out, iqr_out, hist_path, box_path])

        outlier_df = pd.DataFrame(
            outlier_rows,
            columns=["numeric_column", "zscore_outliers", "iqr_outliers", "hist_plot", "box_plot"]
        )

        report_lines.append(outlier_df.to_string(index=False))
        report_lines.append("\n")

    # Save report
    with open("data_quality_report_v2.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("✅ Data Quality Validation Completed!")
    print("Generated:")
    print("  ✅ data_quality_report_v2.txt")
    print("  ✅ cleaned_*.csv (duplicate removed versions)")
    print(f"  ✅ Outlier plots saved in: {PLOT_DIR}/")


if __name__ == "__main__":
    run_data_quality_validation()
