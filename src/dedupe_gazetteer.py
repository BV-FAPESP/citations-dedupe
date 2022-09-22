from random import sample

import os, csv, copy
import collections
import dedupe
import string
import random
import math

from abc import ABC, abstractmethod
from src.generic_utils import *

from src.dedupe_gazetteer_utils import (readData,getTrainingData, getTrueMatchesSet,
                                        getDiceCoefficient, evaluateMatches, readDataToSaveResults)

from settings import *


class TrainingElement:
    def __init__(self, variables: list):
        self.gazetteer = dedupe.Gazetteer(variables)
        self.performance = None

    def prepare_training(self, labeled_messy_d: dict, labeled_canonical_d: dict, training_file: str=None, sample_size: int=1500):
        """ Pre training required """
        self.labeled_messy_d = labeled_messy_d
        self.labeled_canonical_d = labeled_canonical_d
        if training_file:
            print('Reading labeled examples from ', training_file)
            try:
                with open(training_file) as tf:
                    self.gazetteer.prepare_training(self.labeled_messy_d,self.labeled_canonical_d,training_file=tf)
            except IOError:
                raise
        else:
            self.gazetteer.prepare_training(self.labeled_messy_d,
                                            self.labeled_canonical_d,
                                            sample_size=sample_size)

    def model_training(self):
        """ Mark pairs for already labeled data and train """
        print('Starting labeling and train the model...')
        n_distinct_pairs = len(self.labeled_messy_d)
        labeled_pairs = dedupe.training_data_link(self.labeled_messy_d,
                                                  self.labeled_canonical_d,
                                                  common_key='link_id',
                                                  training_size=n_distinct_pairs)
        self.gazetteer.mark_pairs(labeled_pairs)
        self.gazetteer.train()

    def write_training(self, op_training_file:str):
        """ When finished, save the training away to disk
        Write a JSON file that contains labeled examples (pairs) """
        with open(op_training_file, 'w') as tf:
            self.gazetteer.write_training(tf)

    def write_settings(self, op_settings_file:str):
        """ Save the weights and predicates to disk"""
        with open(op_settings_file, 'wb') as sf:
            self.gazetteer.write_settings(sf) # Write a settings file containing the data model and predicates.

    def cleanup_training(self):
        """ Clean up data we used for training. Free up memory. """
        self.gazetteer.cleanup_training()

    def training_performance(self, value):
        self.performance = value

    def __ge__(self, other):
        return self.performance >= other.performance

    def __str__(self):
        return str(round(self.performance, 4))


class TrainingProcess:
    def __init__(self, op_settings_file: str, op_training_file: str, training_element: TrainingElement) -> None:
        self.op_settings_file = op_settings_file
        self.op_training_file = op_training_file
        self.training_element = training_element

        # Always remove settings and training files on __init__
        try:
            os.unlink(self.op_settings_file)
            os.unlink(self.op_training_file)
        except FileNotFoundError:
            pass

    def training(self, ip_canonical_file, ip_messy_training_file: str, ip_messy_validation_file: str, labeled_sample_size: int=1000):
        # Reading data
        canonical_d = readData(ip_canonical_file)
        print(f"Number of records from canonical data (pesquisadores unicos): {len(canonical_d)}")

        messy_training_d = readData(ip_messy_training_file)
        print(f"Number of records from messy data for training (autorias): {len(messy_training_d)}")
        messy_validation_d = readData(ip_messy_validation_file)
        labeled_pair_groups_list = getTrainingData(messy_d=messy_training_d, canonical_d=canonical_d,  sample_size=labeled_sample_size)
        print(f"Number of records from messy data for validation (autorias): {len(messy_validation_d)}")
        print(f"Number of labeled pair groups for training: {len(labeled_pair_groups_list)}")
        print("\n[TRAINING PROCESS]")
        trained_element = copy.deepcopy(self.training_element)
        best_trained_element = None

        i = 0
        stop = False
        n_groups = len(labeled_pair_groups_list)

        while i < n_groups and stop == False:
            print('=================================================================')
            print(f'Iteration: {i}')
            (labeled_messy_d, labeled_canonical_d) = labeled_pair_groups_list[i]
            if i == 0:
                trained_element.prepare_training(labeled_messy_d, labeled_canonical_d, sample_size=150000)
                trained_element.model_training()
                trained_element.write_training(self.op_training_file)

                dc = getDiceCoefficient(gazetteer_obj=trained_element.gazetteer, canonical_d=canonical_d, validation_d=messy_validation_d)
                trained_element.training_performance(dc)
                print(f'[Validation] Dice Coefient: {trained_element}')
                best_trained_element = copy.deepcopy(trained_element)
            else:
                try:
                    trained_element = copy.deepcopy(self.training_element)
                    trained_element.prepare_training(labeled_messy_d, labeled_canonical_d, training_file=self.op_training_file)
                    trained_element.model_training()
                    dc = getDiceCoefficient(gazetteer_obj=trained_element.gazetteer, canonical_d=canonical_d, validation_d=messy_validation_d)
                    trained_element.training_performance(dc)

                    if trained_element.performance > best_trained_element.performance:
                        print(f'[Validation] Dice Coefient (new): {trained_element}')
                        best_trained_element = copy.deepcopy(trained_element)
                        best_trained_element.write_training(self.op_training_file)
                    else:
                        stop = True
                        print(f'[Validation] Dice Coefient (best): {best_trained_element}')
                        print(f'[Validation] Dice Coefient (new): {trained_element}')
                        print('Stopping...')
                except Exception as e:
                    print("An exception occurred: ",e)
                    stop = True
                    pass

            trained_element.cleanup_training()
            del trained_element
            i += 1

        # Write a settings file containing the best data model and predicates.
        best_trained_element.write_settings(self.op_settings_file)

        # Clean up data we used for training
        best_trained_element.cleanup_training()

        print('=================================================================')



class ModelEvaluation():
    """ Model Evaluation """

    def __init__(self, ip_canonical_file: str, ip_messy_test_file: str, op_false_positives_file: str, op_false_negatives_file: str):
        self.ip_canonical_file = ip_canonical_file
        self.ip_messy_test_file = ip_messy_test_file
        self.op_false_positives_file = op_false_positives_file
        self.op_false_negatives_file = op_false_negatives_file
        self.canonical_2_save_d = readDataToSaveResults(self.ip_canonical_file)
        self.messy_test_2_save_d = readDataToSaveResults(self.ip_messy_test_file)


    def evaluate_matches(self, canonical_d: dict, messy_test_d: dict, found_matches_s: set):
        n_messy_test = len(messy_test_d)
        n_canonical = len(canonical_d)

        ### True matches set
        true_matches_s = getTrueMatchesSet(canonical_d=canonical_d, messy_d=messy_test_d)
        evaluateMatches(found_matches=found_matches_s, true_matches=true_matches_s, n_messy_test=n_messy_test, n_canonical=n_canonical)

        true_positives_s = found_matches_s.intersection(true_matches_s)
        self.false_positives_s = found_matches_s.difference(true_positives_s)
        self.false_negatives_s = true_matches_s.difference(found_matches_s)



    def save_false_positives(self, messy_matches, cluster_membership):
        ### salvando informacao obtida da clusterizacao

        false_positives_d = collections.defaultdict(list)
        for (record_id_1, record_id_2) in self.false_positives_s:
            canon_record_id = record_id_1 if self.ip_canonical_file in record_id_1 else record_id_2
            if canon_record_id not in false_positives_d.keys():
                false_positives_d[canon_record_id] = []

        for (record_id_1, record_id_2) in self.false_positives_s:
            messy_record_id = record_id_1 if self.ip_messy_test_file in record_id_1 else record_id_2
            canon_record_id = record_id_1 if self.ip_canonical_file in record_id_1 else record_id_2
            false_positives_d[canon_record_id].append(messy_record_id)

        # obtendo cabeçalho original
        with open(self.ip_canonical_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='|')
            headers = reader.fieldnames

        # salvando falsos positivos
        with open(self.op_false_positives_file, 'w') as f_output:
            fieldnames = ['cluster_id','link_score','source_file', 'record_id'] + headers
            writer = csv.DictWriter(f_output, delimiter='|', fieldnames=fieldnames)
            writer.writeheader() # save the new fieldnames

            # Salvando:
            # - entidades do conjunto canonico, cuja correspondencia foi encontrada incorretamente
            # - entidades do conjunto messy, cuja correspondencia foi encontrada incorretamente
            for canon_record_id, messy_record_ids in list(false_positives_d.items()):
                cluster_id =  cluster_membership[canon_record_id]
                canon_record_row = self.canonical_2_save_d[canon_record_id].copy()
                cluster_details = {'cluster_id':cluster_id, 'link_score':None, 'source_file':self.ip_canonical_file, 'record_id':canon_record_id}
                canon_record_row.update(cluster_details)
                writer.writerow(canon_record_row)
                for messy_record_id in messy_record_ids:
                    score = messy_matches[messy_record_id][canon_record_id]
                    messy_record_row = self.messy_test_2_save_d[messy_record_id].copy()
                    cluster_details = {'cluster_id':cluster_id, 'link_score':score, 'source_file':self.ip_messy_test_file, 'record_id':messy_record_id}
                    messy_record_row.update(cluster_details)
                    writer.writerow(messy_record_row)

    def save_false_negatives(self):
        ### salvando informacao obtida da clusterizacao

        false_negatives_d = collections.defaultdict(list)
        for (record_id_1, record_id_2) in self.false_negatives_s:
            canon_record_id = record_id_1 if self.ip_canonical_file in record_id_1 else record_id_2
            if canon_record_id not in false_negatives_d.keys():
                false_negatives_d[canon_record_id] = []

        for (record_id_1, record_id_2) in self.false_negatives_s:
            messy_record_id = record_id_1 if self.ip_messy_test_file in record_id_1 else record_id_2
            canon_record_id = record_id_1 if self.ip_canonical_file in record_id_1 else record_id_2
            false_negatives_d[canon_record_id].append(messy_record_id)

        # obtendo cabeçalho original
        with open(self.ip_canonical_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='|')
            headers = reader.fieldnames

        # salvando falsos negativos
        with open(self.op_false_negatives_file, 'w') as f_output:
            fieldnames = ['cluster_id','link_score','source_file', 'record_id'] + headers
            writer = csv.DictWriter(f_output, delimiter='|', fieldnames=fieldnames)
            writer.writeheader() # save the new fieldnames

            # Salvando:
            # - entidades do conjunto canonico, cuja correspondencia nao foi encontrada
            # - entidades do conjunto messy, cuja correspondencia nao foi encontrada
            for canon_record_id, messy_record_ids in list(false_negatives_d.items()):
                canon_record_row = self.canonical_2_save_d[canon_record_id].copy()
                cluster_details = {'cluster_id':None, 'link_score':None,
                                   'source_file':self.ip_canonical_file, 'record_id':canon_record_id}
                canon_record_row.update(cluster_details)
                writer.writerow(canon_record_row)
                for messy_record_id in messy_record_ids:
                    messy_record_row = self.messy_test_2_save_d[messy_record_id].copy()
                    cluster_details = { 'cluster_id':None, 'link_score':None,
                                        'source_file': self.ip_messy_test_file,'record_id': messy_record_id}
                    messy_record_row.update(cluster_details)
                    writer.writerow(messy_record_row)


class Noisify():
    """
        Generates data augmentation adding noise based on percentual or number of characters.
    """
    def __init__(self, amount, percentual=True):
        self.amount = amount
        self.percentual = percentual # if not true, amount is treated as number of characters

    def add_noise(self, name):
        if self.percentual:
            number_of_characters = math.ceil(((len(name)*self.amount/100)))
        else:
            number_of_characters = self.amount
        special_characters_indices = [i for i, c in enumerate(name)
                                      if c == ' ' or c == '.' or c == ',']
        noise_indices = []
        for i in range(number_of_characters):
            noise_indices.append(random.choice([i for i in range(1,len(name))
                                                if i not in special_characters_indices]))
        s = list(name)
        for noise in noise_indices:
            s[noise] = random.choice(string.ascii_letters)

        return ''.join(s)

    def get_noisy_data(self, data):
        for key in data:
            data[key]['nome'] = self.add_noise(data[key]['nome'])
            data[key]['primeiro_nome'] = getLongFirstName(remover_acentos(data[key]['nome']))
            data[key]['abr'] = getPartialAbbreviation(remover_acentos(data[key]['nome']))
            data[key]['ult_sobrenome'] = getLastName(remover_acentos(data[key]['nome']))

        return data


class IPredict(ABC):
    @abstractmethod
    def __init__():
        raise NotImplementedError()

    def cluster_data(self):
        print('Clustering new data...')
        print('Reading from', self.op_settings_file)
        with open(self.op_settings_file, 'rb') as sf:
            gazetteer = dedupe.StaticGazetteer(sf)
        gazetteer.index(self.canonical_d)

        results = gazetteer.search(self.messy_test_d, threshold=0.5, n_matches=1, generator=True)
        # n_matches=1 -> se obtem um unico pesquisador associado por cada autor de artigo em messy_test_d
        # se u valor nao eh dado, a busca retorna todos os possiveis matches acima do threshold
        # generator=True -> o match gera uma sequencia de possiveis matches, em vez de uma lista.
        # Default generator=False.

        messy_matches = collections.defaultdict(dict) # dicionario cujos valores sao dicionarios
        found_matches_s = set()

        # format of an item in "results": (messy_record_id,((canon_record_id,score),...))
        for messy_record_id, matches in results:
            for canon_record_id, score in matches: # matches = ((canon_record_id,score),...)
                messy_matches[messy_record_id][canon_record_id] = score
                found_pair = (messy_record_id, canon_record_id)
                found_matches_s.add(frozenset(found_pair))


        cluster_membership = {}
        cluster_id = 0

        for messy_record_id in messy_matches.keys():
            matches = messy_matches[messy_record_id] # dictionary with a single element for n_matches=1
            for canon_record_id in matches:
                if canon_record_id not in cluster_membership:
                    cluster_membership[canon_record_id] = cluster_id
                    cluster_id += 1

        self.found_matches_s = found_matches_s
        self.messy_matches = messy_matches
        self.cluster_membership = cluster_membership
        self.save_prediction_result()



class ProductionPredict(IPredict):
    """ Classication or Bloking Process """

    def __init__(self, ip_canonical_file: str, ip_messy_test_file: str, op_settings_file: str, op_matches_found_file: str):
        print('\n[PREDICTION PROCESS]')
        self.ip_messy_test_file = ip_messy_test_file
        self.op_matches_found_file = op_matches_found_file

        print('Importing messy test data ...')
        self.messy_test_d = readData(ip_messy_test_file)
        print(f"Number of records from messy data for test (autorias): {len(self.messy_test_d)}")

        print('Reading from', op_settings_file)
        self.op_settings_file = op_settings_file

        self.ip_canonical_file = ip_canonical_file
        self.canonical_d = readData(ip_canonical_file)


class TrainingTest(IPredict):
    def __init__(self, ip_canonical_file: str,
                        ip_messy_test_file: str,
                        op_settings_file: str,
                        op_matches_found_file: str,
                        model_evaluation: ModelEvaluation=None,
                        noisify: Noisify=None):

        print('\n[PREDICTION PROCESS]')
        self.ip_messy_test_file = ip_messy_test_file
        self.op_matches_found_file = op_matches_found_file

        print('Importing messy test data ...')
        self.messy_test_d = readData(ip_messy_test_file)
        print(f"Number of records from messy data for test (autorias): {len(self.messy_test_d)}")

        print('Reading from', op_settings_file)
        self.op_settings_file = op_settings_file

        self.ip_canonical_file = ip_canonical_file
        self.canonical_d = readData(ip_canonical_file)

        self.model_evaluation = model_evaluation
        self.noisify_o = noisify


    def save_prediction_result(self):
        """ salvando informacao obtida da clusterizacao """

        canonical_d = readDataToSaveResults(self.ip_canonical_file) #self.canonical_d
        messy_test_d = readDataToSaveResults(self.ip_messy_test_file) #self.messy_test_d

        found_matches_s = self.found_matches_s
        messy_matches = self.messy_matches
        cluster_membership = self.cluster_membership


        found_matches_d = collections.defaultdict(list)
        for (record_id_1, record_id_2) in found_matches_s:
            canon_record_id = record_id_1 if self.ip_canonical_file in record_id_1 else record_id_2
            if canon_record_id not in found_matches_d.keys():
                found_matches_d[canon_record_id] = []

        for (record_id_1, record_id_2) in found_matches_s:
            messy_record_id = record_id_1 if self.ip_messy_test_file in record_id_1 else record_id_2
            canon_record_id = record_id_1 if self.ip_canonical_file in record_id_1 else record_id_2
            found_matches_d[canon_record_id].append(messy_record_id)

        # obtendo cabeçalho original
        with open(self.ip_canonical_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='|')
            headers = reader.fieldnames

        # salvando resultados
        with open(self.op_matches_found_file, 'w') as f_output:
            fieldnames = ['cluster_id','link_score','source_file', 'record_id'] + headers
            writer = csv.DictWriter(f_output, delimiter='|', fieldnames=fieldnames)
            writer.writeheader() # save the new fieldnames

            # Salvando:
            # - entidades encontradas do conjunto canonico
            # - entidades encontradas do conjunto messy
            for canon_record_id, messy_record_ids in list(found_matches_d.items()):
                cluster_id =  cluster_membership[canon_record_id]
                canon_record_row = canonical_d[canon_record_id].copy()
                cluster_details = {'cluster_id':cluster_id, 'link_score':None, 'source_file':self.ip_canonical_file, 'record_id':canon_record_id}
                canon_record_row.update(cluster_details)
                writer.writerow(canon_record_row)
                for messy_record_id in messy_record_ids:
                    score = messy_matches[messy_record_id][canon_record_id]
                    messy_record_row = messy_test_d[messy_record_id].copy()
                    cluster_details = {'cluster_id':cluster_id, 'link_score':score, 'source_file':self.ip_messy_test_file, 'record_id':messy_record_id}
                    messy_record_row.update(cluster_details)
                    writer.writerow(messy_record_row)

    def evaluate_model(self):
        self.model_evaluation.evaluate_matches(self.canonical_d, self.messy_test_d, self.found_matches_s)
        self.model_evaluation.save_false_positives(self.messy_matches, self.cluster_membership)
        self.model_evaluation.save_false_negatives()

    def noisify(self):
        self.messy_test_d = self.noisify_o.get_noisy_data(self.messy_test_d)
