from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Análisis de ventas de chocolate",
    layout="wide",
)

st.title("Análisis de ventas de chocolate")
st.caption(
    "Resumen de ventas de chocolate: totales globales, productos más fuertes, "
    "canales de venta y precios reales por caja."
)


@st.cache_data(ttl="1h")
def load_data() -> dict[str, pd.DataFrame | float | int]:
    csv_path = Path(__file__).parent.parent / "data_sets" / "Chocolate_Sales.CSV"
    df = pd.read_csv(csv_path)

    for col in ("Amount", "Price_per_Box"):
        # Limpieza de datos, quitamos los signos de dolares y espacios en blanco
        df[col] = df[col].astype(str).str.replace("$", "", regex=False).str.strip()

        # Conversion de las columnas a numeric
        # Nota: errors=coerce transforma cualquier texto corrupto a un valor vacio (NaN)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # KPIs Globales
    total_sales = df["Amount"].sum()
    unique_orders = df["Order_ID"].nunique()
    total_boxes_shipped = df["Boxes_Shipped"].sum()

    # Ventas por producto
    sales_by_product = df.groupby("Product", as_index=False).agg(
        sales=("Amount", "sum")
    )

    # Ventas por pais y canal
    # Nota: unstack, forma una tabla Channel/Country (convierte uno de los niveles del indice en columnas)
    sales_by_country_channel = (
        df.groupby(["Country", "Channel"])["Amount"].sum().unstack()
    )

    # Promedio de ticket
    median = df["Amount"].median()
    mean = df["Amount"].mean()

    # Promedio por caja Listado VS Ponderado
    valid_mask = (df["Boxes_Shipped"] > 0) & (df["Amount"] > 0)
    df_valid = df[valid_mask].copy()
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

    return {
        "total_sales": total_sales,
        "unique_orders": unique_orders,
        "total_boxes_shipped": total_boxes_shipped,
        "sales_by_product": sales_by_product,
        "sales_by_country_channel": sales_by_country_channel,
        "median": median,
        "mean": mean,
        "price_by_product": price_by_product,
    }


data = load_data()

with st.container(horizontal=True):
    st.metric(
        "Ventas totales",
        f"${data['total_sales']:,.0f}",
        border=True,
        help="Suma de todas las ventas registradas.",
    )
    st.metric(
        "Órdenes únicas",
        f"{data['unique_orders']:,}",
        border=True,
        help="Número de pedidos distintos registrados.",
    )
    st.metric(
        "Cajas enviadas",
        f"{data['total_boxes_shipped']:,}",
        border=True,
        help="Total de unidades (cajas) vendidas.",
    )

col1, col2 = st.columns(2)
with col1, st.container(border=True):
    st.subheader("Ventas por producto")
    st.caption("Qué productos generan más ingresos en dólares.")
    st.bar_chart(
        data["sales_by_product"],
        x="Product",
        y="sales",
        width="stretch",
    )
with col2, st.container(border=True):
    st.subheader("Ventas por país y canal")
    st.caption("Dónde se vende más, comparando canal retail vs online.")
    st.bar_chart(
        data["sales_by_country_channel"],
        width="stretch",
    )

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    st.subheader("Ticket promedio")
    st.caption(
        "Media = promedio simple. Mediana = valor típico, no afectada por ventas extremas."
    )
    with st.container(horizontal=True):
        st.metric("Media", f"${data['mean']:,.2f}", border=True)
        st.metric("Mediana", f"${data['median']:,.2f}", border=True)
with col4, st.container(border=True):
    st.subheader("Precio por caja: listado vs real")
    st.caption(
        "Precio de lista vs precio real cobrado por caja. "
        "El % es el descuento implícito entre ambos."
    )
    st.dataframe(
        data["price_by_product"],
        hide_index=False,
        column_config={
            "listed_price": st.column_config.NumberColumn(
                "Precio listado", format="$%.2f"
            ),
            "avg_effective": st.column_config.NumberColumn(
                "Precio efectivo medio", format="$%.2f"
            ),
            "total_amount": st.column_config.NumberColumn("Ventas totales"),
            "total_boxes": st.column_config.NumberColumn("Cajas totales"),
            "weighted_price": st.column_config.NumberColumn(
                "Precio ponderado", format="$%.2f"
            ),
            "discount_gap_pct": st.column_config.NumberColumn(
                "Descuento implícito", format="%.2f%%"
            ),
        },
    )
