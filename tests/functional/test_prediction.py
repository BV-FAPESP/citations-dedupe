import pdb
from src import dedupe_gazetteer as dg
from src import dedupe_gazetteer_utils as du


import os
import unittest
import dedupe

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

    def step1_init_training_test(self):
        self.tt = dg.TrainingTest(ip_canonical_file, ip_messy_test_file, op_settings_file, op_matches_found_file, self.model_evaluation, self.noisify)
        self.assertIsInstance(self.tt, dg.TrainingTest)

    def step2_cluster_data(self):
        try:
            # Check this function separately.
            # It is from Dedupe library.
            gazetteer = dedupe.StaticGazetteer(open(self.tt.op_settings_file, 'rb'))
            self.assertIsInstance(gazetteer, dedupe.StaticGazetteer)
        except:
            raise
        else:
            self.tt.cluster_data()

    def step3_save_prediction_result(self):
        self.tt.save_prediction_result()

    def step4_evaluate_model(self):
        self.tt.evaluate_model()

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
