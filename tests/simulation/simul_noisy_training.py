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



def train(variables, noise_train, save_train=False):
    training_element = TrainingElement(variables)

    """
    Skip training if you have already trained, otherwise
    it will delete your trained and settings files, and train again.
    """
    op_settings_filename = op_settings_file
    op_training_filename = op_training_file
    if save_train:
        noise_train_level = 'lt'+str(noise_train[0])+'-'+str(noise_train[2])
        op_settings_filename = f'{op_settings_file}_{noise_train_level}'
        op_training_filename = op_training_file.replace('.json',f'_{noise_train_level}.json')

    tp = TrainingProcess(op_settings_file=op_settings_filename,
                         op_training_file=op_training_filename,
                         training_element=training_element)
    start_time = datetime.now()
    labeled_sample_size = 1000
    noisify = Noisify(noise_train[0], noise_train[1], noise_train[2])
    tp.training(ip_canonical_file, ip_messy_training_file, ip_messy_validation_file, labeled_sample_size, noisify)
    end_time = datetime.now()
    print(f"Training Time: {end_time - start_time} \n")


def predict(noise_train,noise_pred,save_pred=False):
    start_time = datetime.now()

    op_settings_filename = op_settings_file
    op_false_positives_filename = op_false_positives_file
    op_false_negatives_filename = op_false_negatives_file
    op_matches_found_filename = op_matches_found_file
    if save_pred:
        noise_train_level = 'lt'+str(noise_train[0])+'-'+str(noise_train[2])
        noise_pred_level = 'lp'+str(noise_pred[0])+'-'+str(noise_pred[2])
        op_settings_filename = f'{op_settings_file}_{noise_train_level}'
        op_false_positives_filename = op_false_positives_file.replace('.csv',f'_{noise_train_level}_{noise_pred_level}.csv')
        op_false_negatives_filename = op_false_negatives_file.replace('.csv',f'_{noise_train_level}_{noise_pred_level}.csv')
        op_matches_found_filename = op_matches_found_file.replace('.csv',f'_{noise_train_level}_{noise_pred_level}.csv')

    ### Prediction
    model_evaluation = ModelEvaluation(ip_canonical_file,ip_messy_test_file,
                                       op_false_positives_filename, op_false_negatives_filename)

    noisify = Noisify(noise_pred[0], noise_pred[1], noise_pred[2])


    tt = TrainingTest(ip_canonical_file, ip_messy_test_file,
                      op_settings_filename, op_matches_found_filename,
                      model_evaluation, noisify)
    tt.noisify()
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

def build_variables():
    primeiro_nome = ['Exact', 'String']
    ultimo_sobrenome = ['Exact', 'String']

    variables = list(itertools.product(primeiro_nome, ultimo_sobrenome))
    variables_list = []
    for idx_var, variable in enumerate(variables):
        variables_dedupe = [
                            {'field': 'nome', 'type': 'String'},
                            {'field': 'nome', 'type': 'Text'},
                            {'field': 'primeiro_nome', 'type': variable[0], 'has missing': True},
                            {'field': 'abr', 'type':'ShortString'},
                            {'field': 'ult_sobrenome', 'type': variable[1]},
        ]
        variables_list.append((variable[0],variable[1],variables_dedupe))

    return variables_list

def build_noise(noise_level:list, abs_percent:list, data_noise_per:list):
    return list(itertools.product(noise_level, abs_percent,data_noise_per))

def build_noise_train():
    #noise_level = [1,2,3]
    abs_percent = [False]
    data_noise = { 1:[0,10,50,100],  # noise_level: data_noise_per
                   2:[0,10,50],
                   3:[0,10]
                  }
    noises = []
    for (level,data_per) in data_noise.items():
        noises += build_noise([level], abs_percent, data_per)

    return noises

def build_noise_pred():
    noise_level = [1,2,3]
    abs_percent = [False]
    data_noise_per =[0,5,10,20,40,60]

    return build_noise(noise_level, abs_percent, data_noise_per)


def build_simulation():
    simulations = []
    variables_list = build_variables()
    noises_pred = build_noise_pred()
    noises_train = build_noise_train()

    combs = len(variables_list) * len(noises_pred) * len(noises_train)

    simul_num = 1

    for idx_var, variable in enumerate(variables_list):
        variables_desc = f" Training (Change Variables): \n\t Primeiro nome: {variable[0]} \n\t Último sobrenome: {variable[1]}"
        variables_dedupe = variable[2]
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

                                        'variables':variables_dedupe,
                                        'noise_train': noise_train,
                                        'noise_pred': noise_pred})
                    simul_num += 1
    return simulations


if __name__ == '__main__':

    simulations = build_simulation()
    trained_d = defaultdict(boolean)
    save_op = False # Parameter to save output files

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
            train(simulation['variables'], simulation['noise_train'],save_train=save_op)
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
        predict(noise_train=simulation['noise_train'],noise_pred=simulation['noise_pred'], save_pred=save_op)
