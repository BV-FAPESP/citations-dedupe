"""
This is file contains a sample main function.
You can build your own, to simulate and test your data.
It is not a TEST file, it is a sample file to run the algorithm.
"""

import pdb
from xmlrpc.client import boolean
from src.dedupe_gazetteer import *
from src.dedupe_gazetteer_utils import *


import logging
from datetime import datetime
import optparse
import _io, os
import unittest
import dedupe
import itertools
from collections import defaultdict
from settings import *



def train(noise):
    VARIABLES = [
                    {'field': 'nome', 'type': 'String'},
                    {'field': 'nome', 'type': 'Text'},
                    {'field': 'primeiro_nome', 'type':'Exact', 'has missing': True},
                    {'field': 'abr', 'type':'ShortString'},
                    {'field': 'ult_sobrenome', 'type': 'Exact'}
                ]

    training_element = TrainingElement(VARIABLES)

    """
    Skip training if you have already trained, otherwise
    it will delete your trained and settings files, and train again.
    """
    tp = TrainingProcess(op_settings_file, op_training_file, training_element)
    start_time = datetime.now()
    labeled_sample_size = 1000
    noisify = Noisify(noise[0], noise[1], noise[2])
    tp.training(ip_canonical_file, ip_messy_training_file, ip_messy_validation_file, labeled_sample_size, noisify)
    end_time = datetime.now()
    print(f"Training Time: {end_time - start_time} \n")


def predict():
    start_time = datetime.now()

    ### Prediction
    model_evaluation = ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
    tt = TrainingTest(ip_canonical_file, ip_messy_test_file, op_settings_file, op_matches_found_file, model_evaluation)
    tt.cluster_data()
    end_time = datetime.now()
    print(f"Prediction Time and File Recording Time: {end_time - start_time} \n")
    ###

    ### Performance of the algorithm
    start_time = datetime.now()
    tt.evaluate_model()
    end_time = datetime.now()
    print(f"Model Evaluation Time and Files Recording Time: {end_time - start_time} \n")
    ###

def build_noise():
    ruido = [1]
    abs_percent = [False]
    data_noise_per = [0,10,20,50,100]
    return list(itertools.product(ruido, abs_percent,data_noise_per))


if __name__ == '__main__':

    noises = build_noise()
    for noise in noises:
        print ('\n#############################################\n\n')
        print(f'Training with Noise: {noise}')
        start_time = datetime.now()
        train(noise)
        predict()
        end_time = datetime.now()
        print(f'Total Processing Time: {end_time - start_time}')
        print ('\n\n#############################################\n')
