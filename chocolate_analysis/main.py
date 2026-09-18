import pandas as pd

df = pd.read_csv("data_sets/Chocolate_Sales.CSV")

# Limpieza de datos, quitamos los signos de dolares y espacios en blanco
df["Amount"] = df["Amount"].astype(str).str.replace("$", "", regex=False).str.strip()
df["Price_per_Box"] = (
    df["Price_per_Box"].astype(str).str.replace("$", "", regex=False).str.strip()
)

# Conversion de la columna Amount a numeric
# Nota: errors=coerce transforma cualquier texto corrupto a un valor vacio (NaN)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df["Price_per_Box"] = pd.to_numeric(df["Price_per_Box"], errors="coerce")

# KPIs Globales
total_sales = df["Amount"].sum()
unique_orders = df["Order_ID"].nunique()
total_boxes_shipped = df["Boxes_Shipped"].sum()

# Ventas por producto
sales_by_product = df.groupby("Product").agg(sales=("Amount", "sum"))

# Ventas por pais y canal
sales_by_country_channel = df.groupby(["Country", "Channel"])["Amount"].sum().unstack()
# Nota: unstack, forma una tabla Channel/Country (convierte uno de los niveles del indice en columnas)

# Promedio de ticket
median = df["Amount"].median()
mean = df["Amount"].mean()

# Promedio por caja Listado VS Ponderado
valid_mask = (df["Boxes_Shipped"] > 0) & (df["Amount"] > 0)
df_valid = df[valid_mask]
df_valid = df_valid.copy()

df_valid["effective_price"] = df_valid["Amount"] / df_valid["Boxes_Shipped"]

price_by_product = df_valid.groupby("Product").agg(
    listed_price=("Price_per_Box", "mean"),
    avg_effective=("effective_price", "mean"),
    total_amount=("Amount", "sum"),
    total_boxes=("Boxes_Shipped", "sum"),
)

price_by_product["weighted_price"] = (
    price_by_product["total_amount"] / price_by_product["total_boxes"]
)

price_by_product["discount_gap_pct"] = (
    (price_by_product["listed_price"] - price_by_product["weighted_price"])
    / price_by_product["listed_price"]
) * 100

price_by_product = price_by_product.round(2)

print("Precio promedio por cada y producto")
print(price_by_product)
