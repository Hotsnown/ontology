import pandas as pd
import numpy as np

cepc = pd.read_csv("./data/interim/cepc.csv")
judilibre = pd.read_csv("./data/interim/judilibre.csv")

cepc["number"] = cepc["reference"].str.extract(r"(\d\d[/-]\d\d.?\d\d\d?)")

judilibre = judilibre.fillna("No Rupture Brutale found.")
judilibre['motivation'] = judilibre.apply(lambda row: ', '.join([row[col] for col in ["premier_motivation", "deuxième_motivation", "troisième_motivation", "quatrième_motivation"] if "rupture brutale" in row[col]]), axis=1)

merged_df = pd.merge(cepc, judilibre, on='number', how='inner')

summary_df = merged_df[["résumé", "motivation"]]

summary_df = summary_df.dropna()
print(len(summary_df))
summary_df.to_csv("./data/interim/summary.csv")