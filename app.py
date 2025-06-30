import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px
import base64

@st.cache_data

def load_model():
    model = joblib.load("xgb_model.pkl")
    columns = joblib.load("model_columns.pkl")
    return model, columns

model, model_columns = load_model()

st.title("SmartStock Optimizer")
st.write("Upload your inventory + sales data and get demand forecasts and optimized transfers between stores.")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file is not None:
    user_df = pd.read_csv(uploaded_file)

    if 'date' in user_df.columns:
        user_df['day_of_week'] = pd.to_datetime(user_df['date'], errors='coerce').dt.dayofweek

    X_input = user_df.copy()
    if 'forecasted_demand' in X_input.columns:
        X_input = X_input.drop(columns=['forecasted_demand'])
    for col in model_columns:
        if col not in X_input.columns:
            X_input[col] = 0
    X_input = X_input[model_columns]

    user_df['forecasted_demand'] = model.predict(X_input)

    st.subheader("Forecasted Demand")
    st.dataframe(user_df[['store_id', 'product_id', 'inventory', 'forecasted_demand']])

    forecasted_df = user_df.copy()
    transfers = []
    products = forecasted_df['product_id'].unique()

    for product in products:
        data = forecasted_df[forecasted_df['product_id'] == product].copy()
        data['gap'] = data['inventory'] - data['forecasted_demand']

        needs = data[data['gap'] < -3].sort_values(by='gap')
        surplus = data[data['gap'] > 3].sort_values(by='gap', ascending=False)

        for i, needy in needs.iterrows():
            for j, supplier in surplus.iterrows():
                transfer_qty = min(abs(needy['gap']), supplier['gap'])
                if transfer_qty <= 0:
                    continue
                transfers.append({
                    'product': product,
                    'from_store': supplier['store_id'],
                    'to_store': needy['store_id'],
                    'quantity': int(transfer_qty)
                })
                surplus.loc[j, 'gap'] -= transfer_qty
                needs.loc[i, 'gap'] += transfer_qty
                if needs.loc[i, 'gap'] >= -3:
                    break

    transfer_df = pd.DataFrame(transfers)

    st.subheader("Suggested Transfers")
    if not transfer_df.empty:
        st.dataframe(transfer_df)
        csv = transfer_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="transfer_plan.csv">Download Transfer CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.write("No transfers needed. Inventory is balanced.")

    def compute_availability(df):
        before = (df['inventory'] >= df['forecasted_demand']).mean() * 100
        after_df = df.copy()
        for _, row in transfer_df.iterrows():
            mask_from = (after_df['store_id'] == row['from_store']) & (after_df['product_id'] == row['product'])
            mask_to = (after_df['store_id'] == row['to_store']) & (after_df['product_id'] == row['product'])
            from_index = after_df[mask_from].index.min()
            to_index = after_df[mask_to].index.min()
            if pd.notna(from_index):
                after_df.at[from_index, 'inventory'] -= row['quantity']
            if pd.notna(to_index):
                after_df.at[to_index, 'inventory'] += row['quantity']
        after = (after_df['inventory'] >= after_df['forecasted_demand']).mean() * 100
        return before, after

    before, after = compute_availability(forecasted_df)
    st.metric("Availability Before Transfers", f"{before:.2f}%")
    st.metric("Availability After Transfers", f"{after:.2f}%")

    st.subheader("Visualizations")
    if st.checkbox("Inventory Gap by Store (Bar Chart)"):
        gap_df = forecasted_df.copy()
        gap_df['gap'] = gap_df['inventory'] - gap_df['forecasted_demand']
        fig = px.bar(gap_df, x='store_id', y='gap', color='product_id', title="Inventory - Forecasted Demand")
        st.plotly_chart(fig)

    if st.checkbox("Forecast Distribution per Product"):
        fig = px.box(forecasted_df, x='product_id', y='forecasted_demand', points="all",
                     title="Forecasted Demand Distribution")
        st.plotly_chart(fig)

    if not transfer_df.empty and st.checkbox("Transfer Heatmap"):
        pivot = transfer_df.pivot(index='from_store', columns='to_store', values='quantity').fillna(0)
        fig = px.imshow(pivot, text_auto=True, title="Transfer Quantities (From → To)")
        st.plotly_chart(fig)
else:
    st.info("Please upload a CSV file to begin.")
