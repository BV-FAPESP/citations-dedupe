"""
This code reduces the number of columns of the output files obtained from
running dedupe_gazetteer_grupo_controle.py,
to view the results more clearly.

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

import os,csv
import collections

from datetime import datetime


ARQUIVOS_SAIDA_DIR = os.path.join(os.environ['PYTHONPATH'], 'arquivos/dados_saida')

# input files
output_dedupe_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_matches_found.csv')
false_positives_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_false_positives.csv')
false_negatives_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_false_negatives.csv')

# output files
simple_output_dedupe_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_matches_found_simplified.csv')
simple_false_positives_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_false_positives_simplified.csv')
simple_false_negatives_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_false_negatives_simplified.csv')


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

    start_time = datetime.now()
    simplify_save_result(output_dedupe_file, simple_output_dedupe_file)
    simplify_save_result(false_positives_file, simple_false_positives_file)
    simplify_save_result(false_negatives_file, simple_false_negatives_file)
    end_time = datetime.now()
    print(f"Tempo de Processamento: {end_time - start_time}")
