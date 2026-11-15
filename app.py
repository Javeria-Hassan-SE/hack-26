import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def create_sales_data():
    rng = np.random.default_rng(42)
    row_count = 600
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    categories = ["Electronics", "Home", "Clothing", "Beauty"]
    regions = ["North", "South", "East", "West"]
    category_prices = {
        "Electronics": (180, 900),
        "Home": (35, 300),
        "Clothing": (20, 180),
        "Beauty": (10, 100),
    }

    sales = pd.DataFrame(
        {
            "Date": rng.choice(dates, row_count),
            "Category": rng.choice(categories, row_count),
            "Region": rng.choice(regions, row_count),
            "Units": rng.integers(1, 6, row_count),
        }
    )
    sales["Unit Price"] = sales["Category"].map(
        lambda category: rng.uniform(*category_prices[category])
    )
    sales["Revenue"] = (sales["Units"] * sales["Unit Price"]).round(2)
    return sales.sort_values("Date")


sales = create_sales_data()

st.title("Sales Dashboard")
st.caption("A simple overview of synthetic sales data for 2025.")

with st.sidebar:
    st.header("Filters")
    selected_regions = st.multiselect(
        "Region", sorted(sales["Region"].unique()), default=sorted(sales["Region"].unique())
    )
    selected_categories = st.multiselect(
        "Category",
        sorted(sales["Category"].unique()),
        default=sorted(sales["Category"].unique()),
    )

filtered_sales = sales[
    sales["Region"].isin(selected_regions)
    & sales["Category"].isin(selected_categories)
]

if filtered_sales.empty:
    st.info("Select at least one region and category to view sales.")
else:
    revenue = filtered_sales["Revenue"].sum()
    order_count = len(filtered_sales)
    average_order = revenue / order_count

    metric_columns = st.columns(3)
    metric_columns[0].metric("Total revenue", f"${revenue:,.0f}")
    metric_columns[1].metric("Orders", f"{order_count:,}")
    metric_columns[2].metric("Average order value", f"${average_order:,.2f}")

    monthly_revenue = (
        filtered_sales.assign(Month=filtered_sales["Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month", as_index=False)["Revenue"]
        .sum()
        .set_index("Month")
    )
    category_revenue = (
        filtered_sales.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
    )

    chart_columns = st.columns(2)
    with chart_columns[0]:
        st.subheader("Monthly revenue")
        st.line_chart(monthly_revenue)
    with chart_columns[1]:
        st.subheader("Revenue by category")
        st.bar_chart(category_revenue)

    with st.expander("View sales data"):
        st.dataframe(
            filtered_sales.sort_values("Date", ascending=False),
            width="stretch",
            hide_index=True,
        )
