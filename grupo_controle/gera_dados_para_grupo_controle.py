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

import os, sys, django, csv

from django.db.models import Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bv.settings")
django.setup()


from processamentos.machine_learning.dedupe_gazetteer_2.classes_genericas import (BaseArtigos,
                                                                                  CorrelacaoPesquisadorAutoriaComProcesso,
                                                                                  AutoriasComProjeto)

from datetime import datetime



######################################################################
ARQUIVOS_AUX_DIR = os.path.join(os.path.dirname(__file__),'arquivos/dados_auxiliares')
ARQUIVOS_ENTRADA_DIR = os.path.join(os.path.dirname(__file__),'arquivos/dados_entrada')

## Arquivos de saida de dados auxiliares
# Contem dados da correlacao entre pesquisador FAPESP e autor WoS
correlacao_file =  os.path.join(ARQUIVOS_AUX_DIR,'dados_pesquisador_autoria_com_projeto.csv')
# arquivo com autores de artigo
autorias_file = os.path.join(ARQUIVOS_AUX_DIR,'cj_messy_autorias_completo.csv')

## Arquivos de saida de dados que serao usados com o Dedupe
# arquivo com pesquisadores unicos FAPESP
unique_researcher_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_canonico_pesquisadores.csv')
# arquivo com autorias de artigo para treinamento
training_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_treinamento.csv')
# arquivo com autorias de artigos para evitar o problema de overfitting no processo de treinamento,
validation_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_validacao.csv')
# arquivo com autorias de artigos para testar a acuracia do dedupe
test_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_teste.csv')

######################################################################







if __name__ == '__main__':

    #procedencia_d = {'wos':1,'scielo':3}
    start_time = 0
    end_time = 0

    start_time = datetime.now()

    if not os.path.exists(correlacao_file):
        print('\n================================================================')
        print('Obtendo correlacoes de pesquisadores e autorias com processo...')
        base_wos = BaseArtigos(procedencia_id=1)
        artigos_wos = base_wos.get_artigos_comProcesso()
        print(f"Quantidade de artigos com processo, encontrados: {base_wos.qt_art_encontrados}" )

        correlacao = CorrelacaoPesquisadorAutoriaComProcesso()
        pesquisador_autoria_list = correlacao.get_correlacoes_pesquisador_autoria(artigos_wos)
        correlacao.grava_correlacoes(correlacao_file, pesquisador_autoria_list)

        print(f"Quantidade de artigos com pesquisadores identificados = {correlacao.qt_art_identificados}")
        print(f"Quantidade de pesquisadores identificados = {correlacao.qt_pesq_identificados}")

        end_time = datetime.now()
        print(f"Tempo de processamento: {end_time - start_time}")


    print('\n================================================================')
    print('Obtendo dados para treinamento-validacao e teste com o dedupe')

    start_time = datetime.now()
    cj_messy_autorias = AutoriasComProjeto(unique_researcher_file, autorias_file, training_file, validation_file,test_file)
    cj_messy_autorias.splitData(correlacao_file)
    end_time = datetime.now()

    print(f"Tempo de processamento: {end_time - start_time}")
