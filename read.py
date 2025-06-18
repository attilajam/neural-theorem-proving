import pandas as pd 

df = pd.read_csv("output.csv")

print(len(set(df["theorem"])))
