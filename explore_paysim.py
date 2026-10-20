import pandas as pd

df = pd.read_csv("dataset/paysim.csv", nrows=200_000)

print("Shape (rows, columns):", df.shape)
print("\nColumns and types:")
print(df.dtypes)
print("\nFirst 5 rows:")
print(df.head())
print("\nTransaction types:")
print(df["type"].value_counts())
print("\nFraud rate:", df["isFraud"].mean())
