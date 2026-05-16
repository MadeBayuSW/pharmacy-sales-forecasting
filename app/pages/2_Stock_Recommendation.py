import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Stock Recommendation",
    page_icon="📦",
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

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"

prediction_result = pd.read_csv(DATA_DIR / "prediction_result.csv")
stock_recommendation = pd.read_csv(DATA_DIR / "product_stock_recommendation.csv")

prediction_result["sales_date"] = pd.to_datetime(prediction_result["sales_date"])

st.title("📦 Stock Recommendation Dashboard")
st.write(
    """
    Halaman ini menampilkan hasil prediksi penjualan dan rekomendasi prioritas stok produk apotek.
    """
)

# =========================
# Summary Metrics
# =========================
total_products = stock_recommendation["product_id"].nunique()
total_actual = prediction_result["total_quantity_sold"].sum()
total_predicted = prediction_result["predicted_quantity_sold"].sum()
high_priority_count = stock_recommendation["stock_priority"].eq("High Priority").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Products", f"{total_products:,}")
col2.metric("Actual Sales", f"{total_actual:,.0f}")
col3.metric("Predicted Sales", f"{total_predicted:,.0f}")
col4.metric("High Priority Products", f"{high_priority_count:,}")

st.divider()

# =========================
# Sidebar Filter
# =========================
st.sidebar.header("Filter")

priority_order = ["High Priority", "Medium Priority", "Low Priority"]

priority_options = [
    p for p in priority_order
    if p in stock_recommendation["stock_priority"].unique()
]

selected_priority = st.sidebar.multiselect(
    "Select Stock Priority",
    options=priority_options,
    default=priority_options
)

product_options = stock_recommendation["product_name"].dropna().unique().tolist()

selected_product = st.sidebar.selectbox(
    "Select Product",
    options=["All Products"] + product_options
)

filtered_stock = stock_recommendation[
    stock_recommendation["stock_priority"].isin(selected_priority)
].copy()

filtered_prediction = prediction_result.copy()

if selected_product != "All Products":
    filtered_prediction = filtered_prediction[
        filtered_prediction["product_name"] == selected_product
    ]

# =========================
# Actual vs Predicted Monthly Sales
# =========================
st.subheader("📈 Actual vs Predicted Monthly Sales")

filtered_prediction["month"] = (
    filtered_prediction["sales_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    filtered_prediction
    .groupby("month")[["total_quantity_sold", "predicted_quantity_sold"]]
    .sum()
    .reset_index()
)

monthly_sales_melted = monthly_sales.melt(
    id_vars="month",
    value_vars=["total_quantity_sold", "predicted_quantity_sold"],
    var_name="Type",
    value_name="Quantity"
)

monthly_sales_melted["Type"] = monthly_sales_melted["Type"].replace({
    "total_quantity_sold": "Actual Sales",
    "predicted_quantity_sold": "Predicted Sales"
})

fig_monthly = px.line(
    monthly_sales_melted,
    x="month",
    y="Quantity",
    color="Type",
    markers=True,
    title="Actual vs Predicted Monthly Sales",
    color_discrete_map={
        "Actual Sales": "#38BDF8",
        "Predicted Sales": "#F97316"
    },
    text="Quantity"
)

fig_monthly.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="top center",
    line=dict(width=4),
    marker=dict(size=9)
)

fig_monthly.update_layout(
    template="plotly_dark",
    plot_bgcolor="#0F172A",
    paper_bgcolor="#0F172A",
    font=dict(color="#E2E8F0"),
    legend_title_text="",
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig_monthly, use_container_width=True)

# =========================
# Top High Priority Products
# =========================
st.subheader("🔥 Top 10 High Priority Products")

top_high_priority = (
    stock_recommendation[
        stock_recommendation["stock_priority"] == "High Priority"
    ]
    .sort_values("predicted_quantity", ascending=False)
    .head(10)
    .copy()
)

top_high_priority["predicted_quantity_label"] = (
    top_high_priority["predicted_quantity"].round(0)
)

fig_top = px.bar(
    top_high_priority,
    x="predicted_quantity",
    y="product_name",
    orientation="h",
    title="Top 10 Products Based on Predicted Quantity",
    labels={
        "predicted_quantity": "Predicted Quantity",
        "product_name": "Product Name"
    },
    color="product_name",
    text="predicted_quantity_label",
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig_top.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig_top.update_layout(
    template="plotly_dark",
    plot_bgcolor="#0F172A",
    paper_bgcolor="#0F172A",
    font=dict(color="#E2E8F0"),
    showlegend=False,
    yaxis={"categoryorder": "total ascending"},
    margin=dict(l=20, r=110, t=60, b=20)
)

st.plotly_chart(fig_top, use_container_width=True)

# =========================
# Stock Priority Distribution
# =========================
st.subheader("📦 Stock Priority Distribution")

priority_count = (
    stock_recommendation["stock_priority"]
    .value_counts()
    .reset_index()
)

priority_count.columns = ["stock_priority", "count"]

priority_count["stock_priority"] = pd.Categorical(
    priority_count["stock_priority"],
    categories=priority_order,
    ordered=True
)

priority_count = priority_count.sort_values("stock_priority")

fig_priority = px.bar(
    priority_count,
    x="stock_priority",
    y="count",
    title="Number of Products by Stock Priority",
    labels={
        "stock_priority": "Stock Priority",
        "count": "Number of Products"
    },
    color="stock_priority",
    text="count",
    color_discrete_map={
        "High Priority": "#EF4444",
        "Medium Priority": "#F59E0B",
        "Low Priority": "#10B981"
    }
)

fig_priority.update_traces(
    texttemplate="%{text:,}",
    textposition="outside"
)

fig_priority.update_layout(
    template="plotly_dark",
    plot_bgcolor="#0F172A",
    paper_bgcolor="#0F172A",
    font=dict(color="#E2E8F0"),
    showlegend=False,
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig_priority, use_container_width=True)

# =========================
# Recommendation Table
# =========================
st.subheader("📋 Product Stock Recommendation")

table_data = filtered_stock.sort_values(
    "predicted_quantity",
    ascending=False
).copy()

if "predicted_quantity" in table_data.columns:
    table_data["predicted_quantity"] = table_data["predicted_quantity"].round(2)

if "avg_daily_prediction" in table_data.columns:
    table_data["avg_daily_prediction"] = table_data["avg_daily_prediction"].round(2)

st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("🧠 Business Interpretation")

st.markdown(
    """
    Produk dengan kategori **High Priority** merupakan produk dengan prediksi permintaan tinggi,
    sehingga dapat diprioritaskan dalam perencanaan pengadaan stok.

    Produk dengan kategori **Medium Priority** dapat dipertahankan pada level stok normal,
    sedangkan produk **Low Priority** perlu dipantau agar tidak menyebabkan penumpukan barang.

    Karena dataset belum memiliki data stok aktual, rekomendasi ini masih berbasis
    **prediksi permintaan**, bukan perbandingan antara stok tersedia dan kebutuhan stok.
    """
)