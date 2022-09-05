import pdb
from src import dedupe_gazetteer as gc
from src import dedupe_gazetteer_utils as du


import _io, os
import unittest
import dedupe

################################################################################
# FILES
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
    def setUp(self):
        VARIABLES = [
                        {'field': 'nome', 'type': 'String'},
                        {'field': 'nome', 'type': 'Text'},
                        {'field': 'primeiro_nome', 'type':'Exact', 'has missing': True},
                        {'field': 'abr', 'type':'ShortString'},
                        {'field': 'ult_sobrenome', 'type': 'Exact'}
                    ]
        self.training_element = gc.TrainingElement(op_training_file, VARIABLES)

    def test_init(self):
        """ Test TrainingProcess __init__ method """
        training_process = gc.TrainingProcess(ip_canonical_file, op_settings_file, op_training_file, training_element = self.training_element)
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




class TestTrainingElement(unittest.TestCase):
    """
    Execute tests in order
    https://stackoverflow.com/questions/5387299/python-unittest-testcase-execution-order
    """
    def setUp(self):
        """ Test TrainingElement __init__ method """
        VARIABLES = [
                        {'field': 'nome', 'type': 'String'},
                        {'field': 'nome', 'type': 'Text'},
                        {'field': 'primeiro_nome', 'type':'Exact', 'has missing': True},
                        {'field': 'abr', 'type':'ShortString'},
                        {'field': 'ult_sobrenome', 'type': 'Exact'}
                    ]
        self.training_element = gc.TrainingElement(op_training_file, VARIABLES)
        self.canonical_d = du.readData(ip_canonical_file)
        self.messy_training_d = du.readData(ip_messy_training_file)
        self.sample_size = 1000



    def _chk_labeled_pair_groups_list(self, lot):
        for i in range(len(list(lot[0].keys()))):
            self.assertEqual(lot[0][list(lot[0].keys())[i]]['link_id'], lot[1][list(lot[1].keys())[i]]['link_id'])
        return True


    def _chk_labeled_pairs(self, lp):
        try:
            for i in range(len(lp)):
                self.assertEqual(lp[i][0]['link_id'], lp[i][1]['link_id'])
            return True
        except:
            return False


    def step1_get_training_data(self):
        labeled_pair_groups_list = du.getTrainingData(messy_d=self.messy_training_d, canonical_d=self.canonical_d,  sample_size=self.sample_size)
        (self.labeled_messy_d, self.labeled_canonical_d) = labeled_pair_groups_list[0]

        self.assertIsInstance(labeled_pair_groups_list, list)
        self.assertEqual(len(self.labeled_messy_d), self.sample_size)
        self.assertEqual(len(self.labeled_canonical_d), self.sample_size)

        print ('\n\nGET TRAINING DATA')
        print('Split dataset into chunks to train and validate')
        print(f'* Number of labeled_pair_groups_list (to iterate training): {len(labeled_pair_groups_list)}')
        print(f'* Len labeled_messy_d: {len(self.labeled_messy_d)}')
        print(f'* Len labeled_canonical_d: {len(self.labeled_canonical_d)}')

        if self._chk_labeled_pair_groups_list(labeled_pair_groups_list[0]):
            print('* All trained data pairs of a chunck are equal (link_id).  Example:')
        messy_d_key0 = list(self.labeled_messy_d.keys())[0]
        canonical_d_key0 = list(self.labeled_canonical_d.keys())[0]
        print(f'Messy: {self.labeled_messy_d[messy_d_key0]}')
        print(f'Canonical: {self.labeled_canonical_d[canonical_d_key0]}')


    def step2_prepare_training(self):
        print('\n\nFrom now on the process runs in iterations to train and validate the model, \n \
            up untill the model is good enough (Dice Coefficient).\n \
            Each iteration runs over a chunk of data.')

        print('\n\nPREPARE TRAINING')
        self.assertIsNone( self.training_element.prepare_training(self.labeled_messy_d, self.labeled_canonical_d, sample_size=150000) )
        print('Required Prepare Training done')

    def step3_active_labeling(self):
        print('\n\nACTIVE LABELING')
        print('Mark pairs of matchs and distinct (messy x canonical)')
        n_distinct_pairs = len(self.labeled_messy_d)
        labeled_pairs = dedupe.training_data_link(self.labeled_messy_d, self.labeled_canonical_d, 'link_id', training_size=n_distinct_pairs)

        self.assertGreater(len(labeled_pairs['match']), 0)
        self.assertGreater(len(labeled_pairs['distinct']), 0)

        self.assertIsInstance(labeled_pairs['match'][0], tuple)
        self.assertIsInstance(labeled_pairs['match'][0][0], dict)
        self.assertIsInstance(labeled_pairs['match'][0][1], dict)

        self.assertIsInstance(labeled_pairs['distinct'][0], tuple)
        self.assertIsInstance(labeled_pairs['distinct'][0][0], dict)
        self.assertIsInstance(labeled_pairs['distinct'][0][1], dict)

        self.training_element.gazetteer.mark_pairs(labeled_pairs)
        self.training_element.gazetteer.train()

        print(f'* Len labeled_pairs match: {len(labeled_pairs["match"])}')
        print(f'* Len labeled_pairs distinct: {len(labeled_pairs["distinct"])}')

        if self._chk_labeled_pairs(labeled_pairs['match']):
            print('* All pairs of matches are equal. Example:')
            print (f'Messy: {labeled_pairs["match"][0][0]}')
            print (f'Canonical: {labeled_pairs["match"][0][1]}')

        if not self._chk_labeled_pairs(labeled_pairs['distinct']):
            print('* All pairs of distinct are different. Example:')
            print (f'Messy: {labeled_pairs["distinct"][0][0]}')
            print (f'Canonical: {labeled_pairs["distinct"][0][1]}')

    def step4_write_training(self):
        print('\n\nWRITE TRAINING')
        self.training_element.write_training()
        print(f'Training file has been writen: {op_training_file}')

    def _steps(self):
        for name in dir(self): # dir() result is implicitly sorted
            if name.startswith("step"):
                yield name, getattr(self, name)

    def test_steps(self):
        for name, step in self._steps():
            try:
                step()
            except Exception as e:
                self.fail("{} failed ({}: {})".format(step, type(e), e))




if __name__ == '__main__':
    unittest.main()
