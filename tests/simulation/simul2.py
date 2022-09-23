import pdb
from typing import OrderedDict
from src.dedupe_gazetteer import *
from src.dedupe_gazetteer_utils import *

from datetime import datetime
from settings import *



def train(variables):
    training_element = TrainingElement(variables)
    tp = TrainingProcess(op_settings_file, op_training_file, training_element)
    tp.training(ip_canonical_file, ip_messy_training_file, ip_messy_validation_file, sample_size = 1000)
    end_time = datetime.now()


def predict():
    model_evaluation = ModelEvaluation(ip_canonical_file, ip_messy_test_file, op_false_positives_file, op_false_negatives_file)
    tt = TrainingTest(ip_canonical_file, ip_messy_test_file, op_settings_file, op_matches_found_file, model_evaluation)
    tt.cluster_data()
    tt.evaluate_model()


if __name__ == '__main__':

    variables = [{'name': 'VARIABLES 1',
                    'description': 'Description of variables 1',
                    'variables':
                    [
                        {'field': 'nome', 'type': 'String'},
                        {'field': 'primeiro_nome', 'type': 'Exact', 'has missing': True},
                        {'field': 'abr', 'type':'ShortString'},
                        {'field': 'ult_sobrenome', 'type': 'Exact'},
                    ]

                    },
                    {'name': 'VARIABLES 2',
                    'description': 'Description of variables 2',
                    'variables':
                            [
                                {'field': 'nome', 'type': 'Text'},
                                {'field': 'primeiro_nome', 'type': 'String', 'has missing': True},
                                {'field': 'abr', 'type':'ShortString'},
                                {'field': 'ult_sobrenome', 'type': 'Exact'}
                            ]
                    }
                ]

    noises = [{'name': 'NOISE 1',
                    'description': 'Description of noise 1'
                },
                {'name': 'NOISE 2',
                    'description': 'Description of noise 2'
                }
            ]



    for variable in variables:
        print ('\n---------------------------------------------')
        print(variable['name'])
        print(variable['description'])
        print ('---------------------------------------------\n')
        train(variable['variables'])

        for noise in noises:
            print ('\n---------------------------------------------')
            print (noise['name'])
            print (noise['description'])
            print ('---------------------------------------------\n')
            predict()

        print ('\n#############################################\n')
