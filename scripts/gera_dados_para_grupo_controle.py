# -*- coding: utf-8 -*-

"""
This script generates the following four CSV files for
the tests with Dedupe and the control group:
- 'cj_canonico_pesquisadores.csv'
- 'cj_messy_autorias_para_treinamento.csv'
- 'cj_messy_autorias_para_validacao.csv'
- 'cj_messy_autorias_para_teste.csv'

NOTE: If you want to use our code with another dataset,
      you will need to provide
      the file containing the true matches for your dataset (correlacao_file).

"""

import os, sys
from os import path
sys.path.append(path.join(path.dirname(__file__), '..'))


from src.classes_genericas import AutoriasComProjeto


from datetime import datetime


######################################################################
ARQUIVOS_AUX_DIR = os.path.join(os.environ['PYTHONPATH'], 'arquivos/dados_auxiliares')
ARQUIVOS_ENTRADA_DIR = os.path.join(os.environ['PYTHONPATH'], 'arquivos/dados_entrada')

## Input file
# Contains true matches between FAPESP researcher set and WoS author set
correlacao_file =  os.path.join(ARQUIVOS_AUX_DIR,'true_matches_pesquisador_autoria.csv')

## Auxiliary data output files
# File with authors' data
autorias_file = os.path.join(ARQUIVOS_AUX_DIR,'cj_messy_autorias_completo.csv')

## Output files. The data inside are the input data to work with Dedupe
# Data file of FAPESP researchers
unique_researcher_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_canonico_pesquisadores.csv')
# Data file for training
training_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_treinamento.csv')
# Data file for validation to avoid the problem of overfitting in the training process
validation_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_validacao.csv')
# Data file for test the accuracy of the model used with Dedupe
test_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_teste.csv')

######################################################################







if __name__ == '__main__':


    start_time = 0
    end_time = 0


    if not os.path.exists(correlacao_file):
        print(f'The file {correlacao_file} does not exist')
    else:
        print('Getting data for training, validation and testing with Dedupe...')
        start_time = datetime.now()
        cj_messy_autorias = AutoriasComProjeto(unique_researcher_file, autorias_file, training_file, validation_file,test_file)
        cj_messy_autorias.splitData(correlacao_file)
        end_time = datetime.now()
        print(f"Processing time: {end_time - start_time}")
