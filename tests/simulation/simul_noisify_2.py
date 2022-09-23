"""
This is file contains a sample main function.
You can build your own, to simulate and test your data.

It is not a TEST file, it is a sample file to run the algorithm.
"""

import pdb
from typing import OrderedDict
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



def train(variables):
    training_element = TrainingElement(variables)
    """
    Skipt training with you have already trained otherwhise it will delete your trained and settings file,
    and train again.
    """
    tp = TrainingProcess(op_settings_file, op_training_file, training_element)
    print(f"Number of records from canonical data (pesquisadores unicos): NEED TO ACCESS canonical_d")

    sample_size = 1000
    step_time = datetime.now()
    tp.training(ip_canonical_file, ip_messy_training_file, ip_messy_validation_file, labeled_sample_size = 1000)
    end_time = datetime.now()
    print(f"Training Time: {end_time - step_time} \n")


def predict(noise):
    start_time = datetime.now()
    step_time = 0
    end_time = 0

    ### Prediction
    step_time = datetime.now()
    model_evaluation = ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
    noisify = Noisify(noise[0], noise[1])
    tt = TrainingTest(ip_canonical_file, ip_messy_test_file, op_settings_file, op_matches_found_file, model_evaluation, noisify)
    tt.noisify()
    tt.cluster_data()
    end_time = datetime.now()
    print(f"Prediction Time and File Recording Time: {end_time - step_time} \n")
    ###

    ### Performance of the algorithm
    step_time = datetime.now()
    tt.evaluate_model()
    end_time = datetime.now()
    print(f"Model Evaluation Time and Files Recording Time: {end_time - step_time} \n")
    ###

    print(f'Total Processing Time: {end_time - start_time}')




def build_variables():
    primeiro_nome = ['Exact', 'String']
    ultimo_sobrenome = ['Exact', 'String']
    return list(itertools.product(primeiro_nome, ultimo_sobrenome))

def build_noise():
    ruido = [1,2]
    abs_percent = [True, False]
    return list(itertools.product(ruido, abs_percent))

def build_simulation():
    simulations = []
    variables = build_variables()
    noises = build_noise()
    combs = len(variables) * len(noises)
    simul_num = 1

    for idx_var, variable in enumerate(variables):
        variables_desc = f" Training (Change Variables): \n\t Primeiro nome: {variable[0]} \n\t Último sobrenome: {variable[1]}"
        variables = [
                            {'field': 'nome', 'type': 'String'},
                            {'field': 'primeiro_nome', 'type': variable[0], 'has missing': True},
                            {'field': 'abr', 'type':'ShortString'},
                            {'field': 'ult_sobrenome', 'type': variable[1]},
        ]
        for idx_noise, noise in enumerate(noises):
            noise_desc = f" Prediction (Add Noise): \n\t Noise Level: {noise[0]} \n\t Abs_Percent: {noise[1]}"
            noise = (noise[0], noise[1])
            simulations.append({'simul_name': f'Simulation #{simul_num} of {combs}',
                                'training_id': f'{variable[0]} - {variable[1]}',
                                'training_descricao':variables_desc,
                                'variables':variables,
                                'predict_descricao':noise_desc,
                                'noise': noise})
            simul_num += 1

    return simulations





if __name__ == '__main__':
    simulations = build_simulation()

    trained_d = defaultdict(boolean)
    for simulation in simulations:
        print ('\n#############################################\n\n')

        if simulation['training_id'] not in trained_d:
            print(simulation['simul_name'])
            print('New Training')
            print(simulation['training_descricao'])
            print(simulation['predict_descricao'])
            train(simulation['variables'])
            print()
            trained_d[simulation['training_id']] = True
        else:
            print(simulation['simul_name'])
            print('Already Trained')
            print(simulation['training_descricao'])
            print(simulation['predict_descricao'])
            print()
        predict(simulation['noise'])

        print ('\n\n#############################################\n')


