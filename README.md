# Correspondência de dados usando Dedupe Gazetteer

Depupe é uma biblioteca Python, baseada na tese de doutorado de Mikhail Yuryevich Bilenko [1], que usa *machine learning* para performar rapidamente correspondência nebulosa (fuzzy matching), deduplicação (deduplication) e resolução de entidade (entity resolution) [2].

Dedupe fornece a classe chamada Gazetter que lida com o problema de correspondência de dados.

Os arquivos aqui disponiibilizados correspondem a um exemplo de aplicação de correspondência de dados entre o conjunto de
dados da BV-FAPESP e uma base de artigos científicos como por exemplo Scopus, PubMed, Web of Science entre outras.

Inicialmente estamos disponibilizando o código correspondente ao Grupo Controle para uma análise do potencial de uso da classe Gazetteer, bem como das suas limitações. Posterioremente será disponibilizado o código para o grupo de aplicação.


## Requisitos

- Dedupe 2.0.6
- fuzzywuzzy 0.18.0
- pandas 1.0.0


![image](https://user-images.githubusercontent.com/110296380/181920468-aacc0063-81c4-45e0-a8fd-0d897952a00a.png)


Os arquivos disponibilizados estão divididos em dois grupos:
I. Grupo controle
II. Grupo aplicacao

# I. Grupo Controle
O grupo controle representa o grupo que sera usado para treinar e testar o modelo usado com a biblioteca Python Dedupe.
Os dados usados correspondem a artigos científicos que fazem referência a um ou mais projetos FAPESP, indicando seu número de processo.

A seguir é listada a sequência de arquivos que devem ser executados para obter os dados clusterizados com o Dedupe, bem como os resultados da avaliação do modelo de treinamento:


### 1. prepara_dados_grupo_controle.py

Organiza e divide os dados do arquivo *'true_matches_pesquisador_autoria.csv'*, para obter os dados de entrada para o treinamento, predição e teste com o Dedupe.

    __NOTA: O arquivo 'true_matches_pesquisador_autoria.csv' se encontra na pasta 'arquivos/grupo_controle/dados_auxiliares', e    contém a lista de correlações entre pesquisadores FAPESP e autores de artigos, para o caso de artigos com projeto(s) FAPESP associado(s).
    Se você quiser usar o codigo disponibilizado para conjuntos de dados diferentes, é necessário disponibilizar este arquivo com as correlações verdadeiras dos seus conjuntos de dados.

Para executar o script, usar o comando: **python prepara_dados_grupo_controle.py**

O script gera os seguintes 4 arquivos para trabalhar com o Dedupe, os quais estarão na pasta *'arquivos/grupo_controle/dados_entrada'*:
- 'cj_canonico_pesquisadores.csv' (conjunto canônico)
- 'cj_messy_autorias_para_treinamento.csv' (conjunto messy para o processo de treinamento)
- 'cj_messy_autorias_para_validacao.csv' (conjunto messy para o processo de validação)
- 'cj_messy_autorias_para_teste.csv' (conjunto messy para a avaliação do modelo)


### 2. dedupe_gazetteer.py

- Treina e clusteriza dados do grupo controle
- Avalia os resultados obtidos com o modelo gerado pelo Dedupe

- Para executar o script, usar o comando: **python dedupe_gazetteer.py controle**


O script gera 5 arquivos:

2 arquivos com os dados do treinamento, na pasta *'arquivos/dados_treinamento'*:
- gazetteer_learned_settings
- gazetteer_training.json

3 arquivos com os dados de saída da predição para os dados de teste, na pasta *'arquivos/grupo_controle/dados_saida'*:
- gazetteer_matches_found.csv
- gazetteer_false_positives.csv
- gazetteer_false_negatives.csv

__NOTA: O arquivo gerado 'gazetteer_learned_settings' serah usado para
        a predição do grupo de aplicação.



### 4. simplifica_resultado.py
Diminui o número de colunas dos arquivos de saída com o script anterior, para ter uma melhor visualização dos resultados obtidos.

Para executar o arquivo, usar o comando: **python simplifica_resultado.py controle**

O script gera os seguintes arquivos na pasta *'arquivos/grupo_controle/dados_saida'*:
- gazetteer_matches_found_simplified.csv
- gazetteer_false_positives_simplified.csv
- gazetteer_false_negatives_simplified.csv



# II. Grupo Aplicação
Representa o grupo que sera usado para encontrar a
correspondencia entre o pesquisador FAPESP e o autor de artigo WoS,
para o caso de artigos sem projeto FAPESP identificado.

A seguir eh listada a sequência de arquivos que devem ser executados
para obter os dados clusterizados com o Dedupe:

### 1. prepara_dados_grupo_aplicacao.py

Organiza e pre-processa os dados dos arquivos da pasta *'arquivos/grupo_aplicacao/dados_auxiliares'*:
- 'pesquisadores_fapesp.csv': contém a lista de todos os pesquisadores FAPESP de todos os projetos ativos.
- 'autorias_sem_processo.csv': contém a lista de todos os autores de artigos WoS sem projeto FAPESP associado.

Para executar o script, usar o comando: **python prepara_dados_grupo_aplicacao.py**

Os arquivos gerados estarão na pasta *'arquivos/grupo_aplicacao/dados_entrada'* como:
- 'cj_canonico_pesquisadores.csv'
- 'cj_messy_autorias.csv'

### 2. dedupe_gazetteer.py

Clusteriza os dados do grupo de aplicação, os quais foram gerados com o sccript *'prepara_dados_grupo_aplicacao.py'*.

Os dados de treinamento usados correspondem aos arquivos obtidos com o treinamento do grupo controle, i.e., o arquivo *'gazetteer_learned_settings'* da pasta *'arquivos/dados_treinamento'*.

Para executar o script, usar o comando: **python dedupe_gazetteer.py aplicacao**

O script gera o seguinte arquivo com os dados de saída da predição, o qual se encontrara na pasta *'arquivos/grupo_aplicacao/dados_saida'*:
- gazetteer_matches_found.csv

### 3. simplifica_resultado.py

Diminui o numero de colunas dos arquivos de saida com o script anterior, para ter uma melhor visualizacao dos resultados obtidos.


Para executar o script, usar o comando: **python simplifica_resultado.py aplicacao**

O script gera o seguinte arquivo na pasta *'arquivos/grupo_aplicacao/dados_saida'*:
- gazetteer_matches_found_simplified.csv


--------------------------------------------------------------------------------

### Citações

Se você utilizar parte do código disponibilizado para um trabalho acadêmico, por favor forneça a seguinte citação:

Grupo de TI da Biblioteca Virtual FAPESP (BV-FAPESP). Correspondência de dados entre o conjunto de dados da BV-FAPESP e artigos científicos. Processo FAPESP n.º 21/14625-9. ULR: https://github.com/BV-FAPESP/citations-dedupe

### Referências

[1] Mikhail Yuryevich Bilenko. Learnable Similarity Functions and Their Application to Record Linkage and Clustering. The University of Texas at Austin. Austin, USA. 2006.

[2] Forest Gregg and Derek Eder. 2022. Dedupe. https://github.com/dedupeio/dedupe.
