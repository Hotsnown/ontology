import pandas as pd
import numpy as np

cepc = pd.read_csv("./data/interim/cepc.csv")

demandes = cepc[["résumé", "title", "header"]]
print(demandes)
demandes.to_csv("./data/interim/demandes.csv", encoding="utf-8")