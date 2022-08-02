
import os, random, csv

from generic_utils import (getLongFirstName, getLastName, getPartialAbbreviation,
                            countRows, csvDictWriter, csvDictReaderGenerator)


class AutoriasComProjeto:
    """
    Class used to prepare input data for working with Dedupe
    """

    # Percent distribution to split the messy dataset
    training_per = 0.6  # 60% of input data for training
    validation_per = 0.2 # 20% of input data for evaluation during training
    # test_per = 0.2 # 20% of input data to test the model

    # field names for the new sets of FAPESP researchers and authors from WoS
    fieldnames = ['unique_id','link_id', 'art_id',
                  'pesq_id', 'nome', 'primeiro_nome', 'abr', 'ult_sobrenome', 'inst']

    def __init__(self, canonical_file, messy_file, training_file, validation_file,test_file):
        self.canonical_file = canonical_file
        self.messy_file = messy_file
        self.training_file = training_file
        self.validation_file = validation_file
        self.test_file = test_file


    def splitData(self, correlacao_file):
        """
        Read data from a CSV file (correlacao_file) and split the data into two sets:
        - a set of unique FAPESP researchers (canonical set), and
        - a set of authors from WoS (messy set).
        """

        with open(self.canonical_file, 'w', newline='') as researcher_f, \
            open(self.messy_file, 'w',newline='') as author_f:

            writer_r = csv.DictWriter(researcher_f, delimiter='|', fieldnames=self.fieldnames)
            writer_r.writeheader()
            writer_a = csv.DictWriter(author_f, delimiter='|', fieldnames=self.fieldnames)
            writer_a.writeheader()

            pesquisador_considerado_list = []
            reader = csvDictReaderGenerator(correlacao_file)
            for i, row in reader:
                link_id =  row['pesq_id'] # common key between researchers and article authors

                if row['pesq_id'] not in pesquisador_considerado_list:
                    writer_r.writerow({ self.fieldnames[0]: 'gcc'+str(i), \
                                        self.fieldnames[1]: link_id,\
                                        self.fieldnames[2]: '', \
                                        self.fieldnames[3]: row['pesq_id'],\
                                        self.fieldnames[4]: row['pesq_nome'],\
                                        self.fieldnames[5]: getLongFirstName(row['pesq_nome']),\
                                        self.fieldnames[6]: getPartialAbbreviation(row['pesq_nome']),\
                                        self.fieldnames[7]: getLastName(row['pesq_nome']),\
                                        self.fieldnames[8]: row['pesq_inst_sede']})
                    pesquisador_considerado_list.append(row['pesq_id'])

                writer_a.writerow({ self.fieldnames[0]: 'gcm'+str(i), \
                                    self.fieldnames[1]: link_id,\
                                    self.fieldnames[2]: row['art_id'],\
                                    self.fieldnames[3]: row['autor_id'],\
                                    self.fieldnames[4]: row['autor_nome'],\
                                    self.fieldnames[5]: getLongFirstName(row['autor_nome']),\
                                    self.fieldnames[6]: getPartialAbbreviation(row['autor_nome']),\
                                    self.fieldnames[7]: getLastName(row['autor_nome']),\
                                    self.fieldnames[8]: row['autor_inst']})

        # Split authors data for training, validation and test
        if os.path.exists(self.messy_file):
            print('Splitting the authorship dataset (messy set) ...')
            self.splitAuthorsData()


    def splitAuthorsData(self):
        """
        Read data from a CSV file (self.messy_file) and split the data into three sets:
        - one set for training,
        - one set for validation and
        - one set for testing.
        """

        n_data = countRows(self.messy_file)
        n_training_data = int(self.training_per * n_data)
        n_validation_data = int(self.validation_per * n_data)
        n_test_data = n_data - n_training_data - n_validation_data

        print(f'Number of lines (authors) = {n_data}')
        print(f'Training set size = {n_training_data}')
        print(f'Validation set size = {n_validation_data}')
        print(f'Test set size ={n_test_data} \n')


        ### computing data for training
        with open(self.messy_file) as f:
            reader = csv.DictReader(f, delimiter='|')
            fieldnames = reader.fieldnames
            data_list = [row for row in reader]

        random.seed(3)
        training_data = random.sample(data_list, n_training_data) # random subset

        # NOTA: No treinamento com o Dedupe, se faz uso do active learnig,
        # sendo possivel criar amostras rotuladas a partir de
        # dados messy e canonicos que contenham um id em comum (link_id).
        # Mas eh necessario que o messy data nao contenha
        # dados repetidos para evitar erros no processo de emparelhamento
        # para obter as amostras rotuladas.
        # Assim, a seguir o conjunto para treinamento eh reduzido,
        # escolhendo uma unica autoria por pesquisador
        common_key_list = []
        unique_list = []
        for item in training_data:
            common_key = item['link_id']
            if common_key not in common_key_list:
                common_key_list.append(common_key)
                unique_list.append(item)

        # training data sem link_id repetido
        csvDictWriter(self.training_file, fieldnames, unique_list)
        print(f"Number of samples for Training (single authors): {len(unique_list)} ({round(100*len(unique_list)/n_training_data,2)}% of {n_training_data})")

        ### data for validation process
        remaining_data = [row for row in data_list if row not in training_data]
        random.seed(4)
        validation_data = random.sample(remaining_data, n_validation_data) # random subset
        print(f'Number of samples for Validation: {len(validation_data)}')
        csvDictWriter(self.validation_file, fieldnames, validation_data)

        ### computing data for test
        test_data = [row for row in remaining_data if row not in validation_data]
        print(f'Number of samples for Test: {len(test_data)} \n')
        csvDictWriter(self.test_file, fieldnames, test_data)
