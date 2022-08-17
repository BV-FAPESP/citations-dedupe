"""
The methods in this file will be used in the dedupe_gazetteer.py file

The methods "preProcess" and "readData"
were obtained from https://github.com/dedupeio/dedupe-examples

"""


import csv, re, os
import collections
import dedupe

from unidecode import unidecode


def preProcess(column):
    """
    Do a little bit of data cleaning with the help of Unidecode and Regex.
    Things like casing, extra spaces, quotes and new lines can be ignored.
    """

    column = unidecode(column)
    column = re.sub('\n', ' ', column)
    column = re.sub('/', ' ', column)
    column = re.sub(":", ' ', column)
    column = re.sub(' +', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column:
        column = None
    return column


def readData(filename):
    """
    Read data from a CSV file (filename) and create a dictionary of records (data_d),
    where the key is a unique record ID (record_id).
    """

    data_d = {}

    with open(filename) as f:
        reader = csv.DictReader(f, delimiter='|')
        for i, row in enumerate(reader):
            clean_row = [(key, preProcess(value)) for (key, value) in list(row.items())]
            record_id = filename + str(i)
            data_d[record_id] = dict(clean_row)

    return data_d


def getTrainingData(messy_d, canonical_d, sample_size):
    """
    Read data from messy_d and canonical_d
    and create a list called labeled_pair_groups_list.
    This list contains tuples such as
    each tuple contains two dictionaries with n elements, where n=sample_size:
    - labeled_messy_d: A dicionary with n elements in messy_d
    - labeled_canonical_d: A dicionary with n elements in in canonical_d,
      where for each item in it contains the same link_id in an item in
      labeled_messy_d.
    """

    canonical_record_ids = {}
    for record_id, row in canonical_d.items():
        link_id = row['link_id']
        canonical_record_ids[link_id] = record_id


    # computing labeled messy data as a dictionary
    labeled_pair_groups_list = []
    labeled_canonical_d = {}
    labeled_messy_d = {}
    i = 0

    for messy_record_id, row in list(messy_d.items()):
        link_id = row['link_id']
        canonical_record_id = canonical_record_ids[link_id]
        labeled_canonical_d[canonical_record_id] = canonical_d[canonical_record_id]
        labeled_messy_d[messy_record_id] = messy_d[messy_record_id]

        i += 1
        j = i % sample_size
        if j == 0 or len(messy_d)==i:
            labeled_pair_groups_list.append((labeled_messy_d,labeled_canonical_d))
            labeled_canonical_d = {}
            labeled_messy_d = {}


    return labeled_pair_groups_list

def getTrueMatchesSet(canonical_d, messy_d):
    """
    Creates a set of true matches
    """

    true_matches_s = set()

    canonical_record_ids = {}
    for canonical_record_id, row in list(canonical_d.items()):
        link_id = row['link_id']
        canonical_record_ids[link_id] = canonical_record_id

    for messy_record_id, row in list(messy_d.items()):
        link_id = row['link_id']
        canonical_record_id = canonical_record_ids[link_id]
        pair = (messy_record_id, canonical_record_id)
        true_matches_s.add(frozenset(pair))

    return true_matches_s


def getDiceCoefficient(gazetteer_obj, canonical_d, validation_d):
    """
    Computes the Dice Coefficient to the result obtained from
    the prediction process for the validation messy set (validation_d).
    """

    # get matches
    print('Validation process...')
    gazetteer_obj.index(canonical_d)
    results = gazetteer_obj.search(validation_d, threshold=0.5, n_matches=1, generator=True)

    messy_matches = collections.defaultdict(dict) # dicionario cujos valores sao dicionarios
    found_matches_s = set()
    for messy_record_id, matches in results: # format of an item in results: (messy_record_id,((canon_record_id,score),...)
        for canon_record_id, score in matches:
            pair = (messy_record_id, canon_record_id)
            found_matches_s.add(frozenset(pair))

    true_matches_s = getTrueMatchesSet(canonical_d, validation_d)

    # Computing Dice coefficient
    n_true_positives = len(found_matches_s.intersection(true_matches_s))
    print(f"[Validation] True Positives = {n_true_positives}")
    n_false_positives = len(found_matches_s) - n_true_positives
    n_false_negatives = len(true_matches_s) - n_true_positives

    dc = 2*n_true_positives/float((2*n_true_positives) + n_false_negatives + n_false_positives)

    return dc


################################################################################


def evaluateMatches(found_matches:set, true_matches:set, n_messy_test:int, n_canonical:int):
    """
    Evaluates the matches found in the prediction process
    """

    n_true_matches = len(true_matches)
    n_found_matches = len(found_matches)

    # all_possible_matches = n_messy_test * n_canonical
    # false_matches = all_possible_dupes - true_matches
    n_false_matches = n_messy_test * n_canonical - n_true_matches

    print(f"Number of known match pairs (true matches): {n_true_matches}")
    print(f"Number of matches found: {n_found_matches} \n")
    #print(f"Number of false matches: {n_false_matches}")

    # True Positives : matches found correctly
    n_true_positives = len(found_matches.intersection(true_matches))
    print(f"Number of matches found correctly (True Positives): {n_true_positives}")

    # False Positives: matches found incorrectly
    n_false_positives = n_found_matches - n_true_positives
    print(f"Number of matches found incorrectly (False Positives): {n_false_positives}")

    # True Negatives : matches not found correctly
    n_true_negatives = n_false_matches - n_false_positives
    print(f"Number of matches not found correctly (True Negatives): {n_true_negatives}")

    # False Negatives: matches not found incorrectly (true matches not founded)
    n_false_negatives = n_true_matches - n_true_positives
    print(f"Number of matches not found incorrectly (False Negatives): {n_false_negatives} \n")

    print('Evaluation Metrics:')
    # Relevance denotes how well a retrieved set meets the information need of the user.
    # precision and recall are based on an understanding and measure of relevance.

    # Precision, also called positive predictive value
    # It is the fraction of relevant instances (true matches) among the retrieved instances (all matches found)
    # In other words, the fraction of matches found that are relevant to the query
    # How many matches found are true matches?
    precision = n_true_positives/float(n_true_positives + n_false_positives) # found_matches = n_true_positives + n_false_positives
    print(f'Precision = {round(precision,4)}')

    # Recall, also known as sensitivity
    # It is the fraction of the total amount of relevant instances (all true matches) that were successfully retrieved
    # In other words, the fraction of the total true matches (ground truth) that were successfully found
    # How many true matches were found?
    recall = n_true_positives/float(n_true_positives + n_false_negatives) # true_matches = n_true_positives + n_false_negatives
    print(f'Recall = {round(recall,4)}')

    # Dice similarity coefficient, also called
    # F1-score, F-measure, Sorensen–Dice coefficient and Hellden's mean accuracy index
    # It can be viewed as a similarity measure over sets (matches found and true matches)
    # Dice_coeficient = 2*n_true_positives/float((2*n_true_positives) + n_false_negatives + n_false_positives)
    Dice_coeficient = 2*precision*recall/(precision + recall)
    print(f"Dice similarity coeficient: {round(Dice_coeficient,4)} \n")



def readDataToSaveResults(filename):
    """
    Read data from a CSV file (filename) and create a dictionary of records (data_d),
    where the key is a unique record ID (record_id).
    Here the row is not pre-processed, compared to the readData method.
    """

    data_d = {}

    with open(filename) as f:
        reader = csv.DictReader(f, delimiter='|')
        for i, row in enumerate(reader):
            record_id = filename + str(i)
            data_d[record_id] = dict(row)

    return data_d
