import pandas as pd
import streamlit as st

st.set_page_config(page_title="SmartStock Optimizer", layout="wide")
st.title("SmartStock Inventory Rebalancer")

# Load your data
@st.cache_data
def load_data():
    df = pd.read_csv("your_final_dataframe.csv")         # Inventory + forecast data
    transfers = pd.read_csv("transfer_output.csv")       # Transfer suggestions
    return df, transfers

df, transfers_df = load_data()

# --- KPI Section ---
def compute_availability(df, transfers_df):
    latest_day = df['day'].max()
    df_day = df[df['day'] == latest_day].copy()

    df_day['available'] = df_day['inventory'] >= df_day['forecasted_demand']
    before = df_day['available'].mean() * 100

    for _, row in transfers_df.iterrows():
        from_mask = (df_day['store_id'] == row['from_store']) & (df_day['product_id'] == row['product'])
        to_mask = (df_day['store_id'] == row['to_store']) & (df_day['product_id'] == row['product'])

        df_day.loc[from_mask, 'inventory'] -= row['quantity']
        df_day.loc[to_mask, 'inventory'] += row['quantity']

    df_day['available'] = df_day['inventory'] >= df_day['forecasted_demand']
    after = df_day['available'].mean() * 100
    return before, after

before, after = compute_availability(df, transfers_df)

# --- KPI Display ---
kpi1, kpi2 = st.columns(2)
kpi1.metric("Availability Before Transfers", f"{before:.2f}%")
kpi2.metric("Availability After Transfers", f"{after:.2f}%")

st.markdown("---")

# --- Filters ---
st.subheader("Explore Transfers by Store or Product")

col1, col2 = st.columns(2)
with col1:
    store_filter = st.selectbox("Filter by Store", ["All"] + sorted(df['store_id'].unique()))
with col2:
    product_filter = st.selectbox("Filter by Product", ["All"] + sorted(df['product_id'].unique()))

filtered = transfers_df.copy()
if store_filter != "All":
    filtered = filtered[(filtered['from_store'] == store_filter) | (filtered['to_store'] == store_filter)]
if product_filter != "All":
    filtered = filtered[filtered['product'] == product_filter]

st.dataframe(filtered, use_container_width=True)

st.markdown("---")

# --- Raw Data Viewer ---
with st.expander("Raw Inventory + Forecast Data (Latest Day Only)"):
    latest_day = df['day'].max()
    st.dataframe(df[df['day'] == latest_day], use_container_width=True)
