import pandas as pd

df = pd.read_csv("data_sets/Chocolate_Sales.CSV")

boxes_shipped_by_country = df.groupby("Country", as_index=False).agg(
    total_shipped=("Boxes_Shipped", "sum")
)

print("SUMA DE CAJAS ENVIADAS POR PAIS")
print(boxes_shipped_by_country)
