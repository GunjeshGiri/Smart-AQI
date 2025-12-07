# src/dashboard_streamlit.py
# Minimal Streamlit dashboard skeleton
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Smart-AQI Dashboard", layout="wide")

st.title("Smart-AQI — Dashboard (Skeleton)")
st.markdown("This is a skeleton Streamlit dashboard. Populate charts and maps after you have data.")

uploaded = st.file_uploader("Upload processed features parquet", type=['parquet'])
if uploaded:
    df = pd.read_parquet(uploaded)
    st.write("Loaded", len(df), "rows")
    st.dataframe(df.head())
else:
    st.info("Upload a `data/processed/features.parquet` file to visualize.")
