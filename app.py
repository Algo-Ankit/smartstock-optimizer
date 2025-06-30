import streamlit as st
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

st.set_page_config(page_title="SmartStock Inventory Rebalancer", layout="wide")

st.title("SmartStock Inventory Rebalancer")

@st.cache_data
def load_model_data(data):
    model = XGBRegressor()
    drop_cols = [col for col in ["forecasted_demand", "product", "store_id"] if col in data.columns]
    X = data.drop(columns=drop_cols)
    y = data["forecasted_demand"]
    model.fit(X, y)
    return model

uploaded_df = st.file_uploader("Upload your_final_dataframe.csv", type="csv")
uploaded_transfers = st.file_uploader("Upload transfer_output.csv", type="csv")

if uploaded_df is not None and uploaded_transfers is not None:
    df = pd.read_csv(uploaded_df)
    transfers_df = pd.read_csv(uploaded_transfers)

    model = load_model_data(df)

    def compute_availability(data, transfers):
        before = (data["inventory"] >= data["forecasted_demand"]).mean() * 100
        new_data = data.copy()
        for _, row in transfers.iterrows():
            new_data.loc[(new_data["store_id"] == row["from_store"]) & (new_data["product"] == row["product"]), "inventory"] -= row["quantity"]
            new_data.loc[(new_data["store_id"] == row["to_store"]) & (new_data["product"] == row["product"]), "inventory"] += row["quantity"]
        after = (new_data["inventory"] >= new_data["forecasted_demand"]).mean() * 100
        return before, after

    before_transfer, after_transfer = compute_availability(df, transfers_df)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Availability Before Transfers", f"{before_transfer:.2f}%")
    with col2:
        st.metric("Availability After Transfers", f"{after_transfer:.2f}%")

    st.markdown("---")
    st.subheader("Explore Transfers by Store or Product")

    stores = ["All"] + sorted(transfers_df["from_store"].unique().tolist() + transfers_df["to_store"].unique().tolist())
    products = ["All"] + sorted(transfers_df["product"].unique())

    selected_store = st.selectbox("Filter by Store", stores)
    selected_product = st.selectbox("Filter by Product", products)

    filtered_transfers = transfers_df.copy()
    if selected_store != "All":
        filtered_transfers = filtered_transfers[
            (filtered_transfers["from_store"] == selected_store) | (filtered_transfers["to_store"] == selected_store)
        ]
    if selected_product != "All":
        filtered_transfers = filtered_transfers[filtered_transfers["product"] == selected_product]

    st.dataframe(filtered_transfers, use_container_width=True)

else:
    st.warning("Please upload both 'your_final_dataframe.csv' and 'transfer_output.csv'.")
