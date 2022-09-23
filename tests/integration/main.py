"""
This is file contains a sample main function.
You can build your own, to simulate and test your data.
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



if __name__ == '__main__':

    ### Logging

    # Dedupe uses Python logging to show or suppress verbose output.
    # Added for convenience.
    # To enable verbose logging, run:
    # python [path_to]/dedupe_gazetteer_grupo_controle.py -v
    optp = optparse.OptionParser()
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help='Increase verbosity (specify multiple times for more)'
                    )
    (opts, args) = optp.parse_args()
    log_level = logging.WARNING
    if opts.verbose:
        if opts.verbose == 1:
            log_level = logging.INFO
        elif opts.verbose >= 2:
            log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)


    start_time = datetime.now()
    step_time = 0
    end_time = 0


    ### Training

    ## Variables Definition
    # Define the fields the gazetteer will pay attention to, by creating
    # a list of dictionaries describing the variables will be used for training a model.
    # Note that a variable definition describes the records that you want to match, and
    # it is a dictionary where the keys are the fields and the values are the field specification.
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
    step_time = datetime.now()
    tp.training(ip_canonical_file, ip_messy_training_file, ip_messy_validation_file, labeled_sample_size = 1000)
    end_time = datetime.now()
    print(f"Training Time: {end_time - step_time} \n")
    ###


    ### Prediction
    step_time = datetime.now()
    model_evaluation = ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
    tt = TrainingTest(ip_canonical_file, ip_messy_test_file, op_settings_file, op_matches_found_file, model_evaluation)
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
