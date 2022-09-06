import pdb
from src import dedupe_gazetteer as dg
from src import dedupe_gazetteer_utils as du


import os
import unittest
from datetime import datetime

from settings import *

class TestPredictionProcess(unittest.TestCase):
    def setUp(self) -> None:
        self.model_evaluation = dg.ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
        self.noisify = dg.Noisify(1, 1)
        return super().setUp()

    def test_noisify(self):
        noisify = dg.Noisify(1, 1)
        self.assertIsInstance(noisify, dg.Noisify)

    def test_training_test(self):
        tt = dg.TrainingTest(ip_canonical_file, ip_messy_test_file, op_settings_file, op_matches_found_file, self.model_evaluation, self.noisify)


    def test_prediction(self):
        ### Prediction
        step_time = datetime.now()
        model_evaluation = dg.ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
        tt = dg.TrainingTest(ip_canonical_file, ip_messy_test_file, op_settings_file, op_matches_found_file, model_evaluation)
        tt.cluster_data()
        end_time = datetime.now()
        print(f"Prediction Time and File Recording Time: {end_time - step_time} \n")
        ###

    def evaluate_model(self):
        ### Performance of the algorithm
        step_time = datetime.now()
        tt.evaluate_model()
        end_time = datetime.now()
        print(f"Model Evaluation Time and Files Recording Time: {end_time - step_time} \n")
        ###
