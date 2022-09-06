import os

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