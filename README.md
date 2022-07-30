# Correspondência de dados usando Dedupe Gazetteer

Depupe é uma biblioteca Python, baseada na tese de doutorado de Mikhail Yuryevich Bilenko [1], que usa \textit{machine learning} para performar rapidamente correspondência nebulosa (fuzzy matching), deduplicação (deduplication) e resolução de entidade~(entity resolution) [2].

Dedupe fornece a classe chamada Gazetter que lida com o problema de correspondência de dados.

Os arquivos aqui disponiibilizados correspondem a um exemplo de aplicação de correspondência de dados entre o conjunto de
dados da BV-FAPESP e uma base de artigos científicos como por exemplo Scopus, PubMed, Web of Scienc entre outras .

A princípio estamos disponibilizando somente o código correspondente ao Grupo Controle para uma análise do potencial de uso da classe Gazetteer, bem como das suas limitações. Posterioremente será disponibilizado o código para o grupo de aplicação.


## Requisitos

- Dedupe 2.0.6
- fuzzywuzzy 0.18.0
- pandas 1.0.0


![image](https://user-images.githubusercontent.com/110296380/181920468-aacc0063-81c4-45e0-a8fd-0d897952a00a.png)



# I. Grupo Controle
O grupo controle representa o grupo que sera usado para treinar e testar o modelo usado com a biblioteca Python Dedupe.
Os dados usados correspondem a artigos científicos que fazem referência a um ou mais projetos FAPESP, indicando seu número de processo.

A seguir é listada a sequência de arquivos que devem ser executados para obter os dados clusterizados com o Dedupe, bem como os resultados da avaliação do modelo de treinamento:

### 1. grupo_controle/gera_dados_para_grupo_controle.py

  Esse script tem duas funcionalidades:

  **a.** Gera uma lista de correlacao entre pesquisadores FAPESP e autores de artigos WoS,
   para o caso de artigos com projeto(s) FAPESP associado(s), e armazena o resultado
   no arquivo:
   *'grupo_controle/arquivos/dados_auxiliares/dados_pesquisador_autoria_com_projeto.csv'*

     __NOTA: Se você quiser usar o codigo disponibilizado para conjuntos de dados diferentes,
            eh necessario disponibilizar esse arquivo com as correlacoes verdadeiras dos seus
            conjuntos de dados.

  **b.** Organiza e divide os dados do arquivo *'dados_pesquisador_autoria_com_projeto.csv'*
    para obter os dados de entrada para o treinamento, predição e teste com o Dedupe.

Para executar o script, usar o comando: **'python grupo_controle/gera_dados_para_grupo_controle.py'**

O script gera os seguintes 4 arquivos para trabalhar com o Dedupe, que estarão na pasta *'grupo_controle/arquivos/dados_entrada'*:
- 'cj_canonico_pesquisadores.csv' (conjunto canonico)
- 'cj_messy_autorias_para_treinamento.csv' (conjunto messy para o processo de treinamento)
- 'cj_messy_autorias_para_validacao.csv' (conjunto messy para o processo de validacao)
- 'cj_messy_autorias_para_teste.csv' (conjunto messy para a avaliacao do modelo)


### 2. grupo_controle/dedupe_gazetteer_grupo_controle.py

- Treina e clusteriza dados do grupo controle
- Avalia os resultados obtidos com o modelo gerado pelo Dedupe
- Para executar o script, usar o comando:
**python grupo_controle/dedupe_gazetteer_grupo_controle.py'**

O script gera:
  
2 arquivos com os dados do treinamento, na pasta *'grupo_controle/arquivos/dados_treinamneto'*:
   - gazetteer_learned_settings
   - gazetteer_training.json

3 arquivos com os dados de saida da predicao para os dados de teste,*na pasta 'grupo_controle/arquivos/dados_saida'*:
   - gazetteer_matches_found.csv
   - gazetteer_false_positives.csv
   - gazetteer_false_negatives.csv

### 3. simplifica_resultado_dedupe_gazetteer.py
Diminui o numero de colunas dos arquivos de saida com o script anterior, para ter uma melhor visualizacao dos resultados obtidos.

Para executar o arquivo, usar o comando: **'python grupo_controle/simplifica_resultado_dedupe_gazetteer.py'**

O script gera os seguintes arquivos na pasta *'grupo_controle/arquivos/dados_saida'*:
- gazetteer_matches_found_simplified.csv
- gazetteer_false_positives_simplified.csv
- gazetteer_false_negatives_simplified.csv

--------------------------------------------------------------------------------

### Citações

Se você utilizar parte do código disponibilizado para um trabalho acadêmico, por favor forneça a seguinte citação:

Grupo de TI da Biblioteca Virtual FAPESP (BV-FAPESP). Correspondência de dados entre o conjunto de dados da BV-FAPESP e artigos científicos. Processo FAPESP n.º 21/14625-9. ULR: https://bv.fapesp.br

### Referências

[1] Mikhail Yuryevich Bilenko. Learnable Similarity Functions and Their Application to Record Linkage and Clustering. The University of Texas at Austin. Austin, USA. 2006.

[2] Forest Gregg and Derek Eder. 2022. Dedupe. https://github.com/dedupeio/dedupe.
