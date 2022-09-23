"""
This is file contains a sample main function.
You can build your own, to simulate and test your data.

It is not a TEST file, it is a sample file to run the algorithm.
"""

import pdb
from src.dedupe_gazetteer import *
from src.dedupe_gazetteer_utils import *


import logging
from datetime import datetime
import optparse
import _io, os
import unittest
import dedupe

from settings import *





def run(variables):

    start_time = datetime.now()
    step_time = 0
    end_time = 0

    #training_element = TrainingElement(op_training_file, variables)

    """
    Skipt training with you have already trained otherwhise it will delete your trained and settings file,
    and train again.
    """
    #tp = TrainingProcess(ip_canonical_file, op_settings_file, op_training_file, training_element)
    #print(f"Number of records from canonical data (pesquisadores unicos): {len(tp.canonical_d)}")

    #sample_size = 1000
    #step_time = datetime.now()
    #tp.training(ip_messy_training_file, ip_messy_validation_file, sample_size = 1000)
    #end_time = datetime.now()
    #print(f"Training Time: {end_time - step_time} \n")
    ###


    ### Prediction
    step_time = datetime.now()
    model_evaluation = ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
    noisify = Noisify(1, False)
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



### Variables Definition
# Define the fields the gazetteer will pay attention to, by creating
# a list of dictionaries describing the variables will be used for training a model.
# Note that a variable definition describes the records that you want to match, and
# it is a dictionary where the keys are the fields and the values are the field specification.

if __name__ == '__main__':

    simulations = [{'name': 'SIMULATION 1',
                    'description': 'Description of simulation 1',
                    'variables':
                    [
                        {'field': 'nome', 'type': 'String'},
                        {'field': 'primeiro_nome', 'type': 'Exact', 'has missing': True},
                        {'field': 'abr', 'type':'ShortString'},
                        {'field': 'ult_sobrenome', 'type': 'Exact'},
                    ]

                    },
                    {'name': 'SIMULATION 2',
                    'description': 'Description of simulation 2',
                    'variables':
                            [
                                {'field': 'nome', 'type': 'Text'},
                                {'field': 'primeiro_nome', 'type': 'String', 'has missing': True},
                                {'field': 'abr', 'type':'ShortString'},
                                {'field': 'ult_sobrenome', 'type': 'Exact'}
                            ]
                    }
                ]

    for simulation in simulations:
        print ('\n#############################################')
        print(simulation['name'])
        print(simulation['description'])
        run(simulation['variables'])
        print ('#############################################\n')
