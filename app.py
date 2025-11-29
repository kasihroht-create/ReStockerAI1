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
    st.error("🚨 GROQ API Key belum diatur!")
    st.stop()

# Page Config
st.set_page_config(
    page_title="ReStockerAI – Predictive Supply Engine",
    page_icon="🤖",
    layout="wide"
)

# Header
st.title("🤖 ReStockerAI – Predictive Supply Engine")
st.write("AI-powered Stock Forecasting & Smart Restock Recommendation")

# Upload File
uploaded_file = st.file_uploader("📂 Upload Data Persediaan (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    required_columns = [
        "Product",
        "Current_Stock",
        "Average_Daily_Sales",
        "Lead_Time_Days"
    ]

    if not all(col in df.columns for col in required_columns):
        st.error("⚠️ File harus berisi kolom Product, Current_Stock, Average_Daily_Sales, Lead_Time_Days")
        st.stop()

    # Calculations
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

    # Preview
    st.subheader("📊 Inventory Data Preview")
    st.dataframe(df)

    # Visualization
    st.subheader("📈 Stock Gap Analysis")
    fig_bar = px.bar(
        df,
        x="Product",
        y="Stock_Gap",
        color="Stock_Gap",
        title="Stock Gap per Product",
        color_continuous_scale=["red", "yellow", "green"]
    )
    st.plotly_chart(fig_bar)

    st.subheader("📉 Current Stock vs Predicted Demand")
    fig_line = px.line(
        df,
        x="Product",
        y=["Current_Stock", "Estimated_Demand"],
        markers=True
    )
    st.plotly_chart(fig_line)

    # AI SECTION
    st.subheader("🤖 AI Inventory Insight")

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an AI supply chain and inventory optimization expert."
            },
            {
                "role": "user",
                "content": f"""
Analyze this inventory data:
{df.to_string()}

Give stockout risks, overstock issues,
and restock recommendations.
"""
            }
        ]
    )

    st.write(response.choices[0].message.content)

    # Chat with AI
    st.subheader("🗣️ Ask ReStockerAI")

    user_question = st.text_input("Tanyakan sesuatu tentang stok & restock:")

    if user_question:
        chat_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an AI inventory assistant."},
                {"role": "user", "content": f"Inventory Data:\n{df.to_string()}\n\nQuestion:\n{user_question}"}
            ]
        )
        st.write(chat_response.choices[0].message.content)
