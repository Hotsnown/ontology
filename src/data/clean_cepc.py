import re
from spellchecker import SpellChecker

with open("./data/raw/CEPC.txt", "r", encoding="utf-8") as data:
    content = data.read()

# Split the string into lines
lines = content.split('\n')

# Strings that a line shouldn't start with
ignored_startswith = ["CA Paris,", "Cass. com.", "CA Grenoble", "Décision antérieure :", "Com.,", "CA Lyon,", "Page |", "CA Dijon,"]

# String to be replaced
replace_string = "A4798WUA.pdf"

# Regular expressions for substitution
regex_substitutions = [
    (r'^[\d.]+\s', ''), # Number preceding the text
    (r'CA Paris, \d{1,2} [éa-zA-Z]+ 20\d{2}, n° ?\d+ ?/\d+\s?;?', ''),
    (r'\d+ : \d+\s?!?\s?\d+', '')
]

def remove_duplicates(input_list):
    return list(set(input_list))

# Apply all transformations
for regex, replacement in regex_substitutions:
    lines = [
        re.sub(regex, replacement, line) for line in lines
        if not line.startswith(tuple(ignored_startswith))
    ]

# Replace specific string
lines = [line.replace(replace_string, "") for line in lines]

#Remove duplicates
lines = remove_duplicates(lines)

#Spell check
def correct_spelling(input_list):
    spell = SpellChecker(language='fr')
    corrected_list = []

    for string in input_list:
        corrected_string = []
        words = string.split()
        for word in words:
            # Get the one 'most likely' answer
            corrected_word = spell.correction(word)
            corrected_string.append(corrected_word)
        corrected_list.append(' '.join(corrected_string))
    
    return corrected_list


# Join the lines back together
result = '\n'.join(lines)

with open("./data/interim/CEPC_clean.txt", "w", encoding="utf-8") as data:
    data.write(result)
    print("CEPC has been cleaned!")