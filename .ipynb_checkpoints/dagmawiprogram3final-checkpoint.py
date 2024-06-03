"""
CS 401 Program 3
Dagmawi Zerihun
Date : 7 Nov, 2023
ALL SENTPOS FILES USED IN THIS PROGRAM ARE TAKEN FROM DR.BUELL's "Data" folder
"""

# pylint: disable=trailing-whitespace
import re
from collections import defaultdict, Counter

##############################################################

# Define the mapping from CLAWS tags to the Penn Treebank 
# tags used by Stanford and NLTK taggers
clawstopennmapping = {
    'NN1': 'NN',  # Singular common noun
    'NN2': 'NNS',  # Plural common noun
    'NP1': 'NNP',  # Singular proper noun
    'VVG': 'VBG',  # -ing participle of lexical verb
    'VV0': 'VB',   # Base form of lexical verb
    'VVN': 'VBN',  # Past participle of lexical verb
    'VVD': 'VBD',  # Past tense of lexical verb
    'VBZ': 'VBZ',  # -s form of lexical verb
    'VBP': 'VBP',  # Non-3rd person singular present verb
    'JJ':  'JJ',   # General adjective
    'RB':  'RB',   # General adverb
    'IN':  'IN',   # Preposition or subordinating conjunction
}

##############################################################
def mapclawstopenn(tag):
    """
    Map a CLAWS tag to its Penn Treebank equivalent.
    
    Parameters:
    tag (str): The CLAWS tag to be mapped.

    Returns:
    str: The corresponding Penn Treebank tag, 
    or None if not found.
    """
    return clawstopennmapping.get(tag, None)

def parsetaggedtext(text, taggertype):
    """
    Parse tagged text according to the specified tagger 
    type and map the tags.
    
    Parameters:
    text (str): The tagged text to parse.
    taggertype (str): The type of tagger ('CLAWS', 'NLTK', 
    or 'STANF').

    Returns:
    list: A list of tuples with words and their tags.
    """
    parsed = []
    for line in text.split('\n'):
        if 'SENTPOS' in line and taggertype in line:
            line = re.sub(r'^.*?([A-Z]+\s)', '', line)
            # Split the line into words and tags
            for wordtag in line.split():
                if '_' in wordtag:
                    word, tag = wordtag.rsplit('_', 1)
                    # Map CLAWS tags to Penn tags
                    if taggertype == 'CLAWS':
                        tag = mapclawstopenn(tag)
                    if tag is not None:
                        parsed.append((word, tag))
    return parsed
    
def loadtaggeddata(filepath):
    """
    Load tagged data from a specified file.
    
    Parameters:
    filepath (str): The path to the file containing
    tagged data.

    Returns:
    str: The content of the file.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def summarizediscrepancies(discrepancies, outputfilepath):
    with open(outputfilepath, 'w', encoding='utf-8') as file:
        for word, tags in discrepancies.items():
            taglist = ', '.join(
                f"{tagger}: {sorted(list(tagset))}" for tagger, tagset in tags.items()
            )
            file.write(f"word: {word}\ntags: {taglist}\n\n")

    
# pylint: disable=line-too-long    
# Load the data from files


def main():
    clawstext = loadtaggeddata('claws/zsentposclawstomsawyer.txt')
    nltktext = loadtaggeddata('nltk/zsentposnltktomsawyer.txt')
    stanfordtext = loadtaggeddata('stanf/zsentposstanftom.txt')


    # Parse the data
    clawsparsed = parsetaggedtext(clawstext, 'CLAWS')
    nltkparsed = parsetaggedtext(nltktext, 'NLTK')
    stanfordparsed = parsetaggedtext(stanfordtext, 'STANF')

    # Create a dictionary to cross-reference tags between taggers for each word
    crossref = defaultdict(lambda: defaultdict(set))

    # Populate the cross-reference dictionary
    for word, tag in clawsparsed:
        crossref[word.lower()]['claws'].add(tag)
    for word, tag in nltkparsed:
        crossref[word.lower()]['nltk'].add(tag)
    for word, tag in stanfordparsed:
        crossref[word.lower()]['stanford'].add(tag)

    # Find and count the discrepancies between the taggers
    discrepancies = {}
    for word, tags in crossref.items():
        tagsets = {tagger: frozenset(tagset) for tagger, tagset in tags.items()}
        if len(set(tagsets.values())) > 1:  # More than one unique tag set
            discrepancies[word] = tagsets

    # Count the discrepancies by tag
    discrepancycounts = Counter()
    for word, tagsets in discrepancies.items():
        for tagger, tagset in tagsets.items():
            discrepancycounts.update(tagset)

    # Sort and print the discrepancies
    sorteddiscrepancycounts = discrepancycounts.most_common()
    for tag, count in sorteddiscrepancycounts:
        print(f"{tag}: {count} discrepancies")

    # Output a sample of discrepancies for manual inspection
    print("\nSample of discrepancies:")
    for word, tagsets in list(discrepancies.items())[:10]:
        print(f"{word}: {tagsets}")
    
    outputfilepath = "discrepancies-tomsawyer.txt"
    summarizediscrepancies(discrepancies, outputfilepath)
    print(f"Discrepancies have been summarized and saved to {outputfilepath}")

# The docstring for the entire code is implied by the descriptions of each function.
# The functions collectively aim to compare and analyze discrepancies in POS tagging
# between different taggers for the text of "Hamlet".
main()