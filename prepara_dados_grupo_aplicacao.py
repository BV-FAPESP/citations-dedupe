# -*- coding: utf-8 -*-
"""
This script preprocesses the input data to work with Dedupe.

Input files:
- pesquisadores_fapesp.csv: it has the fields pesq_id, pesq_nome, pesq_inst
- autorias_sem_processo.csv: it has the fields art_id, pesq_id, pesq_nome, pesq_inst

Output files:
- cj_canonico_pesquisadores.csv
- cj_messy_autorias.csv

__NOTE: Output files have the same structure
"""

import os, sys

from generic_utils import (remover_acentos,
                           getLongFirstName, getLastName,
                           getPartialAbbreviation,
                           csvDictReaderGenerator, csvDictWriter)

from datetime import datetime

################################################################################
def save_preprocessing(data_list, output_file):
    fieldnames = ['unique_id','link_id', 'art_id', 'pesq_id', 'nome', 'primeiro_nome','abr','ult_sobrenome', 'inst']
    csvDictWriter(output_file, fieldnames, data_list)

def preprocessing_canonical_data(input_file,output_file):
    pesquisadores_list = []
    reader = csvDictReaderGenerator(input_file)
    for idx_row, row in reader:
        full_name = remover_acentos(row['pesq_nome'])
        first_name = getLongFirstName(full_name)
        name_abbr = getPartialAbbreviation(full_name)
        last_surname = getLastName(full_name)
        inst_sede = remover_acentos(row['pesq_inst'])

        pesquisador_dict = {}
        pesquisador_dict['unique_id'] = 'gac'+ str(idx_row)
        pesquisador_dict['link_id'] = row['pesq_id']
        pesquisador_dict['art_id'] = ""
        pesquisador_dict['pesq_id'] = row['pesq_id']
        pesquisador_dict['nome'] = full_name
        pesquisador_dict['primeiro_nome'] = first_name
        pesquisador_dict['abr'] = name_abbr
        pesquisador_dict['ult_sobrenome'] = last_surname
        pesquisador_dict['inst'] = inst_sede

        pesquisadores_list.append(pesquisador_dict)

    if pesquisadores_list:
        save_preprocessing(pesquisadores_list,output_file)
        print(f'Number of researchers recorded: {len(pesquisadores_list)}')


def preprocessing_messy_data(input_file,output_file):
    autorias_list = []
    reader = csvDictReaderGenerator(input_file)
    for idx_row, row in reader:
        full_name = remover_acentos(row['pesq_nome'])
        first_name = getLongFirstName(full_name)
        name_abbr = getPartialAbbreviation(full_name)
        last_surname = getLastName(full_name)
        inst_sede = remover_acentos(row['pesq_inst'])

        autoria_d = {}
        autoria_d['unique_id'] = 'gam'+ str(idx_row)
        autoria_d['link_id'] = row['pesq_id']
        autoria_d['art_id'] = row['art_id']
        autoria_d['pesq_id'] = row['pesq_id']
        autoria_d['nome'] = full_name
        autoria_d['primeiro_nome'] = first_name
        autoria_d['abr'] = name_abbr
        autoria_d['ult_sobrenome'] = last_surname
        autoria_d['inst'] = inst_sede

        autorias_list.append(autoria_d)

    if autorias_list:
        save_preprocessing(autorias_list,output_file)
        print(f'Number of authorships recorded: {len(autorias_list)}')


################################################################################
ARQUIVOS_DIR = os.path.join(os.path.dirname(__file__),'arquivos','grupo_aplicacao')
ARQUIVOS_AUX_DIR = os.path.join(ARQUIVOS_DIR,'dados_auxiliares')
ARQUIVOS_ENT_DIR = os.path.join(ARQUIVOS_DIR,'dados_entrada')

# Input files
pesquisadores_file = os.path.join(ARQUIVOS_AUX_DIR, 'pesquisadores_fapesp.csv')
autorias_file = os.path.join(ARQUIVOS_AUX_DIR, 'autorias_sem_processo.csv')

# Output files
canonical_file = os.path.join(ARQUIVOS_ENT_DIR, 'cj_canonico_pesquisadores.csv')
messy_file = os.path.join(ARQUIVOS_ENT_DIR, 'cj_messy_autorias.csv')
################################################################################


if __name__ == '__main__':
    start_time = 0
    end_time = 0

    start_time = datetime.now()
    preprocessing_canonical_data(input_file=pesquisadores_file, output_file=canonical_file)
    preprocessing_messy_data(input_file=autorias_file, output_file=messy_file)
    end_time = datetime.now()

    print(f"Processing time: {end_time - start_time}")
