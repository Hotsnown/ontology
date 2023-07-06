import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def cooc_train_attributes():
    df = pd.read_csv("./data/processed/deps.csv")

    grouped_by_attribute = df.groupby("0")["1"].apply(list).reset_index()
    G = nx.Graph()

    for row in grouped_by_attribute.iterrows():
          for first_object in row[1][1]:
               for second_object in row[1][1]:
                    G.add_edge(first_object, second_object)
    
    print(G.edges)

cooc_train_attributes()