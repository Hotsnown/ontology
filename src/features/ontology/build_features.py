
import spacy
from spacy.matcher import DependencyMatcher
import pandas as pd

def create_terms():

    nlp = spacy.load('fr_core_news_md')
    matcher = DependencyMatcher(nlp.vocab)
    subject = [
        {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"} 
        },
        {
            "LEFT_ID": "verb",
            "REL_OP": ">",
            "RIGHT_ID": "subject",
            "RIGHT_ATTRS": {"DEP": {"IN": ["nsubj", "nsubjpass", "csubj", "csubjpass"]}},
        },
    ]
    object = [
        {
        "RIGHT_ID": "verb", 
        "RIGHT_ATTRS": {"POS": "VERB"} 
        },
        {
            "LEFT_ID": "verb",
            "REL_OP": ">",
            "RIGHT_ID": "object",
            "RIGHT_ATTRS": {"DEP": {"IN": ["obj", "dobj", "iobj", "pobj"]}},
        }
    ]

    PP = [
        {
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
        },
        {
            "LEFT_ID": "verb",
            "REL_OP": ">",
            "RIGHT_ID": "PP",
            "RIGHT_ATTRS": {"DEP": {"IN": ["obl", "obl:agent", "obl:arg", "obl:mod"]}},
        }
    ]

    matcher.add("FOUNDED", [subject, object, PP])

    with open("./data/raw/CEPC.txt", "r", encoding="utf8") as file:
        content = file.read()
        texts = content.split("\n")

    df = pd.DataFrame(texts[10000:10300], columns=["text"])
    df['doc'] = df['text'].apply(nlp)

    results = []
    for doc in df["doc"]:
        matches = matcher(doc)
        for match_id, token_ids in matches:
            result = {}
            for i in range(len(token_ids)):
                result[i] = doc[token_ids[i]].lemma_
            results.append(result)

    dep_matcher_df = pd.DataFrame(results)
    dep_matcher_df = dep_matcher_df.fillna(0)

    dep_matcher_df.to_csv("./data/processed/deps.csv")

create_terms()