# SmartStock Optimizer
[https://smartstock-optimizer-wy579k5xubnwdezrkryeke.streamlit.app/]
SmartStock Optimizer is a supply chain intelligence web app that uses machine learning to predict product demand and suggest inventory transfers between stores to maximize product availability and reduce overstock.

Built using Python, Streamlit, and XGBoost, the tool enables store managers and analysts to make data-driven transfer decisions.

---

## Problem Statement

In retail operations, uneven product demand across locations leads to:
- Overstocking at some stores (resulting in high holding costs)
- Stockouts at others (leading to lost sales and poor customer experience)

SmartStock Optimizer solves this by:
- Forecasting demand at a store-SKU level
- Identifying stock surpluses and deficits
- Generating transfer plans to balance inventory efficiently

---

## Features

### Upload Inventory and Sales CSV
- Accepts a CSV file with columns like `store_id`, `product_id`, `inventory`, and `date`
- Automatically derives `day_of_week` for forecasting

### Demand Forecasting
- Uses a pre-trained XGBoost model to predict product demand
- Forecasts are displayed alongside actual inventory

### Transfer Planning
- Finds understocked and overstocked stores per product
- Suggests optimal transfer quantities between stores
- Allows download of transfer plan as CSV

### Visual KPIs and Charts
- Availability before and after transfers
- Inventory gap bar charts
- Forecast distribution box plots
- Transfer heatmaps between stores

---

## Sample Input Format

```csv
store_id,product_id,date,inventory
101,P01,2025-06-28,50
102,P01,2025-06-28,20
103,P01,2025-06-28,90
```
Updating the Model
To update model with your own data:
```
from xgboost import XGBRegressor
import joblib

model = XGBRegressor()
model.fit(X_train, y_train)

joblib.dump(model, "xgb_model.pkl")
joblib.dump(X_train.columns.tolist(), "model_columns.pkl")
```
Replace the .pkl files in your repo and redeploy.



Contact
**Author:** [Ankit Anand Singh](https://github.com/Ankit2244)
Feel free to raise issues or contribute to the project!
Let me know if you'd also like the `requirements.txt` or a sample input CSV to match the README.
