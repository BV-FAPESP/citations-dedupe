
"""

You can build your own, to simulate and test your data.

It is not a TEST file, it is a sample file to run the algorithm.
"""
import sys
new_path = r'/home/rmoriya/projetos/citations-dedupe/'
sys.path.append(new_path)

print(sys.path)
import pdb
#from typing import OrderedDict
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






def train(variables, noise):
    training_element = TrainingElement(variables)
    """
    Skipt training with you have already trained otherwhise it will delete your trained and settings file,
    and train again.
    """
    labeled_sample_size = 1000    
    tp = TrainingProcess(op_settings_file, op_training_file, training_element)    
    noisify = Noisify(noise[0], noise[1], noise[2])
    tp.training(ip_canonical_file, ip_messy_training_file, ip_messy_validation_file, labeled_sample_size, noisify)

def predict(noise):
    ### Prediction
    model_evaluation = ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
    noisify = Noisify(noise[0], noise[1], noise[2])
    tt = TrainingTest(ip_canonical_file, ip_messy_test_file, op_settings_file, op_matches_found_file, model_evaluation, noisify)
    tt.noisify()
    tt.cluster_data()    
    ###

    ### Performance of the algorithm
    step_time = datetime.now()
    tt.evaluate_model()
    cm = [[model_evaluation.qt_true_positives, model_evaluation.qt_false_negatives],
        [model_evaluation.qt_false_positives, model_evaluation.qt_true_negatives],
        ]

    # plot_confusion_matrix(cm, ['Positive', 'Negative'])
    ###




def build_variables():
    primeiro_nome = ['Exact', 'String']
    ultimo_sobrenome = ['Exact', 'String']
    # primeiro_nome = ['Exact']
    # ultimo_sobrenome = ['Exact']
    return list(itertools.product(primeiro_nome, ultimo_sobrenome))

def build_noise_train():
    ruido = [1,2,3]
    abs_percent = [False]
    data_noise_per = [0,50,100]
    return list(itertools.product(ruido, abs_percent, data_noise_per))

def build_noise_pred():
    ruido = [1,2,3]
    abs_percent = [False]
    data_noise_per = [0,5,10]
    return list(itertools.product(ruido, abs_percent, data_noise_per))

def build_simulation():
    simulations = []
    variables = build_variables()
    noises_pred = build_noise_pred()
    noises_train = build_noise_train()

    combs = len(variables) * len(noises_pred) * len(noises_train)

    simul_num = 1

    for idx_var, variable in enumerate(variables):
        variables_desc = f" Training (Change Variables): \n\t Primeiro nome: {variable[0]} \n\t Último sobrenome: {variable[1]}"
        variables = [
                            {'field': 'nome', 'type': 'String'},
                            {'field': 'primeiro_nome', 'type': variable[0], 'has missing': True},
                            {'field': 'abr', 'type':'ShortString'},
                            {'field': 'ult_sobrenome', 'type': variable[1]},
        ]        
        for idx_noise, noise_train_el in enumerate(noises_train):
                noise_train_desc = f" Training (Add Noise Train): \n\t Noise Level: {noise_train_el[0]} \n\t Abs_Percent: {noise_train_el[1]} \n\t Noise on data: {noise_train_el[2]}%"
                noise_train = (noise_train_el[0], noise_train_el[1], noise_train_el[2])

                for idx_noise, noise_pred_el in enumerate(noises_pred):
                    noise_pred_desc = f" Prediction (Add Noise Pred): \n\t Noise Level: {noise_pred_el[0]} \n\t Abs_Percent: {noise_pred_el[1]} \n\t Noise on data: {noise_pred_el[2]}%"
                    noise_pred = (noise_pred_el[0], noise_pred_el[1], noise_pred_el[2])
                    simulations.append({'simul_name': f'Simulation #{simul_num} of {combs}',
                                        'training_id': f'{variable[0]} - {variable[1]} - {noise_train_el[0]} - {noise_train_el[2]} ',

                                        'training_descricao':variables_desc,
                                        'noise_train_desc':noise_train_desc,
                                        'noise_pred_desc':noise_pred_desc,

                                        'variables':variables,
                                        'noise_train': noise_train,
                                        'noise_pred': noise_pred})
                    simul_num += 1
    return simulations


if __name__ == '__main__':
    simulations = build_simulation()
    trained_d = defaultdict(boolean)

    for simulation in simulations:
        if simulation['training_id'] not in trained_d:
            print ('\n\033[93m###################################################################################')
            print(simulation['simul_name'])            
            print('New Training')
            print(simulation['training_descricao'])
            print(simulation['noise_train_desc'])
            print(simulation['noise_pred_desc'])
            print ('###################################################################################')
            print('\033[97m')
            train(simulation['variables'], simulation['noise_train'])
            print()
            trained_d[simulation['training_id']] = True
        else:
            print ('\n\033[93m###################################################################################')
            print(simulation['simul_name'])
            print ('###################################################################################')
            print('Already Trained')
            print(simulation['training_descricao'])
            print(simulation['noise_train_desc'])
            print(simulation['noise_pred_desc'])
            print ('###################################################################################')
            print('\033[97m')
            print()
        predict(simulation['noise_pred'])
