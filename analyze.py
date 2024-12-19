import pandas as pd

df = pd.read_csv('./sutr_winrate2.csv').head(100)
print(df[df["result"] >= 1_000_000])