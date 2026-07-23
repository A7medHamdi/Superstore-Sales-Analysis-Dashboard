import pandas as pd

# ==========================
# Load Dataset
# ==========================

df = pd.read_csv("Sample - Superstore.csv", encoding="latin1")


# ==========================
# Data Type Conversion
# ==========================

df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])

# Convert Postal Code to string (before removing it)
df["Postal Code"] = df["Postal Code"].astype(str)


# ==========================
# Feature Engineering
# ==========================

df["Shipping Days"] = (
    df["Ship Date"] - df["Order Date"]
).dt.days

# ==========================
# Date Features
# ==========================

df["Order Year"] = df["Order Date"].dt.year

df["Order Month"] = df["Order Date"].dt.month_name()

df["Order Month Number"] = df["Order Date"].dt.month

# ==========================
# Remove Unnecessary Columns
# ==========================

df.drop(
    columns=["Row ID", "Country", "Postal Code"],
    inplace=True
)


# ==========================
# Remove Duplicates
# ==========================

df.drop_duplicates(inplace=True)


# ==========================
# Data Understanding
# ==========================

print("=" * 50)
print("First 5 Rows")
print("=" * 50)
print(df.head())


print("\n" + "=" * 50)
print("Dataset Shape")
print("=" * 50)
print(df.shape)


print("\n" + "=" * 50)
print("Dataset Information")
print("=" * 50)
df.info()


print("\n" + "=" * 50)
print("Unique Values")
print("=" * 50)
print(df.nunique())


print("\n" + "=" * 50)
print("Numerical Statistics")
print("=" * 50)

print("\n" + "=" * 50)
print("Sales Statistics")
print("=" * 50)

print(df["Sales"].describe())


print("\n" + "=" * 50)
print("Profit Statistics")
print("=" * 50)

print(df["Profit"].describe())


print("\n" + "=" * 50)
print("Quantity Statistics")
print("=" * 50)

print(df["Quantity"].describe())


print("\n" + "=" * 50)
print("Discount Statistics")
print("=" * 50)

print(df["Discount"].describe())


print("\n" + "=" * 50)
print("Shipping Days Statistics")
print("=" * 50)

print(df["Shipping Days"].describe())


print("\n" + "=" * 50)
print("Categorical Statistics")
print("=" * 50)

print("\n" + "=" * 50)
print("Category Summary")
print("=" * 50)

print(df["Category"].value_counts())


print("\n" + "=" * 50)
print("Segment Summary")
print("=" * 50)

print(df["Segment"].value_counts())


print("\n" + "=" * 50)
print("Region Summary")
print("=" * 50)

print(df["Region"].value_counts())


print("\n" + "=" * 50)
print("Ship Mode Summary")
print("=" * 50)

print(df["Ship Mode"].value_counts())


# ==========================
# Data Quality Assessment
# ==========================

print("\n" + "=" * 50)
print("Missing Values")
print("=" * 50)
print(df.isnull().sum())


print("\n" + "=" * 50)
print("Duplicate Rows")
print("=" * 50)
print(df.duplicated().sum())



# ==========================
# Business KPIs
# ==========================

print("\n" + "=" * 50)
print("Business KPIs")
print("=" * 50)


print(f"Total Sales: {df['Sales'].sum():,.2f}")

print(f"Total Profit: {df['Profit'].sum():,.2f}")

print(f"Total Orders: {df['Order ID'].nunique()}")

print(f"Total Customers: {df['Customer ID'].nunique()}")

print(f"Orders with Discount: {(df['Discount'] > 0).sum()}")

print(f"Average Discount: {df['Discount'].mean():.2%}")



# ==========================
# Category Analysis
# ==========================

print("\n" + "=" * 50)
print("Category Sales")
print("=" * 50)

print(
    df.groupby("Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n" + "=" * 50)
print("\nCategory Profit")
print("=" * 50)

print(
    df.groupby("Category")["Profit"]
    .sum()
    .sort_values(ascending=False)
)



# ==========================
# Sub Category Analysis
# ==========================

print("\n" + "=" * 50)
print("Sub Category Sales")
print("=" * 50)

sub_sales = (
    df.groupby("Sub-Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print(sub_sales)


print("\nSub Category Profit")

sub_profit = (
    df.groupby("Sub-Category")["Profit"]
    .sum()
    .sort_values(ascending=False)
)

print(sub_profit)


print("\nWorst Sub Categories")

print(sub_profit.sort_values().head(10))



# ==========================
# Region Analysis
# ==========================

print("\n" + "=" * 50)
print("Sales By Region")
print("=" * 50)

print(
    df.groupby("Region")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n" + "=" * 50)
print("\nProfit By Region")
print("=" * 50)

print(
    df.groupby("Region")["Profit"]
    .sum()
    .sort_values(ascending=False)
)


print("\n" + "=" * 50)
print("State Analysis")
print("=" * 50)

state_sales = (
    df.groupby("State")["Sales"]
    .sum()
    .sort_values(ascending=False)
)


state_profit = (
    df.groupby("State")["Profit"]
    .sum()
    .sort_values(ascending=False)
)


print("\nTop States By Sales")
print(state_sales.head(10))


print("\nTop States By Profit")
print(state_profit.head(10))


print("\nWorst States By Profit")
print(state_profit.sort_values().head(10))



# ==========================
# Segment Analysis
# ==========================

print("\n" + "=" * 50)
print("Sales By Segment")
print("=" * 50)

print(
    df.groupby("Segment")["Sales"]
    .sum()
    .sort_values(ascending=False)
)


print("\nProfit By Segment")

print(
    df.groupby("Segment")["Profit"]
    .sum()
    .sort_values(ascending=False)
)



# ==========================
# Shipping Analysis
# ==========================

print("\n" + "=" * 50)
print("Average Shipping Days")
print("=" * 50)

print(df["Shipping Days"].mean())


print("\nShipping Mode Usage")

print(df["Ship Mode"].value_counts())



# ==========================
# Discount Analysis
# ==========================

print("\n" + "=" * 50)
print("Discount vs Profit Correlation")
print("=" * 50)

print(
    df["Discount"]
    .corr(df["Profit"])
)


print("\nAverage Profit By Discount")

print(
    df.groupby("Discount")["Profit"]
    .mean()
)

# ==========================
# Save Clean Dataset
# ==========================

df.to_csv("Superstore_Cleaned.csv", index=False)

print("Clean dataset saved successfully!")