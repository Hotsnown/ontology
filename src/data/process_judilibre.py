import ast
import numpy as np
import pandas as pd

def fiches_arrêt(row, column): 
    if type(row["zones"]) is str:
      zones = ast.literal_eval(row["zones"])
      introduction = extract_section(row, zones, "introduction")
      expose = extract_section(row, zones, "expose")
      premier_moyen = extract_moyen(row, zones, 0)
      deuxième_moyen = extract_moyen(row, zones, 1)
      troisième_moyen = extract_moyen(row, zones, 2)
      quatrième_moyen = extract_moyen(row, zones, 3)
      premier_motivation = extract_motifs(row, zones, 0)
      deuxième_motivation = extract_motifs(row, zones, 1)
      troisième_motivation = extract_motifs(row, zones, 2)
      quatrième_motivation = extract_motifs(row, zones, 3)
      dispositif = extract_section(row, zones, "dispositif")
      annexes = extract_section(row, zones, "annexes")
      
      if column == "introduction": return introduction
      if column == "expose": return expose
      if column == "premier_moyen": return premier_moyen
      if column == "deuxième_moyen": return deuxième_moyen
      if column == "troisième_moyen": return troisième_moyen
      if column == "quatrième_moyen": return quatrième_moyen
      if column == "premier_motivation": return premier_motivation
      if column == "deuxième_motivation": return deuxième_motivation
      if column == "troisième_motivation": return troisième_motivation
      if column == "quatrième_motivation": return quatrième_motivation
      if column == "dispositif": return dispositif
      if column == "annexes": return annexes
   
    else:
      return np.nan

def extract_section(row, zones, header):
   try:
    start = zones.get(header)[0]["start"]
    end =  zones.get(header)[0]['end']
    return row["text"][start:end]
   except:
      return np.nan
   
def extract_moyen(row, zones, numéro):
  try:
    start = zones.get("moyens")[numéro]["start"]
    end =  zones.get("moyens")[numéro]['end']
    return row["text"][start:end]
  except:
      return np.nan
  s
def extract_motifs(row, zones, numéro):
  try:
    start = zones.get("motivations")[numéro]["start"]
    end =  zones.get("motivations")[numéro]['end']
    return row["text"][start:end]
  except:
      return np.nan
  
ca_decisions = pd.read_csv("./data/raw/decisions.csv")
cass_decisions = pd.read_csv("./data/raw/decisions_backup.csv")

rupture = pd.concat([ca_decisions, cass_decisions], ignore_index=True)

rupture = rupture.assign(**{column: rupture.apply(lambda row: fiches_arrêt(row, column), axis=1) 
                            for column in ["introduction", "expose", "premier_moyen", "deuxième_moyen", "troisième_moyen", "quatrième_moyen", "premier_motivation", "deuxième_motivation", "troisième_motivation", "quatrième_motivation", "dispositif", "annexes"]})

rupture.to_csv("./data/interim/judilibre.csv")