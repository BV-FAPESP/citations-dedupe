import pdb
from src.dedupe_gazetteer import *
from src.dedupe_gazetteer_utils import *


import logging
from datetime import datetime
import optparse
import _io, os
import unittest
import dedupe




################################################################################
### Setup
ARQUIVOS_AUX_DIR = os.path.join(os.environ['PYTHONPATH'],'arquivos/dados_auxiliares')
ARQUIVOS_ENTRADA_DIR = os.path.join(os.environ['PYTHONPATH'],'arquivos/dados_entrada')
ARQUIVOS_TREINAMENTO_DIR = os.path.join(os.environ['PYTHONPATH'],'arquivos/dados_treinamento')
ARQUIVOS_SAIDA_DIR = os.path.join(os.environ['PYTHONPATH'],'arquivos/dados_saida')

# input files
ip_canonical_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_canonico_pesquisadores.csv')
ip_messy_training_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_treinamento.csv')
ip_messy_validation_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_validacao.csv')
ip_messy_test_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_teste.csv')

# output files
op_settings_file = os.path.join(ARQUIVOS_TREINAMENTO_DIR,'gazetteer_learned_settings')
op_training_file = os.path.join(ARQUIVOS_TREINAMENTO_DIR,'gazetteer_training.json')
op_matches_found_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_matches_found.csv')
op_false_positives_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_false_positives.csv')
op_false_negatives_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_false_negatives.csv')

################################################################################



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

    ### Variables Definition
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

    training_element = TrainingElement(op_training_file, VARIABLES)

    """
    Skipt training with you have already trained otherwhise it will delete your trained and settings file,
    and train again.
    """
    tp = TrainingProcess(ip_canonical_file, op_settings_file, op_training_file, training_element)
    print(f"Number of records from canonical data (pesquisadores unicos): {len(tp.canonical_d)}")

    sample_size = 1000
    step_time = datetime.now()
    tp.training(ip_messy_training_file, ip_messy_validation_file, sample_size = 1000)
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