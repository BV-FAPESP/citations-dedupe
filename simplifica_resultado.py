"""
This code reduces the number of columns of the output files obtained from
running dedupe_gazetteer.py, to view the results more clearly.

The field names in these files are:
- cluster_id (to save)
- link_score (to save)
- source_file
- record_id
- unique_id
- link_id (to save)
- art_id (to save)
- pesq_id (to save)
- nome (to save)
- primeiro_nome
- abr
- ult_sobrenome
- inst (to save)
"""

import os,sys,csv
import collections

from datetime import datetime


ARQUIVOS_DIR = os.path.join(os.path.dirname(__file__),'arquivos')
ARQUIVOS_GC_DIR = os.path.join(ARQUIVOS_DIR,'grupo_controle')
ARQUIVOS_GA_DIR = os.path.join(ARQUIVOS_DIR,'grupo_aplicacao')

ARQUIVOS_SAIDA_GC = os.path.join(ARQUIVOS_GC_DIR,'dados_saida')
ARQUIVOS_SAIDA_GA = os.path.join(ARQUIVOS_GA_DIR,'dados_saida')

## Grupo Controle
# input files
output_dedupe_file = os.path.join(ARQUIVOS_SAIDA_GC,'gazetteer_matches_found.csv')
false_positives_file = os.path.join(ARQUIVOS_SAIDA_GC,'gazetteer_false_positives.csv')
false_negatives_file = os.path.join(ARQUIVOS_SAIDA_GC,'gazetteer_false_negatives.csv')
# output files
simple_output_dedupe_file = os.path.join(ARQUIVOS_SAIDA_GC,'gazetteer_matches_found_simplified.csv')
simple_false_positives_file = os.path.join(ARQUIVOS_SAIDA_GC,'gazetteer_false_positives_simplified.csv')
simple_false_negatives_file = os.path.join(ARQUIVOS_SAIDA_GC,'gazetteer_false_negatives_simplified.csv')

## Grupo Aplicacao
# input file
ga_output_dedupe_file = os.path.join(ARQUIVOS_SAIDA_GA,'gazetteer_matches_found.csv')
# output file
ga_simple_output_dedupe_file = os.path.join(ARQUIVOS_SAIDA_GA,'gazetteer_matches_found_simplified.csv')


def simplify_save_result(input_file, output_file):

    print(f"Simplify results from {input_file}")

    with open(output_file, 'w', newline='') as f:
        fieldnames = ['cluster_id','link_score', 'link_id', 'art_id', 'pesq_id', 'nome','inst']
        writer = csv.DictWriter(f, delimiter='|', fieldnames=fieldnames)
        writer.writeheader()

        with open(input_file, newline='') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                writer.writerow({ 'cluster_id': row['cluster_id'],\
                                  'link_score': row['link_score'],\
                                  'link_id': row['link_id'],\
                                  'art_id': row['art_id'],\
                                  'pesq_id': row['pesq_id'],\
                                  'nome': row['nome'],\
                                  'inst': row['inst']
                              })




if __name__ == '__main__':


    start_time = 0
    end_time = 0

    if 'controle' in sys.argv:
        start_time = datetime.now()
        simplify_save_result(output_dedupe_file, simple_output_dedupe_file)
        simplify_save_result(false_positives_file, simple_false_positives_file)
        simplify_save_result(false_negatives_file, simple_false_negatives_file)
        end_time = datetime.now()
        print(f"Processing time: {end_time - start_time}")

    elif 'aplicacao' in sys.argv:
        start_time = datetime.now()
        simplify_save_result(ga_output_dedupe_file, ga_simple_output_dedupe_file)
        end_time = datetime.now()
        print(f"Processing time: {end_time - start_time}")
