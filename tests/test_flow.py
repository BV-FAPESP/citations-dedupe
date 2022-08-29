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
INPUT_FILES = [ip_canonical_file, ip_messy_training_file,\
                        ip_messy_validation_file, ip_messy_test_file]
################################################################################



class TestInitialData(unittest.TestCase):
    def test_files_exists(self):
        """ Test if initial required files exists """
        for file in INPUT_FILES:
            res = du.chk_file_exists(file)
            self.assertIsInstance(res, _io.TextIOWrapper)
            if isinstance(res, _io.TextIOWrapper):
                res.close()

    def test_read_data2dict(self):
        """ Test readData function and assert result is dict"""
        for file in INPUT_FILES:
            res = du.readData(file)
            self.assertIsInstance(res, dict)


class TestTrainingProcess(unittest.TestCase):
    def test_init(self):
        """ Test TrainingProcess __init__ method """
        training_process = gc.TrainingProcess(ip_canonical_file, op_settings_file, op_training_file)
        self.assertIsInstance(training_process, gc.TrainingProcess)

    def test_get_training_data(self):
        """ Test getTrainingData function returns list """
        canonical_d = du.readData(ip_canonical_file)
        messy_training_d = du.readData(ip_messy_training_file)
        labeled_pair_groups_list = du.getTrainingData(messy_d=messy_training_d, canonical_d=canonical_d,  sample_size=1000)

        self.assertIsInstance(labeled_pair_groups_list, list)
        self.assertGreater(len(labeled_pair_groups_list), 0)
        self.assertIsInstance(labeled_pair_groups_list[0], tuple)
        self.assertGreater(len(labeled_pair_groups_list[0]), 0)
        self.assertIsInstance(labeled_pair_groups_list[0][0], dict)
        self.assertGreater(len(labeled_pair_groups_list[0][0]), 0)

        # import pdb; pdb.set_trace()


if __name__ == '__main__':
    unittest.main()
