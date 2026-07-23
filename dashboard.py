# =====================================================================================
# 1. IMPORTS
# =====================================================================================
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =====================================================================================
# 2. PAGE CONFIGURATION
# =====================================================================================
st.set_page_config(
    page_title="Superstore BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================================
# 3. GLOBAL STYLE / THEME (CSS)
# =====================================================================================
PRIMARY_COLOR = "#2E5EAA"
ACCENT_COLOR = "#17A398"
NEGATIVE_COLOR = "#E63946"
POSITIVE_COLOR = "#2A9D8F"
BG_CARD = "#FFFFFF"
TEXT_MUTED = "#6C757D"

# Consistent categorical / sequential palettes used across all charts
PALETTE = ["#2E5EAA", "#17A398", "#F4A261", "#E63946", "#8D99AE",
           "#5C6BC0", "#43AA8B", "#F9844A", "#277DA1", "#90BE6D"]
PLOTLY_TEMPLATE = "plotly_white"

st.markdown(f"""
<style>
    .main {{ background-color: #F5F7FA; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}

    /* KPI Card */
    .kpi-card {{
        background: {BG_CARD};
        border-radius: 14px;
        padding: 18px 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #EDEFF3;
        text-align: left;
        height: 118px;
    }}
    .kpi-title {{
        font-size: 13px;
        color: {TEXT_MUTED};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 750;
        color: #1B1F27;
        margin-bottom: 2px;
    }}
    .kpi-sub {{
        font-size: 12px;
        color: {TEXT_MUTED};
    }}
    .kpi-icon {{
        font-size: 20px;
        float: right;
        opacity: 0.75;
    }}

    /* Section headers */
    .section-title {{
        font-size: 20px;
        font-weight: 700;
        color: #1B1F27;
        margin-top: 6px;
        margin-bottom: 6px;
        border-left: 5px solid {PRIMARY_COLOR};
        padding-left: 10px;
    }}

    .insight-card {{
        background: {BG_CARD};
        border-left: 5px solid {ACCENT_COLOR};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        font-size: 15px;
        color: #1B1F27;
    }}
    .rec-card {{
        background: {BG_CARD};
        border-left: 5px solid {PRIMARY_COLOR};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        font-size: 15px;
        color: #1B1F27;
    }}

    header[data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    div[data-testid="stMetricValue"] {{ font-size: 22px; }}

    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: #C6CBD4; border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)


# =====================================================================================
# 4. DATA LOADING (CACHED) -- NO CLEANING / NO MODIFICATION OF SOURCE DATA
# =====================================================================================
@st.cache_data
def load_data(path: str = "Superstore_Cleaned.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    # Parse dates for time-series charts only (does not alter underlying values)
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")
    df["Order Month Period"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    return df


df_raw = load_data()

# =====================================================================================
# 5. SIDEBAR FILTERS
# =====================================================================================
st.sidebar.markdown("## 🧭 Filters")
st.sidebar.markdown("Use the controls below to slice the dashboard.")


def multiselect_all(label, options, key):
    options_sorted = sorted(options)
    selected = st.sidebar.multiselect(label, options_sorted, default=options_sorted, key=key)
    return selected if selected else options_sorted


years_sel = multiselect_all("Year", df_raw["Order Year"].unique().tolist(), "f_year")
region_sel = multiselect_all("Region", df_raw["Region"].unique().tolist(), "f_region")
segment_sel = multiselect_all("Segment", df_raw["Segment"].unique().tolist(), "f_segment")
category_sel = multiselect_all("Category", df_raw["Category"].unique().tolist(), "f_category")
subcat_sel = multiselect_all("Sub-Category", df_raw["Sub-Category"].unique().tolist(), "f_subcat")
shipmode_sel = multiselect_all("Ship Mode", df_raw["Ship Mode"].unique().tolist(), "f_shipmode")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Filters"):
    st.rerun()

# Apply filters
df = df_raw[
    df_raw["Order Year"].isin(years_sel)
    & df_raw["Region"].isin(region_sel)
    & df_raw["Segment"].isin(segment_sel)
    & df_raw["Category"].isin(category_sel)
    & df_raw["Sub-Category"].isin(subcat_sel)
    & df_raw["Ship Mode"].isin(shipmode_sel)
].copy()

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(df):,}** of **{len(df_raw):,}** records")

# =====================================================================================
# 6. HEADER
# =====================================================================================
st.markdown("# 📊 Superstore Business Intelligence Dashboard")
st.markdown(
    f"<span style='color:{TEXT_MUTED};'>End-to-end sales, profit, customer & shipping "
    f"performance overview • Data refreshed as of {datetime.now().strftime('%B %d, %Y')}</span>",
    unsafe_allow_html=True,
)
st.markdown("")

# =====================================================================================
# 7. KPI CALCULATIONS
# =====================================================================================
if len(df) == 0:
    st.warning("No data matches the current filter selection. Please adjust your filters.")
    st.stop()

total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0
total_orders = df["Order ID"].nunique()
total_customers = df["Customer ID"].nunique()
avg_shipping_days = df["Shipping Days"].mean()
avg_discount = df["Discount"].mean() * 100


def kpi_card(col, icon, title, value, sub=""):
    col.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
kpi_card(k1, "💰", "Total Sales", f"${total_sales:,.0f}")
kpi_card(k2, "📈", "Total Profit", f"${total_profit:,.0f}")
kpi_card(k3, "📐", "Profit Margin", f"{profit_margin:.1f}%")
kpi_card(k4, "🧾", "Total Orders", f"{total_orders:,}")
kpi_card(k5, "👥", "Total Customers", f"{total_customers:,}")
kpi_card(k6, "🚚", "Avg Shipping Days", f"{avg_shipping_days:.1f}")
kpi_card(k7, "🏷️", "Avg Discount", f"{avg_discount:.1f}%")

st.markdown("")

# =====================================================================================
# 8. TABS
# =====================================================================================
tab_overview, tab_sales, tab_profit, tab_customers, tab_shipping, tab_insights = st.tabs(
    ["🏠 Overview", "💵 Sales", "📈 Profit", "👥 Customers", "🚚 Shipping", "💡 Insights"]
)

# -------------------------------------------------------------------------------------
# Reusable helper: apply consistent styling to a plotly figure
# -------------------------------------------------------------------------------------
def style_fig(fig, title=None, height=380):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=title,
        title_font_size=17,
        height=height,
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Segoe UI, Arial", size=12, color="#1B1F27"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# =====================================================================================
# TAB 1: OVERVIEW
# =====================================================================================
with tab_overview:
    st.markdown('<div class="section-title">Monthly Trends</div>', unsafe_allow_html=True)
    monthly = df.groupby("Order Month Period", as_index=False).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum")
    ).sort_values("Order Month Period")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.area(monthly, x="Order Month Period", y="Sales",
                       color_discrete_sequence=[PRIMARY_COLOR])
        fig.update_traces(line_width=2.5)
        st.plotly_chart(style_fig(fig, "Monthly Sales Trend"), use_container_width=True)
    with c2:
        fig = px.area(monthly, x="Order Month Period", y="Profit",
                       color_discrete_sequence=[ACCENT_COLOR])
        fig.update_traces(line_width=2.5)
        st.plotly_chart(style_fig(fig, "Monthly Profit Trend"), use_container_width=True)

    st.markdown('<div class="section-title">Category & Region Performance</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        cat_sales = df.groupby("Category", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        fig = px.bar(cat_sales, x="Category", y="Sales", color="Category",
                     color_discrete_sequence=PALETTE, text_auto=".2s")
        st.plotly_chart(style_fig(fig, "Sales by Category"), use_container_width=True)
    with c4:
        cat_profit = df.groupby("Category", as_index=False)["Profit"].sum().sort_values("Profit", ascending=False)
        fig = px.bar(cat_profit, x="Category", y="Profit", color="Category",
                     color_discrete_sequence=PALETTE, text_auto=".2s")
        st.plotly_chart(style_fig(fig, "Profit by Category"), use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        reg_sales = df.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        fig = px.pie(reg_sales, names="Region", values="Sales", hole=0.5,
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(style_fig(fig, "Sales by Region"), use_container_width=True)
    with c6:
        reg_profit = df.groupby("Region", as_index=False)["Profit"].sum().sort_values("Profit", ascending=False)
        fig = px.pie(reg_profit, names="Region", values="Profit", hole=0.5,
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(style_fig(fig, "Profit by Region"), use_container_width=True)

    st.markdown('<div class="section-title">Correlation Heatmap</div>', unsafe_allow_html=True)
    num_cols = ["Sales", "Quantity", "Discount", "Profit", "Shipping Days"]
    corr = df[num_cols].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                     aspect="auto")
    st.plotly_chart(style_fig(fig, "Correlation Between Numeric Metrics", height=420), use_container_width=True)

    st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)
    top_cat = cat_sales.iloc[0]["Category"]
    top_region = reg_sales.iloc[0]["Region"]
    best_margin_cat = df.groupby("Category")["Profit"].sum().div(df.groupby("Category")["Sales"].sum()).idxmax()
    st.markdown(f"""
    <div class="insight-card">
    Across <b>{total_orders:,}</b> orders from <b>{total_customers:,}</b> customers, the business generated
    <b>${total_sales:,.0f}</b> in sales and <b>${total_profit:,.0f}</b> in profit
    (<b>{profit_margin:.1f}%</b> margin). <b>{top_cat}</b> is the leading category by sales, the
    <b>{top_region}</b> region contributes the most revenue, and <b>{best_margin_cat}</b> delivers the
    strongest profit margin. Average order ships in <b>{avg_shipping_days:.1f} days</b> with an average
    discount of <b>{avg_discount:.1f}%</b>.
    </div>
    """, unsafe_allow_html=True)


# =====================================================================================
# TAB 2: SALES
# =====================================================================================
with tab_sales:
    st.markdown('<div class="section-title">State Performance</div>', unsafe_allow_html=True)
    state_sales = df.groupby("State", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        top10 = state_sales.head(10).sort_values("Sales")
        fig = px.bar(top10, x="Sales", y="State", orientation="h",
                     color="Sales", color_continuous_scale="Blues", text_auto=".2s")
        st.plotly_chart(style_fig(fig, "Top 10 States by Sales"), use_container_width=True)
    with c2:
        bottom10 = state_sales.tail(10).sort_values("Sales")
        fig = px.bar(bottom10, x="Sales", y="State", orientation="h",
                     color="Sales", color_continuous_scale="Reds", text_auto=".2s")
        st.plotly_chart(style_fig(fig, "Bottom 10 States by Sales"), use_container_width=True)

    st.markdown('<div class="section-title">Products & Sub-Categories</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        top_products = df.groupby("Product Name", as_index=False)["Sales"].sum().sort_values(
            "Sales", ascending=False).head(10).sort_values("Sales")
        fig = px.bar(top_products, x="Sales", y="Product Name", orientation="h",
                     color_discrete_sequence=[PRIMARY_COLOR], text_auto=".2s")
        fig.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(style_fig(fig, "Top 10 Products by Sales", height=430), use_container_width=True)
    with c4:
        top_subcat = df.groupby("Sub-Category", as_index=False)["Sales"].sum().sort_values(
            "Sales", ascending=False).head(10).sort_values("Sales")
        fig = px.bar(top_subcat, x="Sales", y="Sub-Category", orientation="h",
                     color_discrete_sequence=[ACCENT_COLOR], text_auto=".2s")
        st.plotly_chart(style_fig(fig, "Top Sub-Categories by Sales", height=430), use_container_width=True)

    st.markdown('<div class="section-title">Sales Distribution & Composition</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        fig = px.histogram(df, x="Sales", nbins=50, color_discrete_sequence=[PRIMARY_COLOR])
        st.plotly_chart(style_fig(fig, "Sales Distribution"), use_container_width=True)
    with c6:
        seg_sales = df.groupby("Segment", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        fig = px.bar(seg_sales, x="Segment", y="Sales", color="Segment",
                     color_discrete_sequence=PALETTE, text_auto=".2s")
        st.plotly_chart(style_fig(fig, "Sales by Segment"), use_container_width=True)

    st.markdown('<div class="section-title">Treemap: Category → Sub-Category → Sales</div>', unsafe_allow_html=True)
    tree_data = df.groupby(["Category", "Sub-Category"], as_index=False)["Sales"].sum()
    fig = px.treemap(tree_data, path=["Category", "Sub-Category"], values="Sales",
                      color="Sales", color_continuous_scale="Blues")
    st.plotly_chart(style_fig(fig, "Sales Treemap", height=480), use_container_width=True)


# =====================================================================================
# TAB 3: PROFIT
# =====================================================================================
with tab_profit:
    st.markdown('<div class="section-title">Profit by State & Category</div>', unsafe_allow_html=True)
    state_profit = df.groupby("State", as_index=False)["Profit"].sum().sort_values("Profit", ascending=False)

    # Map full state names to USPS abbreviations for choropleth rendering
    STATE_ABBR = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
        "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
        "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
        "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
        "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
        "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
        "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    }
    state_profit_map = state_profit.copy()
    state_profit_map["State Code"] = state_profit_map["State"].map(STATE_ABBR)

    c1, c2 = st.columns(2)
    with c1:
        map_df = state_profit_map.dropna(subset=["State Code"])
        if len(map_df) > 0:
            fig = px.choropleth(
                map_df, locations="State Code", locationmode="USA-states", color="Profit",
                scope="usa", color_continuous_scale="RdYlGn", hover_name="State"
            )
            st.plotly_chart(style_fig(fig, "Profit by State (Map)", height=420), use_container_width=True)
        else:
            st.info("No mappable state data available for the current filter selection.")
    with c2:
        cat_profit2 = df.groupby("Category", as_index=False)["Profit"].sum().sort_values("Profit", ascending=False)
        fig = px.bar(cat_profit2, x="Category", y="Profit", color="Category",
                     color_discrete_sequence=PALETTE, text_auto=".2s")
        st.plotly_chart(style_fig(fig, "Profit by Category", height=420), use_container_width=True)

    st.markdown('<div class="section-title">Margins & Discount Impact</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        margin_cat = df.groupby("Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        margin_cat["Profit Margin (%)"] = margin_cat["Profit"] / margin_cat["Sales"] * 100
        fig = px.bar(margin_cat.sort_values("Profit Margin (%)", ascending=False),
                     x="Category", y="Profit Margin (%)", color="Category",
                     color_discrete_sequence=PALETTE, text_auto=".1f")
        st.plotly_chart(style_fig(fig, "Profit Margin by Category"), use_container_width=True)
    with c4:
        fig = px.scatter(df, x="Discount", y="Profit", color="Category",
                          color_discrete_sequence=PALETTE, opacity=0.6,
                          trendline="ols", trendline_scope="overall")
        st.plotly_chart(style_fig(fig, "Discount vs Profit"), use_container_width=True)

    st.markdown('<div class="section-title">Profit Spread & Worst Performers</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        fig = px.box(df, x="Category", y="Profit", color="Category", color_discrete_sequence=PALETTE)
        st.plotly_chart(style_fig(fig, "Profit Distribution by Category (Box Plot)"), use_container_width=True)
    with c6:
        worst_products = df.groupby("Product Name", as_index=False)["Profit"].sum().sort_values(
            "Profit").head(10)
        fig = px.bar(worst_products, x="Profit", y="Product Name", orientation="h",
                     color="Profit", color_continuous_scale="Reds", text_auto=".2s")
        fig.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(style_fig(fig, "10 Worst Products by Profit"), use_container_width=True)

    worst_states = state_profit.tail(10).sort_values("Profit")
    fig = px.bar(worst_states, x="Profit", y="State", orientation="h",
                 color="Profit", color_continuous_scale="Reds", text_auto=".2s")
    st.plotly_chart(style_fig(fig, "10 Worst States by Profit"), use_container_width=True)


# =====================================================================================
# TAB 4: CUSTOMERS
# =====================================================================================
with tab_customers:
    st.markdown('<div class="section-title">Top Customers</div>', unsafe_allow_html=True)
    top_customers = df.groupby("Customer Name", as_index=False)["Sales"].sum().sort_values(
        "Sales", ascending=False).head(10).sort_values("Sales")
    fig = px.bar(top_customers, x="Sales", y="Customer Name", orientation="h",
                 color_discrete_sequence=[PRIMARY_COLOR], text_auto=".2s")
    st.plotly_chart(style_fig(fig, "Top 10 Customers by Sales", height=420), use_container_width=True)

    st.markdown('<div class="section-title">Segment & Order Behavior</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        seg_customers = df.groupby("Segment")["Customer ID"].nunique().reset_index(name="Customers")
        fig = px.pie(seg_customers, names="Segment", values="Customers", hole=0.5,
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(style_fig(fig, "Customer Segments (Unique Customers)"), use_container_width=True)
    with c2:
        orders_per_cust = df.groupby("Customer ID")["Order ID"].nunique().reset_index(name="Orders")
        fig = px.histogram(orders_per_cust, x="Orders", nbins=20, color_discrete_sequence=[ACCENT_COLOR])
        st.plotly_chart(style_fig(fig, "Orders per Customer (Distribution)"), use_container_width=True)

    st.markdown('<div class="section-title">Customer Geographic Distribution</div>', unsafe_allow_html=True)
    cust_state = df.groupby("State")["Customer ID"].nunique().reset_index(name="Customers").sort_values(
        "Customers", ascending=False)
    fig = px.bar(cust_state.head(15), x="State", y="Customers", color="Customers",
                 color_continuous_scale="Teal", text_auto=True)
    st.plotly_chart(style_fig(fig, "Top 15 States by Customer Count", height=420), use_container_width=True)


# =====================================================================================
# TAB 5: SHIPPING
# =====================================================================================
with tab_shipping:
    st.markdown('<div class="section-title">Shipping Mode Overview</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        ship_usage = df["Ship Mode"].value_counts().reset_index()
        ship_usage.columns = ["Ship Mode", "Orders"]
        fig = px.pie(ship_usage, names="Ship Mode", values="Orders", hole=0.5,
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(style_fig(fig, "Shipping Mode Usage"), use_container_width=True)
    with c2:
        avg_ship_mode = df.groupby("Ship Mode", as_index=False)["Shipping Days"].mean().sort_values(
            "Shipping Days", ascending=False)
        fig = px.bar(avg_ship_mode, x="Ship Mode", y="Shipping Days", color="Ship Mode",
                     color_discrete_sequence=PALETTE, text_auto=".1f")
        st.plotly_chart(style_fig(fig, "Average Shipping Days by Mode"), use_container_width=True)

    st.markdown('<div class="section-title">Shipping Time Distribution & Regional Performance</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        fig = px.histogram(df, x="Shipping Days", nbins=15, color_discrete_sequence=[PRIMARY_COLOR])
        st.plotly_chart(style_fig(fig, "Shipping Days Distribution"), use_container_width=True)
    with c4:
        region_ship = df.groupby("Region", as_index=False)["Shipping Days"].mean().sort_values(
            "Shipping Days", ascending=False)
        fig = px.bar(region_ship, x="Region", y="Shipping Days", color="Region",
                     color_discrete_sequence=PALETTE, text_auto=".2f")
        st.plotly_chart(style_fig(fig, "Average Shipping Days by Region"), use_container_width=True)


# =====================================================================================
# TAB 6: INSIGHTS & RECOMMENDATIONS (DYNAMICALLY CALCULATED)
# =====================================================================================
with tab_insights:
    st.markdown('<div class="section-title">💡 Automated Insights</div>', unsafe_allow_html=True)

    # ---- Dynamic calculations (no hardcoded values) ----
    cat_sales_all = df.groupby("Category")["Sales"].sum()
    highest_sales_category = cat_sales_all.idxmax()

    state_profit_all = df.groupby("State")["Profit"].sum()
    highest_profit_state = state_profit_all.idxmax()
    lowest_profit_state = state_profit_all.idxmin()

    region_profit_all = df.groupby("Region")["Profit"].sum()
    best_region = region_profit_all.idxmax()
    worst_region = region_profit_all.idxmin()

    subcat_profit_all = df.groupby("Sub-Category")["Profit"].sum()
    best_subcat = subcat_profit_all.idxmax()
    worst_subcat = subcat_profit_all.idxmin()

    # Discount impact: correlation + comparison of avg profit margin above/below median discount
    discount_profit_corr = df["Discount"].corr(df["Profit"])
    median_discount = df["Discount"].median()
    high_disc_margin = df[df["Discount"] > median_discount]["Profit"].sum() / \
        max(df[df["Discount"] > median_discount]["Sales"].sum(), 1e-9) * 100
    low_disc_margin = df[df["Discount"] <= median_discount]["Profit"].sum() / \
        max(df[df["Discount"] <= median_discount]["Sales"].sum(), 1e-9) * 100

    fastest_ship_mode = df.groupby("Ship Mode")["Shipping Days"].mean().idxmin()
    slowest_ship_mode = df.groupby("Ship Mode")["Shipping Days"].mean().idxmax()

    top_segment = df.groupby("Segment")["Profit"].sum().idxmax()

    insights = [
        f"📦 <b>{highest_sales_category}</b> is the highest-selling category, generating "
        f"${cat_sales_all.max():,.0f} in total sales.",

        f"🏆 <b>{highest_profit_state}</b> is the most profitable state with "
        f"${state_profit_all.max():,.0f} in profit, while <b>{lowest_profit_state}</b> is the "
        f"least profitable at ${state_profit_all.min():,.0f}.",

        f"🌍 The <b>{best_region}</b> region leads in profitability (${region_profit_all.max():,.0f}), "
        f"whereas the <b>{worst_region}</b> region lags behind (${region_profit_all.min():,.0f}).",

        f"🧩 <b>{best_subcat}</b> is the top-performing sub-category by profit "
        f"(${subcat_profit_all.max():,.0f}), while <b>{worst_subcat}</b> is the weakest "
        f"(${subcat_profit_all.min():,.0f}).",

        f"🚚 Orders ship in <b>{avg_shipping_days:.1f} days</b> on average. "
        f"<b>{fastest_ship_mode}</b> is the fastest shipping mode, while "
        f"<b>{slowest_ship_mode}</b> is the slowest.",

        f"💳 Discount and profit show a correlation of <b>{discount_profit_corr:.2f}</b>. "
        f"Orders with above-median discounts (> {median_discount:.0%}) run a "
        f"<b>{high_disc_margin:.1f}%</b> profit margin, versus <b>{low_disc_margin:.1f}%</b> "
        f"for lower-discount orders.",

        f"👑 The <b>{top_segment}</b> segment contributes the most profit overall.",
    ]

    for ins in insights:
        st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">📌 Business Recommendations</div>', unsafe_allow_html=True)

    recommendations = []

    if high_disc_margin < low_disc_margin:
        recommendations.append(
            f"Reduce discounting above {median_discount:.0%} — orders in this range run a "
            f"{low_disc_margin - high_disc_margin:.1f} point lower profit margin than lower-discount orders."
        )
    else:
        recommendations.append(
            "Current discount levels are not eroding margin significantly; monitor periodically "
            "to ensure discounts remain profit-neutral."
        )

    recommendations.append(
        f"Investigate root causes of underperformance in <b>{lowest_profit_state}</b> and the "
        f"<b>{worst_region}</b> region — consider pricing, logistics, or assortment adjustments."
    )
    recommendations.append(
        f"Increase inventory investment and marketing spend behind <b>{highest_sales_category}</b> "
        f"and <b>{best_subcat}</b>, the strongest sales/profit drivers."
    )
    recommendations.append(
        f"Reevaluate the <b>{slowest_ship_mode}</b> shipping method — it has the longest average "
        f"delivery time and may be hurting customer satisfaction relative to "
        f"<b>{fastest_ship_mode}</b>."
    )
    recommendations.append(
        f"Prioritize retention and upsell campaigns for the <b>{top_segment}</b> segment, "
        f"currently the largest source of profit."
    )
    if subcat_profit_all.min() < 0:
        recommendations.append(
            f"Reassess pricing or discontinue low-margin items in <b>{worst_subcat}</b>, "
            f"which is currently operating at a net loss of ${abs(subcat_profit_all.min()):,.0f}."
        )

    for rec in recommendations:
        st.markdown(f'<div class="rec-card">✅ {rec}</div>', unsafe_allow_html=True)

# =====================================================================================
# 9. FOOTER
# =====================================================================================
st.markdown("---")
st.markdown(
    f"<span style='color:{TEXT_MUTED}; font-size:12px;'>Superstore BI Dashboard • Built with "
    f"Streamlit & Plotly • Data source: Superstore_Cleaned.csv</span>",
    unsafe_allow_html=True,
)
