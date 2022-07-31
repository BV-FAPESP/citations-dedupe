import re, csv
from unicodedata import normalize
from fuzzywuzzy import fuzz


exception_words = ['de','da','das','do','dos','del', 'la', 'di']


def remover_acentos(txt, codif='utf-8'):
    try:
        txt = txt.encode('utf-8')
        texto = normalize('NFKD', txt.decode(codif)).encode('ASCII', 'ignore').decode()
        return texto
    except Exception as e:
        print(e)
        print(txt)
        pass



def getExtendedName(fullname):
    txt = fullname.strip()
    if txt.find(',') !=-1:
        txt = txt.rpartition(',')
        txt = txt[2] + ' ' + txt[0]

    txt = remover_acentos(txt)
    txt = re.sub('[-|.|,|\']',' ',txt).strip()
    txt = re.sub('\s+',' ',txt)

    return txt

def getLongFirstName(fullname):
    first_name=''
    ext_name = getExtendedName(fullname)
    txt_list = ext_name.split()
    if len(txt_list[0])>2:
        first_name = txt_list[0]

    return first_name

def getFirstName(fullname):
    ext_name = getExtendedName(fullname)
    first_name = ext_name.split()[0]

    return first_name

def getLastName(fullname):
    ext_name = getExtendedName(fullname)
    txt_list = ext_name.split()
    last_name = txt_list[-1]

    if last_name.lower()=='jr':
        last_name='Junior'

    return last_name

def getPartialAbbreviation(fullname):
    abbr = ''
    #exception_words = ['de','da','das','do','dos']
    name = re.sub('-e-|\se\s',' ',fullname)
    ext_name = getExtendedName(name)
    txt_list = ext_name.split()

    del txt_list[-1]

    for word in txt_list:
        if word.lower() not in exception_words:
            abbr= abbr+word[0].upper()

    return abbr

def getLongMiddleName(fullname):
    name = re.sub('-e-|\se\s',' ',fullname)
    ext_name = getExtendedName(name)
    txt_list = ext_name.split()

    if len(txt_list) <3:
        return ""
    else:
        del txt_list[0]
        del txt_list[-1]

    mName = []
    for word in txt_list:
        if (word.lower() not in exception_words) and len(word)>2:
            mName.append(word)

    return " ".join(mName)

def isSimilarByName(fullnameA, fullnameB):
    nameA_list = getExtendedName(fullnameA).lower().split()
    nameB_list = getExtendedName(fullnameB).lower().split()

    # compara ultimo sobrenome
    if nameA_list[-1] != nameB_list[-1]:
        return False

    # compara primeiro nome
    if nameA_list[0][0] != nameB_list[0][0]:
        return False
    elif len(nameA_list[0]) > 2 and  len(nameB_list[0]) > 2:
        if nameA_list[0] != nameB_list[0]:
            return False

    # compara nomes do meio nao abreviados
    middle_nameA = getLongMiddleName(fullnameA).lower()
    middle_nameB = getLongMiddleName(fullnameB).lower()

    if middle_nameA != '' and middle_nameB != '':
        if fuzz.ratio(middle_nameA,middle_nameB)<40:
            return False

    return True


def getTypeOfNameAbbreviation(fullname):
    name = re.sub('-e-|\se\s',' ',fullname)
    ext_name = getExtendedName(name)
    txt_list = ext_name.split()
    del txt_list[-1]

    new_list = []
    for index, word in enumerate(txt_list):
        if (word.lower() not in exception_words):
            new_list.append(word)

    with_abbr = 0
    for word in new_list:
        if len(word) <= 2:
            with_abbr += 1

    if with_abbr == 0:
        return 0 # nome sem abreviacoes

    if len(new_list) == 1:
        return 1 # unico primeiro nome abreviado
    elif len(new_list) == with_abbr:
        return 2 # nome completamente abreviado sem considerar o ultimo sobrenome

    return 3 # outros casos



def countRows(filename):
    """
    Counts the number of lines in a data file, regardless of field names.
    """
    n_data = 0
    with open(filename) as f:
        reader = csv.DictReader(f, delimiter='|')
        for row in reader:
            n_data += 1

    return n_data

def csvDictWriter(filename, fieldnames, iterable_data):

    with open(filename, 'w', newline='') as f:
        try:
            filewriter = csv.DictWriter(f, delimiter='|',quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
            filewriter.writeheader() # Cria cabecalho do arquivo CSV
            filewriter.writerows(iterable_data)
        except csv.Error as e:
            sys.exit(f'file {filename}, line {filewriter.line_num}: {e}')

def csvDictReaderGenerator(filename, fieldnames=False):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        if fieldnames == True:
            yield reader.fieldnames

        try:
            for row_id, row in enumerate(reader):
                yield (row_id, row)
        except csv.Error as e:
            sys.exit(f'file {filename}, line {reader.line_num}: {e}')
