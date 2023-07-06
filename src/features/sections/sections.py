import pandas as pd
import numpy as np
import ast
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import preprocessing



judilibre = pd.read_csv("./data/interim/judilibre.csv")
dataset = judilibre[judilibre["zones"].notna()]

sections = []
for text, zones in zip(dataset["text"].values, dataset["zones"].values):
    for zone, index in ast.literal_eval(zones).items():
        start = index[0]["start"]
        end = index[0]["end"]
        sections.append((zone, text[start:end]))

inputs = []
for zone, text in sections:
    paras = text.split("\n")
    for para in paras:
        if para != "":
            inputs.append((zone, para))


data = pd.DataFrame(inputs, columns=["zone", "text"])

le = preprocessing.LabelEncoder()
le.fit(data["zone"].values.tolist())

data["label"] = le.transform(data["zone"].values.tolist())

data.to_csv("./data/processed/sections/sections.csv")