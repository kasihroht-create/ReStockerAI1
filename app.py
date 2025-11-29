import streamlit as st
import pandas as pd
import plotly.express as px
import os
from groq import Groq
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 Kunci API GROQ belum diatur!")
    st.stop()

# Page Config
st.set_page_config(
    page_title="ReStockerAI – Multi Company Comparison",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 ReStockerAI – Multi-Company Inventory Comparison")
st.write("AI-powered Inventory Benchmarking & Restock Intelligence")

# Upload File
uploaded_file = st.file_uploader("📂 Upload Data Inventory (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    required_columns = [
        "Company_Name",
        "Product",
        "Current_Stock",
        "Average_Daily_Sales",
        "Lead_Time_Days"
    ]

    if not all(col in df.columns for col in required_columns):
        st.error("⚠️ Format Excel tidak sesuai template!")
        st.stop()

    # Calculation
    df["Estimated_Demand"] = df["Average_Daily_Sales"] * df["Lead_Time_Days"]
    df["Stock_Gap"] = df["Current_Stock"] - df["Estimated_Demand"]

    def stock_status(gap):
        if gap < 0:
            return "🚨 Stockout Risk"
        elif gap > 50:
            return "⚠️ Overstock"
        else:
            return "✅ Safe Stock"

    df["Stock_Status"] = df["Stock_Gap"].apply(stock_status)

    # Company selection
    companies = df["Company_Name"].unique()

    selected_companies = st.multiselect(
        "🏢 Pilih 2 Perusahaan untuk Dibandingkan",
        companies,
        default=companies[:2]
    )

    df_compare = df[df["Company_Name"].isin(selected_companies)]

    # Preview
    st.subheader("📊 Data Inventory")
    st.dataframe(df_compare)

    # Visualization
    st.subheader("📈 Perbandingan Stock Gap")
    fig_gap = px.bar(
        df_compare,
        x="Product",
        y="Stock_Gap",
        color="Company_Name",
        barmode="group",
        title="Stock Gap Comparison"
    )
    st.plotly_chart(fig_gap)

    st.subheader("📉 Predicted Demand Comparison")
    fig_demand = px.line(
        df_compare,
        x="Product",
        y="Estimated_Demand",
        color="Company_Name",
        markers=True
    )
    st.plotly_chart(fig_demand)

    # AI Analysis
    st.subheader("🤖 AI Comparative Inventory Insight")

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role
