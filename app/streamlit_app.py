import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Pharmacy Sales Dashboard",
    page_icon="💊",
    layout="wide"
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    div[data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 800;
    }

    div[data-testid="stMetricLabel"] {
        color: #CBD5E1;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"

sales_daily = pd.read_csv(DATA_DIR / "sales_daily.csv")
prediction_result = pd.read_csv(DATA_DIR / "prediction_result.csv")
stock_recommendation = pd.read_csv(DATA_DIR / "product_stock_recommendation.csv")

sales_daily["sales_date"] = pd.to_datetime(sales_daily["sales_date"])
prediction_result["sales_date"] = pd.to_datetime(prediction_result["sales_date"])

st.title("💊 Pharmacy Sales Forecasting")
st.write(
    """
    Dashboard ini merangkum performa penjualan apotek, hasil prediksi model,
    dan gambaran umum prioritas stok produk.
    """
)

# =========================
# Overall Metrics
# =========================
total_products = sales_daily["product_id"].nunique()
total_quantity = sales_daily["total_quantity_sold"].sum()
total_revenue = sales_daily["total_revenue"].sum()
total_transactions = sales_daily["total_transactions"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Products", f"{total_products:,}")
col2.metric("Total Quantity Sold", f"{total_quantity:,.0f}")
col3.metric("Total Revenue", f"{total_revenue:,.0f}")
col4.metric("Total Transactions", f"{total_transactions:,.0f}")

st.divider()

# =========================
# Monthly Sales Trend
# =========================
st.subheader("📈 Monthly Sales Trend")

sales_daily["month"] = sales_daily["sales_date"].dt.to_period("M").astype(str)

monthly_sales = (
    sales_daily
    .groupby("month")
    .agg(
        total_quantity_sold=("total_quantity_sold", "sum"),
        total_revenue=("total_revenue", "sum")
    )
    .reset_index()
)

fig_monthly_qty = px.line(
    monthly_sales,
    x="month",
    y="total_quantity_sold",
    markers=True,
    text="total_quantity_sold",
    title="Monthly Quantity Sold",
    color_discrete_sequence=["#38BDF8"]
)

fig_monthly_qty.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="top center",
    line=dict(width=4),
    marker=dict(size=9)
)

fig_monthly_qty.update_layout(
    template="plotly_dark",
    plot_bgcolor="#0F172A",
    paper_bgcolor="#0F172A",
    font=dict(color="#E2E8F0"),
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig_monthly_qty, use_container_width=True)

# =========================
# Top Products and Revenue
# =========================
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("🔥 Top 10 Best-Selling Products")

    top_products = (
        sales_daily
        .groupby(["product_id", "product_name"])["total_quantity_sold"]
        .sum()
        .reset_index()
        .sort_values("total_quantity_sold", ascending=False)
        .head(10)
    )

    fig_top_products = px.bar(
        top_products,
        x="total_quantity_sold",
        y="product_name",
        orientation="h",
        color="product_name",
        text="total_quantity_sold",
        title="Top 10 Products by Quantity Sold",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig_top_products.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_top_products.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=20, r=90, t=60, b=20)
    )

    st.plotly_chart(fig_top_products, use_container_width=True)

with right_col:
    st.subheader("💰 Top 10 Products by Revenue")

    top_revenue = (
        sales_daily
        .groupby(["product_id", "product_name"])["total_revenue"]
        .sum()
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(10)
    )

    fig_top_revenue = px.bar(
        top_revenue,
        x="total_revenue",
        y="product_name",
        orientation="h",
        color="product_name",
        text="total_revenue",
        title="Top 10 Products by Revenue",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig_top_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_top_revenue.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=20, r=90, t=60, b=20)
    )

    st.plotly_chart(fig_top_revenue, use_container_width=True)

# =========================
# Actual vs Predicted Summary
# =========================
st.subheader("🤖 Actual vs Predicted Sales")

prediction_result["month"] = prediction_result["sales_date"].dt.to_period("M").astype(str)

monthly_prediction = (
    prediction_result
    .groupby("month")[["total_quantity_sold", "predicted_quantity_sold"]]
    .sum()
    .reset_index()
)

monthly_prediction_melted = monthly_prediction.melt(
    id_vars="month",
    value_vars=["total_quantity_sold", "predicted_quantity_sold"],
    var_name="Type",
    value_name="Quantity"
)

monthly_prediction_melted["Type"] = monthly_prediction_melted["Type"].replace({
    "total_quantity_sold": "Actual Sales",
    "predicted_quantity_sold": "Predicted Sales"
})

fig_prediction = px.line(
    monthly_prediction_melted,
    x="month",
    y="Quantity",
    color="Type",
    markers=True,
    text="Quantity",
    title="Actual vs Predicted Monthly Sales",
    color_discrete_map={
        "Actual Sales": "#22C55E",
        "Predicted Sales": "#F97316"
    }
)

fig_prediction.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="top center",
    line=dict(width=4),
    marker=dict(size=9)
)

fig_prediction.update_layout(
    template="plotly_dark",
    plot_bgcolor="#0F172A",
    paper_bgcolor="#0F172A",
    font=dict(color="#E2E8F0"),
    legend_title_text="",
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig_prediction, use_container_width=True)

st.divider()

st.subheader("📌 Project Summary")
st.write(
    """
    Project ini menggunakan data transaksi SQL apotek yang diolah menjadi data penjualan harian.
    Model terbaik pada tahap awal adalah Random Forest Regressor, yang digunakan untuk memprediksi
    jumlah penjualan produk dan menyusun prioritas stok.
    """
)