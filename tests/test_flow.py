import pdb
from grupo_controle import dedupe_gazetteer_grupo_controle as gc
from grupo_controle import dedupe_gazetteer_utils as du


import unittest
import _io, os



################################################################################
# FILES

### Setup
ARQUIVOS_AUX_DIR = os.path.join(os.path.dirname(__file__),'../grupo_controle/arquivos/dados_auxiliares')
ARQUIVOS_ENTRADA_DIR = os.path.join(os.path.dirname(__file__),'../grupo_controle/arquivos/dados_entrada')
ARQUIVOS_TREINAMENTO_DIR = os.path.join(os.path.dirname(__file__),'../grupo_controle/arquivos/dados_treinamento')
ARQUIVOS_SAIDA_DIR = os.path.join(os.path.dirname(__file__),'../grupo_controle/arquivos/dados_saida')

# input files
pesquisadores_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_canonico_pesquisadores.csv')
autorias_treinamento_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_treinamento.csv')
autorias_validacao_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_validacao.csv')
autorias_teste_file = os.path.join(ARQUIVOS_ENTRADA_DIR,'cj_messy_autorias_para_teste.csv')

# output files
settings_file = os.path.join(ARQUIVOS_TREINAMENTO_DIR,'gazetteer_learned_settings')
training_file = os.path.join(ARQUIVOS_TREINAMENTO_DIR,'gazetteer_training.json')
output_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_matches_found.csv')

false_positives_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_false_positives.csv')
false_negatives_file = os.path.join(ARQUIVOS_SAIDA_DIR,'gazetteer_false_negatives.csv')

input_files = [pesquisadores_file,autorias_treinamento_file,\
                        autorias_validacao_file,autorias_teste_file]

################################################################################



class TestInitialData(unittest.TestCase):
    def test_files_exists(self):
        for file in input_files:
            res = du.chk_file_exists(file)
            self.assertIsInstance(res, _io.TextIOWrapper)
            if isinstance(res, _io.TextIOWrapper):
                res.close()


# Test TrainingProcess __init__ method
class TestTrainingProcess(unittest.TestCase):
    def test_init(self):
        training_process = gc.TrainingProcess(pesquisadores_file, settings_file, training_file)
        self.assertIsInstance(training_process, gc.TrainingProcess)



if __name__ == '__main__':
    unittest.main()