# Credit Risk Scoring System (HCL Hackathon - Data Science & Data Engineering)

## 📌 Project Overview
This project implements an end-to-end **Credit Risk Scoring System** pipeline using three key data sources:
1. **Loan Application Data**
2. **Customer Transaction History**
3. **Credit Bureau Reports**

The objective is to build a **clean, validated, and feature-engineered customer-level dataset** (`final_feature_table.csv`) that can be used for credit risk modeling and scoring.

---

## ✅ Tech Stack
- **Python** (Pandas, NumPy, Matplotlib)
- **MySQL** (Data storage)
- **Jupyter Notebook / VS Code** (Analysis & Development)

---

## 📂 Data Sources & Tables (MySQL)
All datasets are stored in MySQL and joined using the key: `customer_id`.

### 1) `loan_applications`
Contains customer loan profile & delinquency history.
- income, loan amount, tenure
- delinquency history (6M, 12M)
- employment type, loan purpose, etc.

### 2) `transactions`
Contains customer transaction behavior.
- debit/credit transactions
- transaction amount
- account balance history

### 3) `credit_bureau_reports`
Contains bureau credit-related information.
- credit score
- credit utilization ratio
- number of enquiries in last 6 months
- outstanding loan information

---

## ✅ Data Quality Validation Performed
Data Quality checks were performed for all 3 tables using Python:

### 1️⃣ Missing Value Check
- Count and percentage of missing values were computed for each column.

### 2️⃣ Schema & Data Type Validation
- Verified presence of required columns.
- Verified and inspected datatypes of each column.

### 3️⃣ Duplicate Handling
- Checked full row duplicates
- Removed duplicates based on key columns
  - Loan applications → duplicates by `customer_id`
  - Transactions → duplicates by customer & transaction fields
  - Bureau → duplicates by `customer_id`

### 4️⃣ Outlier Detection
Outliers were detected and visualized using:
- **Histogram (Normal Distribution View)**
- **Box Plot (IQR Method View)**

---

## ✅ Data Cleaning & Transformation
Raw fields contained noisy values such as:
- `₹1,20,000`, `1,20,000`
- `--`, `N/A`
- invalid numeric and date formats

Cleaning steps included:
- Converting amount fields from text → numeric
- Handling invalid ranges
  - Credit utilization ratio clipped to **0–1**
  - Credit score fixed to valid range **300–900**
- Handling missing values using:
  - median imputation for important numeric fields
  - zero-fill for delinquency / count-based features where applicable

---

## ✅ Feature Engineering Completed
A customer-level feature dataset was created using the following engineered features:

### ✅ Financial Ratios
- **Debt-to-Income Ratio**
  - `debt_to_income = loan_amount / income`
- **Credit Utilization**
  - cleaned utilization ratio from bureau report

### ✅ Behavioral Features
- **Delayed Payments**
  - `missed_emi_months` derived using EMI transaction month gaps
- **Monthly Spend Stability**
  - stability = `std(monthly_spend) / mean(monthly_spend)`

### ✅ Derived Metrics
- **Rolling 6-Month Delinquencies**
  - derived from loan application delinquency history (6 months)
- **Account Balance Volatility**
  - volatility = `std(balance) / mean(balance)`

### ✅ Bureau Features
- **Number of Past Defaults**
  - engineered using risk indicators such as low credit score, higher delinquency and missed EMIs
- **Enquiry Rate**
  - `enquiry_rate = enquiries_last_6m / 6`

---

## ✅ Final Feature Table Generated
After all transformations and feature engineering, the final dataset contains **only the required features**:

### 📌 Output File: `final_feature_table.csv`

| Feature Name | Description |
|------------|-------------|
| customer_id | Unique customer identifier |
| debt_to_income | Loan amount / income |
| credit_utilization_clean | Cleaned credit utilization ratio |
| missed_emi_months | Months with missing EMI payments |
| monthly_spend_stability | Spend variation per month |
| rolling_6m_delinquency | 6-month delinquency count |
| balance_volatility | Variability of account balance |
| num_past_defaults | Engineered past default count |
| enquiry_rate | Bureau enquiry rate (6M/6) |

✅ This table is ready for model training & risk scoring tasks.

---

## ▶️ How to Run (Up to Feature Table Generation)

### 1) Load tables from MySQL
Use Python to load:
- `loan_applications`
- `transactions`
- `credit_bureau_reports`

### 2) Perform Data Quality Validation
- Missing values
- Duplicates
- Outliers + plots

### 3) Perform Cleaning + Transformations
- Convert money fields to numeric
- Fix invalid ranges
- Impute missing values

### 4) Generate engineered features and merge
- Create customer-level feature table

### 5) Export final dataset
- Saved as `final_feature_table.csv`

---

## 📌 Next Steps (Not Done Yet)
- Model training (Logistic Regression / RandomForest)
- Evaluation metrics (AUC, KS)
- Explainability (SHAP / Feature importance)
- Risk bucket classification
- Dashboard visualizations

---

## ✅ Author
Hackathon participant - Data Science & Data Engineering track
