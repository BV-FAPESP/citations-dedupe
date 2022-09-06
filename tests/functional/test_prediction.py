import pdb
from src import dedupe_gazetteer as dg
from src import dedupe_gazetteer_utils as du


import _io, os
import unittest
import dedupe


from settings import *

class TestModelEvaluation(unittest.TestCase):
    def test_init(self):
        """ Test ModelEvaluation __init__ method """
        model_evaluation = dg.ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
        self.assertIsInstance(model_evaluation, dg.ModelEvaluation)
