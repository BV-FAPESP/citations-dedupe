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
      In our case, this file contains the following fields:
      art_id|pesq_id|pesq_nome|pesq_inst_sede|autor_id|autor_nome|autor_inst
      - art_id: Article id
      - pesq_id: Researcher id
      - pesq_nome: Researcher name
      - pesq_inst_sede: The institution that the researcher is affiliated
      - autor_id: Article author id
      - autor_nome: Article author-name
      - autor_inst: The institution that the article author is affiliated
"""

import os, sys
#from os import path
#sys.path.append(path.join(path.dirname(__file__), '..'))


import random, csv
from generic_utils import (getLongFirstName, getLastName, getPartialAbbreviation,
                            countRows, csvDictWriter, csvDictReaderGenerator)

from datetime import datetime


######################################################################
ARQUIVOS_DIR = os.path.join(os.path.dirname(__file__),'arquivos','grupo_controle')
ARQUIVOS_AUX_DIR = os.path.join(ARQUIVOS_DIR,'dados_auxiliares')
ARQUIVOS_ENTRADA_DIR = os.path.join(ARQUIVOS_DIR,'dados_entrada')

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

class InputDataDedupeCG:
    """
    Class used to prepare input data for working with Dedupe
    and the group of control (GC)
    """

    # Percent distribution to split the messy dataset
    training_per = 0.6  # 60% of input data for training
    validation_per = 0.2 # 20% of input data for evaluation during training
    # test_per = 0.2 # 20% of input data to test the model

    # field names for the new sets of FAPESP researchers and authors from WoS
    fieldnames = ['unique_id','link_id', 'art_id',
                  'pesq_id', 'nome', 'primeiro_nome', 'abr', 'ult_sobrenome', 'inst']

    def __init__(self, canonical_file, messy_file, training_file, validation_file,test_file):
        self.canonical_file = canonical_file
        self.messy_file = messy_file
        self.training_file = training_file
        self.validation_file = validation_file
        self.test_file = test_file


    def splitData(self, correlacao_file):
        """
        Read data from a CSV file (correlacao_file) and split the data into two sets:
        - a set of unique FAPESP researchers (canonical set), and
        - a set of authors from WoS (messy set).
        """

        with open(self.canonical_file, 'w', newline='') as researcher_f, \
            open(self.messy_file, 'w',newline='') as author_f:

            writer_r = csv.DictWriter(researcher_f, delimiter='|', fieldnames=self.fieldnames)
            writer_r.writeheader()
            writer_a = csv.DictWriter(author_f, delimiter='|', fieldnames=self.fieldnames)
            writer_a.writeheader()

            pesquisador_considerado_list = []
            reader = csvDictReaderGenerator(correlacao_file)
            for i, row in reader:
                link_id =  row['pesq_id'] # common key between researchers and article authors

                if row['pesq_id'] not in pesquisador_considerado_list:
                    writer_r.writerow({ self.fieldnames[0]: 'gcc'+str(i), \
                                        self.fieldnames[1]: link_id,\
                                        self.fieldnames[2]: '', \
                                        self.fieldnames[3]: row['pesq_id'],\
                                        self.fieldnames[4]: row['pesq_nome'],\
                                        self.fieldnames[5]: getLongFirstName(row['pesq_nome']),\
                                        self.fieldnames[6]: getPartialAbbreviation(row['pesq_nome']),\
                                        self.fieldnames[7]: getLastName(row['pesq_nome']),\
                                        self.fieldnames[8]: row['pesq_inst_sede']})
                    pesquisador_considerado_list.append(row['pesq_id'])

                writer_a.writerow({ self.fieldnames[0]: 'gcm'+str(i), \
                                    self.fieldnames[1]: link_id,\
                                    self.fieldnames[2]: row['art_id'],\
                                    self.fieldnames[3]: row['autor_id'],\
                                    self.fieldnames[4]: row['autor_nome'],\
                                    self.fieldnames[5]: getLongFirstName(row['autor_nome']),\
                                    self.fieldnames[6]: getPartialAbbreviation(row['autor_nome']),\
                                    self.fieldnames[7]: getLastName(row['autor_nome']),\
                                    self.fieldnames[8]: row['autor_inst']})

        # Split authors data for training, validation and test
        if os.path.exists(self.messy_file):
            print('Splitting the authorship dataset (messy set) ...')
            self.splitAuthorsData()


    def splitAuthorsData(self):
        """
        Read data from a CSV file (self.messy_file) and split the data into three sets:
        - one set for training,
        - one set for validation and
        - one set for testing.
        """

        n_data = countRows(self.messy_file)
        n_training_data = int(self.training_per * n_data)
        n_validation_data = int(self.validation_per * n_data)
        n_test_data = n_data - n_training_data - n_validation_data

        print(f'Number of lines (authors) = {n_data}')
        print(f'Training set size = {n_training_data}')
        print(f'Validation set size = {n_validation_data}')
        print(f'Test set size ={n_test_data} \n')


        ### computing data for training
        with open(self.messy_file) as f:
            reader = csv.DictReader(f, delimiter='|')
            fieldnames = reader.fieldnames
            data_list = [row for row in reader]

        random.seed(3)
        training_data = random.sample(data_list, n_training_data) # random subset

        # NOTA: No treinamento com o Dedupe, se faz uso do active learnig,
        # sendo possivel criar amostras rotuladas a partir de
        # dados messy e canonicos que contenham um id em comum (link_id).
        # Mas eh necessario que o messy data nao contenha
        # dados repetidos para evitar erros no processo de emparelhamento
        # para obter as amostras rotuladas.
        # Assim, a seguir o conjunto para treinamento eh reduzido,
        # escolhendo uma unica autoria por pesquisador
        common_key_list = []
        unique_list = []
        for item in training_data:
            common_key = item['link_id']
            if common_key not in common_key_list:
                common_key_list.append(common_key)
                unique_list.append(item)

        # training data sem link_id repetido
        csvDictWriter(self.training_file, fieldnames, unique_list)
        print(f"Number of samples for Training (single authors): {len(unique_list)} ({round(100*len(unique_list)/n_training_data,2)}% of {n_training_data})")

        ### data for validation process
        remaining_data = [row for row in data_list if row not in training_data]
        random.seed(4)
        validation_data = random.sample(remaining_data, n_validation_data) # random subset
        print(f'Number of samples for Validation: {len(validation_data)}')
        csvDictWriter(self.validation_file, fieldnames, validation_data)

        ### computing data for test
        test_data = [row for row in remaining_data if row not in validation_data]
        print(f'Number of samples for Test: {len(test_data)} \n')
        csvDictWriter(self.test_file, fieldnames, test_data)






if __name__ == '__main__':


    start_time = 0
    end_time = 0


    if not os.path.exists(correlacao_file):
        print(f'The file {correlacao_file} does not exist')
    else:
        print('Getting data for training, validation and testing with Dedupe...')
        start_time = datetime.now()
        cj_messy_autorias = InputDataDedupeCG(unique_researcher_file, autorias_file, training_file, validation_file,test_file)
        cj_messy_autorias.splitData(correlacao_file)
        end_time = datetime.now()
        print(f"Processing time: {end_time - start_time}")
