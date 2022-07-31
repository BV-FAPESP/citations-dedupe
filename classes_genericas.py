"""

Este script contém duas classes:
- BaseArtigos: Usada para pegar os dados de artigos armazenados no banco da BV
- AutoriasComProjeto: Usada para preparar os dados de entrada para trabalhar com o Dedupe

"""

import os, random, csv
from django.db.models import Count


from memoria.models import Documento, Titulo

from processamentos.machine_learning.dedupe_gazetteer_2.generic_utils import (remover_acentos, isSimilarByName,
                                                                            getLongFirstName, getLastName, getPartialAbbreviation,
                                                                            countRows, csvDictWriter, csvDictReaderGenerator)

class BaseArtigos(object):
    """docstring for BaseArtigos."""

    def __init__(self, procedencia_id:int):
        super(BaseArtigos, self).__init__()
        self.procedencia_id = procedencia_id
        self.tipo_publicacao_id = 36
        self.qt_art_encontrados = 0

    def get_artigos_comProcesso(self):

        artigos = self.get_artigos()
        artigos = artigos.exclude(processos='')

        artigos_filtrados = self.filtra_artigos(artigos)
        self.qt_art_encontrados = artigos_filtrados.count()

        return artigos_filtrados


    def get_artigos_semProcesso(self):
        artigos = self.get_artigos()
        artigos = artigos.filter(processos='')

        artigos_filtrados = self.filtra_artigos(artigos)
        n_artigos = artigos_filtrados.count()

        print(f"Numero de artigos sem processo, encontrados: {n_artigos}" )
        return artigos_filtrados

    def get_artigos(self):
        artigos = []
        if self.procedencia_id == 1:
            artigos = self.get_artigosWoS()
        elif self.procedencia_id == 3:
            artigos = self.get_artigosScielo()

        return artigos

    def get_artigosWoS(self):
        # O campo notas, parece que foi preenchido a mao, e de alguma maneira associa manualmente o
        # artigo ao processo.
        # Se for isso, gera um enorme desvio se nao houver correlacao entre autor e pesquisador
        # como parece ser o caso de alguns artigos com nota.
        artigos = Documento.objects.filter(procedencia_id=self.procedencia_id,tipo_publicacao_id=self.tipo_publicacao_id, notas='')
        artigos = artigos.exclude(uid_wos='').order_by('id')

        return artigos

    def get_artigosScielo(self):
        # O campo notas, parece que foi preenchido a mao, e de alguma maneira associa manualmente o
        # artigo ao processo.
        # Se for isso, gera um enorme desvio se nao houver correlacao entre autor e pesquisador
        # como parece ser o caso de alguns artigos com nota.
        artigos = Documento.objects.filter(procedencia_id=self.procedencia_id,tipo_publicacao_id=self.tipo_publicacao_id, notas='')
        artigos = artigos.exclude(ur_scielo='').order_by('id')

        return artigos

    def filtra_artigos(self, artigos):

        artigos = artigos.exclude(doi='').exclude(autoria='').order_by('id')

        # artigos com doi repetido
        dupes = artigos.values('doi').annotate(Count('id')).order_by().filter(id__count__gt=1)
        # id de artigos com titulo em branco
        titulo_em_branco = Titulo.objects.filter(titulo='').values('documento_id')

        # excluindo artigos com doi repetido, devido a possiveis casos de ambiguidade de autoria
        artigos = artigos.exclude(doi__in=[item['doi'] for item in dupes])
        # excluindo artigos com titulo em branco e sem titulo associado
        artigos = artigos.exclude(id__in=[item['documento_id'] for item in titulo_em_branco]).exclude(titulo=None)

        return artigos



class CorrelacaoPesquisadorAutoriaComProcesso:

    qt_pesq_identificados = 0
    qt_art_identificados = 0
    fieldnames = [ 'art_id',
                   'pesq_id', 'pesq_nome', 'pesq_inst_sede',
                   'autor_id', 'autor_nome', 'autor_inst']

    def pega_instituicao_sede_processo(self, processo):
        instituicao_sede = ''

        try:
            if processo.pega_instituicao_sede():
                instituicao_sede = processo.pega_instituicao_sede().__str__()
            elif processo.pega_empresas():
                instituicao_sede = processo.pega_empresas()[0].empresa.razao_social

            instituicao_sede = remover_acentos(instituicao_sede)

        except Exception as e:
            print(e)
            print(processo.instituicao_sede)
            pass

        return instituicao_sede

    def pega_pesquisadores_processos(self, processos_artigo):
        # Pega os processos do artigo e armazena os dados dos pesquisadores
        # processos_artigo: sao instancias de projetos e/ou bolsas


        pesquisadores_list = []
        pesquisador_considerado = []

        for proc in processos_artigo:

            inst_sede = self.pega_instituicao_sede_processo(proc)
            if not inst_sede:
                continue

            id_pesquisador_b = proc.beneficiario_cpd.id
            id_pesquisador_r = proc.responsavel_cpd.id

            if not id_pesquisador_b in pesquisador_considerado:
                pesquisador_b = {}
                pesquisador_b['id'] = id_pesquisador_b
                pesquisador_b['nome_completo'] = remover_acentos(proc.beneficiario_cpd.nome_cpd)
                pesquisador_b['sobrenome'] = remover_acentos(proc.beneficiario_cpd.nome_cpd.split(' ')[-1])
                pesquisador_b['inst_sede'] = inst_sede
                pesquisadores_list.append(pesquisador_b)
                pesquisador_considerado.append(id_pesquisador_b)

            if not id_pesquisador_r in pesquisador_considerado:
                pesquisador_r = {}
                pesquisador_r['id'] = id_pesquisador_r
                pesquisador_r['nome_completo'] = remover_acentos(proc.responsavel_cpd.nome_cpd)
                pesquisador_r['sobrenome'] =  remover_acentos(proc.responsavel_cpd.nome_cpd.split(' ')[-1])
                pesquisador_r['inst_sede'] = inst_sede
                pesquisadores_list.append(pesquisador_r)
                pesquisador_considerado.append(id_pesquisador_r )


        return pesquisadores_list

    """ Exclui autorias que nao tem instituicao e/ou complemento """
    def filtra_autorias(self, autorias):
        autorias_filtradas = []

        for idx, autoria in enumerate(autorias):
            try:
                if len(autoria.instituicao.all()) < 1:
                    continue
                if not autoria.instituicao.all()[0].complemento:
                    continue
            except Exception as e:
                print(e)
                continue

            autorias_filtradas.append(autoria)

        return autorias_filtradas


    def get_pesquisador_autoria(self, artigo_id, autorias, pesquisador_d):

        # Verifica se hah mais de um sobrenome igual nas autorias,
        # em relacao ao sobrenome do pesquisador,
        # para nao gerar uma lista com falsos positivos.
        # Exclui qdo ha sobrenomes repetidos.
        autores_str = ' '.join(str(autoria) for autoria in autorias)
        if autores_str.count(pesquisador_d['sobrenome']) > 1:
            print('Pesquisador desconsiderado, para evitar falsos positivos.')
            return

        pesquisador_autoria = {}

        for idx, autoria in enumerate(autorias):
            # Verifica se o nome do pesquisador do processo
            # eh similar com o nome do autor no artigo.
            if not isSimilarByName(pesquisador_d['nome_completo'], autoria.autor):
                continue

            # formato do cabeçalho (fieldnames)
            # ['art_id', 'pesq_id', 'pesq_nome', 'pesq_inst_sede', 'autor_id', 'autor_nome', 'autor_inst']
            pesquisador_autoria = { self.fieldnames[0]: artigo_id, \
                                    self.fieldnames[1]: pesquisador_d['id'],\
                                    self.fieldnames[2]: pesquisador_d['nome_completo'],\
                                    self.fieldnames[3]: pesquisador_d['inst_sede'],\
                                    self.fieldnames[4]: autoria.id,\
                                    self.fieldnames[5]: autoria.autor,\
                                    self.fieldnames[6]: autoria.instituicao.all()[0].complemento
                                  }

            break


        return pesquisador_autoria

    def get_correlacoes_pesquisador_autoria(self, artigos):

        pesquisador_autoria_list = []

        for idx_art, art in enumerate(artigos):
            print("===============================")
            print(f"{idx_art}: {art.id} - {art}")

            # pega e filtra autorias do artigo
            (autorias, autor_inst) = art.pega_autoria_publica()
            autorias_filtradas = self.filtra_autorias(autorias)

            if not autorias_filtradas:
                continue

            # Pega os processos do artigo e armazena os dados dos pesquisadores em pesquisadores_processos
            processos_artigo = art.pega_processos() # instancias de projetos e/ou bolsas
            pesquisadores_processos = self.pega_pesquisadores_processos(processos_artigo) # lista de Pesquisadores do Processo


            # procura correlacao entre pesquisadores nos processos e autores nos artigos
            achou_pesquisador = 0
            artigo_id = art.id
            for pesquisador in pesquisadores_processos:
                pesquisador_autoria_d = self.get_pesquisador_autoria(artigo_id, autorias_filtradas, pesquisador)
                if pesquisador_autoria_d:
                    pesquisador_autoria_list.append(pesquisador_autoria_d)
                    self.qt_pesq_identificados += 1
                    achou_pesquisador = 1

            if achou_pesquisador:
                self.qt_art_identificados += 1

        return pesquisador_autoria_list

    def grava_correlacoes(self, output_file, pesquisador_autoria_list):

        # grava os dados em arquivo
        csvDictWriter(output_file, self.fieldnames, pesquisador_autoria_list)


class AutoriasComProjeto:

    # percentagem para a divisao do dataset
    training_per = 0.6  # 60% dos dados de entrada para o treinamento
    validation_per = 0.2 # 20% dos dados de entrada para a avaliacao durante o treinamento
    #test_per = 0.2 # 20% dos dados de entrada para o teste do Dedupe

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
        - a set of unique FAPESP researchers, and
        - a set of authors from WoS.
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

        # Split authors data for training and test
        if os.path.exists(self.messy_file):
            print('Dividindo o conjunto de dados de autorias ...')
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

        print(f'Número de linhas (autorias) = {n_data}')
        print(f'Tamanho do conjunto para Treinamento = {n_training_data}')
        print(f'Tamanho do conjunto para Validação = {n_validation_data}')
        print(f'Tamanho do conjunto para Teste ={n_test_data} \n')


        ### computing data for training
        with open(self.messy_file) as f:
            reader = csv.DictReader(f, delimiter='|')
            fieldnames = reader.fieldnames
            data_list = [row for row in reader]

        random.seed(3)
        training_data = random.sample(data_list, n_training_data) # random subset
        #print('number of possible samples to train:', len(training_data))

        # No treinamento com o Dedupe, se faz uso do active learnig,
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
        print(f"Número de amostras para Treinamento (autores únicos): {len(unique_list)} ({round(100*len(unique_list)/n_training_data,2)}% of {n_training_data})")

        ### data for validation process
        remaining_data = [row for row in data_list if row not in training_data]
        random.seed(4)
        validation_data = random.sample(remaining_data, n_validation_data) # random subset
        print(f'Número de amostras para Validação: {len(validation_data)}')
        csvDictWriter(self.validation_file, fieldnames, validation_data)

        ### computing data for test
        test_data = [row for row in remaining_data if row not in validation_data]
        print(f'Número de amostras para Teste: {len(test_data)} \n')
        csvDictWriter(self.test_file, fieldnames, test_data)
