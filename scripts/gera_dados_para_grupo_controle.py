# -*- coding: utf-8 -*-

"""
This script generates the following four CSV files for
the tests with Dedupe and the control group:
- 'cj_canonico_pesquisadores.csv': Data file for the set of researchers
- 'cj_messy_autorias_para_treinamento.csv': Data file for training
- 'cj_messy_autorias_para_validacao.csv': Data file for validation to avoid the problem of overfitting in the training process
- 'cj_messy_autorias_para_teste.csv': Data file for testing the accuracy of the model generated
These files will be in 'arquivos/grupo_controle/dados_entrada'.

The data inside of these files are the input data to work with Dedupe
The following variables are related to the location of these files, as well as are defined in 'settings.py'.
- ip_canonical_file: For 'cj_canonico_pesquisadores.csv'
- ip_messy_training_file: For 'cj_messy_autorias_para_treinamento.csv'
- ip_messy_validation_file: For 'cj_messy_autorias_para_validacao.csv'
- ip_messy_test_file: For 'cj_messy_autorias_para_teste.csv'

NOTE: If you want to use our code with another dataset,
      you will need to provide
      the file containing the true matches for your dataset (variable 'ip_true_matches_file').

      In our case, this file is named 'true_matches_pesquisador_autoria.csv',
      and it is predetermined to be in 'arquivos/grupo_controle/dados_auxiliares'.
      This file contains the true matches between the sets of researchers and authorships.
      The following fields are considered in this file:
      art_id|pesq_id|pesq_nome|pesq_inst_sede|autor_id|autor_nome|autor_inst
      - art_id: Article id
      - pesq_id: Researcher id
      - pesq_nome: Researcher name
      - pesq_inst_sede: The institution that the researcher is affiliated
      - autor_id: Article author id
      - autor_nome: Article author-name
      - autor_inst: The institution that the article author is affiliated
"""

import os, sys, random, csv
import collections
from datetime import datetime

from src.generic_utils import (remover_acentos,getLongFirstName, getLastName, getPartialAbbreviation,
                            countRows, csvDictWriter, csvDictReaderGenerator)

from settings import *

##########################################################################################################
## Auxiliary files
# ip_true_matches_file has to contain the true matches between the sets of researchers and authorships
ip_true_matches_file =  os.path.join(ARQUIVOS_AUX_DIR,'true_matches_pesquisador_autoria.csv')
# op_messy_file is an output file with the complete authorship data, used only for reference
op_messy_file = os.path.join(ARQUIVOS_AUX_DIR,'cj_messy_autorias_completo.csv')
##########################################################################################################


class ControlSet:
    # Percent distribution to split the messy dataset
    training_per = 0.6  # 60% of input data for training
    validation_per = 0.2 # 20% of input data for evaluation during training
    # test_per = 0.2 # 20% of input data to test the model

    # field names for the new sets of FAPESP researchers and authors from WoS
    fieldnames = ['unique_id','link_id', 'art_id',
                  'pesq_id', 'nome', 'primeiro_nome',
                  'abr', 'ult_sobrenome', 'inst']

    def __init__(self, true_matches_file,
                 canonical_file = ip_canonical_file,
                 messy_file = op_messy_file,
                 training_file = ip_messy_training_file,
                 validation_file = ip_messy_validation_file,
                 test_file = ip_messy_test_file):
        self.true_matches_file = true_matches_file
        self.canonical_file = canonical_file
        self.messy_file = messy_file
        self.training_file = training_file
        self.validation_file = validation_file
        self.test_file = test_file
        self.canonical_size = 0
        self.messy_size = 0

    def preprocessing_data(self):
        """
        Preprocessing data
        """
        pesquisadores_d = collections.defaultdict(dict)
        autorias_d = collections.defaultdict(list)
        pesquisador_considerado_list = []
        reader = csvDictReaderGenerator(self.true_matches_file)
        pesq_ui = 0
        for i, row in reader:
            link_id =  row['pesq_id'] # common key between researchers and article authors

            if link_id not in pesquisador_considerado_list:
                pesquisador = {}
                pesquisador['unique_id'] = 'gcc'+str(pesq_ui)
                pesquisador['link_id'] = link_id
                pesquisador['art_id']  = ""
                pesquisador['pesq_id'] = row['pesq_id']
                pesquisador['nome']    = remover_acentos(row['pesq_nome'])
                pesquisador['primeiro_nome'] = getLongFirstName(row['pesq_nome'])
                pesquisador['abr'] = getPartialAbbreviation(row['pesq_nome'])
                pesquisador['ult_sobrenome'] = getLastName(row['pesq_nome'])
                pesquisador['inst']    = remover_acentos(row['pesq_inst_sede'])
                pesquisadores_d[link_id] = pesquisador
                pesquisador_considerado_list.append(link_id)
                pesq_ui += 1
                self.canonical_size += 1

            autoria = {}
            autoria['unique_id'] = 'gcm'+str(i)
            autoria['link_id']= link_id
            autoria['art_id'] = row['art_id']
            autoria['pesq_id']= row['autor_id']
            autoria['nome']   = remover_acentos(row['autor_nome'])
            autoria['primeiro_nome'] = getLongFirstName(row['autor_nome'])
            autoria['abr'] = getPartialAbbreviation(row['autor_nome'])
            autoria['ult_sobrenome'] = getLastName(row['autor_nome'])
            autoria['inst']   = remover_acentos(row['autor_inst'])

            if link_id not in autorias_d.keys():
                autorias_d[link_id]=[]

            autorias_d[link_id].append(autoria)
            self.messy_size += 1

        return (pesquisadores_d, autorias_d)

    def split_data(self):
        if not os.path.exists(self.true_matches_file):
            print(f'The file {self.true_matches_file} does not exist')
            return
        else:
            print('Getting data for training, validation and testing with Dedupe...')


        (pesquisadores_d, autorias_d) = self.preprocessing_data()

        print(f'Pesquisadores ={self.canonical_size}')
        print(f'Autorias ={self.messy_size}')

        self.save_canonical_set(pesquisadores_d)
        self.save_messy_set(autorias_d)

        data_size = self.canonical_size # number of entities
        training_data_size = int(self.training_per * data_size)
        validation_data_size = int(self.validation_per * data_size)
        test_data_size = data_size - training_data_size - validation_data_size

        print(f'Number of entities (researchers) = {data_size}')
        print(f'Number of entities for Training  = {training_data_size}')
        print(f'Number of entities for Validation = {validation_data_size}')
        print(f'Number of entities for Test = {test_data_size} \n')

        print('Splitting the canonical dataset ...')

        link_list = [link_id for link_id in pesquisadores_d.keys()]

        # link ids for the training process
        random.seed(3)
        training_links = random.sample(link_list, training_data_size) # random subset

        remaining_links = [link_id for link_id in link_list if link_id not in training_links]

        # link ids for the validation process
        random.seed(4)
        validation_links = random.sample(remaining_links, validation_data_size) # random subset

        # link ids for the test
        test_links = [link_id for link_id in remaining_links if link_id not in validation_links]

        # filter and save dataset for the training process
        training_set = Dataset('training')
        training_set.process_dataset(canonical_d=pesquisadores_d,messy_d=autorias_d,links=training_links)
        csvDictWriter(self.training_file, self.fieldnames, training_set.messy_set)
        # print('Number of researchers for training: ',training_set.canonical_size)
        print('Number of authorships for Training: ',training_set.messy_size)

        # filter and save dataset for the validation process
        validation_set = Dataset('validation')
        validation_set.process_dataset(canonical_d=pesquisadores_d,messy_d=autorias_d,links=validation_links)
        csvDictWriter(self.validation_file, self.fieldnames, validation_set.messy_set)
        print('Number of authorships for Validation: ', validation_set.messy_size)

        # filter and save dataset for the test
        test_set = Dataset('test')
        test_set.process_dataset(canonical_d=pesquisadores_d,messy_d=autorias_d,links=test_links)
        csvDictWriter(self.test_file, self.fieldnames, test_set.messy_set)
        print('Number of authorships for Testing: ',test_set.messy_size)

    def save_canonical_set(self, pesquisadores_d:dict):
        canonical_set = []
        for (link_id, pesquisador) in pesquisadores_d.items():
            canonical_set.append(pesquisador)

        csvDictWriter(self.canonical_file, self.fieldnames, canonical_set)


    def save_messy_set(self, autorias_d:dict):
        messy_set = []
        for (link_id, autorias) in autorias_d.items():
            for autoria in autorias:
                messy_set.append(autoria)

        csvDictWriter(self.messy_file, self.fieldnames, messy_set)


class Dataset:

    def __init__(self,type:str):
        self.canonical_set = []
        self.messy_set = []
        self.type = type
        self.canonical_size = 0
        self.messy_size = 0

    def process_dataset(self,canonical_d:dict, messy_d:dict, links:list):
        if self.type == 'training':
            self.process_training_dataset(canonical_d,messy_d, links)
        else:
            self.process_other_dataset(canonical_d,messy_d, links)

        self.canonical_size = len(self.canonical_set)
        self.messy_size = len(self.messy_set)

    def process_training_dataset(self, canonical_d, messy_d, links):
        # NOTE: In the training process with Dedupe,
        # it is possible to create labeled samples from the messy and canonical datasets,
        # which need to contain an ID in common (link_id).
        # However, to avoid any error in the correlation process that obtains
        # the set of labeled samples, we need to have a messy dataset that contains
        # only one authorship for a researcher in the canonical dataset.
        # Thus, the training set needs to contain only one authorship in the messy dataset
        # for a researcher in the canonical dataset.

        for link_id in links:
            researcher = canonical_d[link_id]
            # it chooses a random authorship for the researcher
            authorship_list = messy_d[link_id]
            random.seed(1)
            authorship = random.sample(authorship_list, 1)[0]
            #
            self.canonical_set.append(researcher)
            self.messy_set.append(authorship)


    def process_other_dataset(self, canonical_d, messy_d, links):

        authorship_list = []
        for link_id in links:
            authorship_list = messy_d[link_id]
            authors_name = []
            for authorship in authorship_list:
                author_name = authorship['nome']
                # it filters single author names for the researcher
                if author_name not in authors_name:
                    self.messy_set.append(authorship)
                    authors_name.append(author_name)




if __name__ == '__main__':


    start_time = 0
    end_time = 0


    start_time = datetime.now()
    cj_messy_autorias = ControlSet(ip_true_matches_file)
    cj_messy_autorias.split_data()
    end_time = datetime.now()
    print(f"Processing time: {end_time - start_time}")
