from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

import pandas as pd

sections = pd.read_csv("./data/processed/sections/sections.csv")

documents = sections["text"]
labels = sections["label"]

X_train, X_test, y_train, y_test = train_test_split(documents, labels, test_size=0.2, random_state=42)

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LinearSVC())
])

pipeline.fit(X_train, y_train)

accuracy = pipeline.score(X_test, y_test)
print(f"Accuracy: {accuracy}")