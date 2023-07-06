import requests
import re
from pdfminer.high_level import extract_text
import textacy
import textacy.preprocessing as tprep
import pandas as pd
import os

import re
import json

cepc_links = [
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/bilan_faculte_droit2004_2006.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/bilan_faculte_droit2006_2007.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/bilan_cepc2008.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/bilan_cepc2009.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/rapports/rapport2010_2011.pdf#page=68",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/bilan_judiciaire_fac_montpellier.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/bilan_fac_montpellier2012.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/Bilan_decisions_judiciaires2013_faculte_montpellier.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/Bilan_decisions_judiciaires2014_faculte_montpellier.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/Bilan_decisions_judiciaires2015_faculte_montpellier.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/Bilan-decisions-judiciaires-2016-faculte-droit-Montpellier.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/Bilan-decisions-judiciaires-2017-faculte-droit-Montpellier.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/bilan-2018-des-decisions-judiciaires.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/bilan-de-jurisprudence-2019-montpelllier.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/Bilan-des-decisions-judiciaires-31-12-2020.pdf",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/Bilan-des-%20d%C3%A9cisions-%20judiciaires-2021-%20Faculte-Montpellier.pdf?v=1682318931",
              "https://www.economie.gouv.fr/files/files/directions_services/cepc/etude/bilan-des-decisions-judiciaires-31-12-2022.pdf?v=1682318931"
]

def download_file(url):

    try:
        year = re.findall(r"\d\d\d\d", url)[0]
    except:
        year = 2011

    # Specify the directory and filename
    directory = "./data/raw/"
    filename = f"{year}.pdf"

    # Create the file path
    file_path = os.path.join(directory, filename)

    if not os.path.isfile(file_path):

        response = requests.get(url)
        
        with open(f"./data/raw/{year}.pdf", "wb") as file:
            file.write(response.content)
    else:
        print(f"The file {filename} exists.")

[download_file(url) for url in cepc_links]

def read_pdf(filename, pages):
  text = extract_text(filename, page_numbers=pages)
  return text

with open("./src/data/cepc_pages.json", 'r', encoding="utf-8") as page_file:
     pages = json.loads(page_file.read())

with open("./src/data/cepc_headers.json", 'r', encoding="utf-8") as header_file:
     headers = json.loads(header_file.read())

def read_pages(year):
  t = list(filter(lambda x: x["year"] == year, pages["data"]))[0]
  return read_pdf(
       f"./data/raw/{year}.pdf", 
      range(t["analysis_start_page"], t["last_page"]))

def get_headers(year):
   return next(iter([h for h in headers["data"] if h["year"] == year]), {"headers": [{"title":"not found", "header":"not found"}]})

def parse_headers(splitted, year):
    headers_dict = get_headers(year)
    headers_all = set([header["title"] for header in headers_dict["headers"]])

    data = init_data(splitted, headers_dict, year)
    report_missing_headers(headers_all, data, year)

    return data


def init_data(splitted, headers_dict, year):
    data = []
    current_header = headers_dict["headers"][0]
    header_found = {current_header["title"]}

    for paragraph in splitted:

        for header in headers_dict["headers"]:
            if header["title"] in paragraph:
                current_header = header
                header_found.add(current_header["title"])

        data.append({"raw": paragraph,
                     "title": current_header["title"],
                     "header": current_header["header"],
                     "year": year})

    return data


def report_missing_headers(headers_all, data, year):
    header_found = set([entry["title"] for entry in data])
    difference = headers_all.difference(header_found)

    print(difference)
    print(f"{year} {len(difference)}")

def parse_documents(page):
  year = page["year"]
  content = read_pages(year)
  headers_dict = get_headers(year)

  for header in headers_dict["headers"]:
      title = header["title"]
      pattern = re.compile(title)
      content = re.sub(pattern, "\n"+title, content)

  splitted = content.split("\n\n")
  with open(f"./data/raw/cepc_{year}.json", "w", encoding="utf-8") as cepc_file:
     cepc_json = json.dumps({"data":splitted})
     cepc_file.write(cepc_json)
  data = parse_headers(splitted, page["year"])
  return data

data = []
for page in pages["data"]:
  data.extend(parse_documents(page))

df = pd.DataFrame(data)

df = df.applymap(lambda x: x.encode().
                 decode('utf-8') if isinstance(x, str) else x)

df["décision antérieure"] = df["raw"].str.extract(r"(Décision antérieure.*)")
df["clean"] = df["raw"].str.replace("Décision antérieure.*", "").str.replace(r"Page \| \d+\s+", "").str.replace("\n", "").str.replace("♀", "")
df["reference"] = df["clean"].str.extract(r"^(.*?\d\s?\d\d?\s?[\/-]?\d\d\.?\d\d\d?\d?)|^(.*\d\d\d\d\d? :).*")[0]
df["résumé"] =  df["clean"].str.extract(r"^.*?\d\s?\d\d?\s?[\/-]?\d\d\.?\d\d\d?\d? (.*)")

df = df[df["clean"].str.contains("CA|Com")]

df.to_csv("data/interim/cepc.csv",encoding='utf-8-sig')