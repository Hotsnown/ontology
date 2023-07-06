from tika import parser # pip install tika
import re
import pandas as pd

raw = parser.from_file('data/raw/Vocabulaire juridique by Gérard Cornu.pdf')
texts =raw['content']

splitted = re.split(r"\n\n([A-Z]{4,})", texts)
all_terms = splitted[301:]
terms = [all_terms[n] for n in range(len(all_terms)) if n%2==0]
content = [all_terms[n] for n in range(len(all_terms)) if not n%2==0]
dictionnaire = zip(terms, content)

pd.DataFrame(dictionnaire).to_csv("data/processed/dict.csv")