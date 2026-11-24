# Rastreabilidade dos resultados

## Origem e escopo

A preparação parte do checkpoint `Checkpoint_R5_R7_3sementes_1000MBB_com_tabelas.zip` e dos scripts associados. A integridade da cópia conferida é identificada pelo SHA-256 `16e5143cab9d5f91290b6a55701e8708a6fff6f993b93b357a8b6750fb3831b6`. O checkpoint contém dados individuais e modelos serializados e não acompanha o pacote público preparado.

A execução utiliza previsões pontuais previamente disponíveis para três sementes (123, 456 e 789). Para os nove casos do protocolo B, foram preservadas as 600 réplicas MBB anteriores e produzidas mais 400; os modelos pontuais não foram novamente treinados nessa extensão. O nome histórico da pasta importada contém `600_MBB`, mas os arquivos de réplicas verificados nela contêm 1.000 por caso. Nem todo arquivo histórico dentro de um checkpoint é automaticamente atualizado: use as tabelas de 1.000 identificadas abaixo.

| Material selecionado | Procedência e alcance | Situação |
|---|---|---|
| `Tabela03_bootstrap_Finf_kprime_1000.csv` | Consolidação de 1.000 réplicas por cenário, protocolo B. | Conferida a partir do checkpoint e regenerada. |
| `Tabela03_Finf_artigo_1000.csv` | Apresentação dos resultados de infiltração para o artigo. | Regenerada; verificar redação do manuscrito. |
| `Tabela05_configuracoes_B.csv` | Configurações disponíveis no checkpoint, protocolo B. | Regenerada a partir dos artefatos disponíveis. |
| `Tabela06_metricas_teste_protocolo_B.csv` e `Tabela06_comparacao_modelos_B.csv` | Desempenho no teste para os dois modelos, protocolo B. | 18 linhas conferidas contra as previsões salvas; tabelas regeneradas. |
| `Fig08_NRMSE_range_test_B` | NRMSE pela amplitude no teste, protocolo B. | Figura regenerada a partir das métricas disponíveis. Conferir legenda e número final no manuscrito. |
| `Ablacao_por_variavel_disponivel_B.csv` | Informação de ablação disponível na execução. | **Não demonstrada como equivalente à Tabela 4 do artigo.** |

A origem e correspondência das demais figuras e tabelas com a versão final do artigo ainda precisam de conferência. Em particular, verificar rótulo de período da Figura 2 e a identificação de RMSE/NRMSE na Figura 8 antes de publicar o manuscrito.

## Limites de interpretação

- As métricas de treino e validação de modelos finais reajustados com os dois períodos não são uma validação independente. O período de teste já foi consultado anteriormente.
- A conferência das métricas usa previsões já arquivadas; ela não prova que o pipeline completo foi reproduzido a partir dos dados originais.
- Uma réplica por cenário foi recalculada para comparar as rotinas e os artefatos; isso não constitui conferência por reexecução de todas as 9.000 réplicas.
- A cópia do notebook com 1.000 réplicas foi configurada a partir da de 600, com saídas limpas; não foi executada integralmente.
- A correção das séries e eventuais usos de informação futura devem ser documentados e considerados na interpretação.
- O manuscrito deve ser alinhado ao número de sementes desta execução. Resultados e afirmações baseados em 600 réplicas devem ser atualizados quando substituídos pelos de 1.000. Por exemplo, o valor ajustado por Holm para R5/PM₁ mudou de aproximadamente 0,0449 para 0,0899; a interpretação requer revisão.

## Identificação dos notebooks

- Notebook original de 600 réplicas: SHA-256 `67b190544396d768df71b4517c0fd2799fbd4c311d9985af91ba09904df8d173`.
- Cópia configurada para 1.000 réplicas: SHA-256 `35c31d2b8cb922fd398b6bbd8b86b0dbf2a527bff647e9bf4f10ab62d19e195d`.

As versões exatas de bibliotecas disponíveis durante a retomada constam em `ambiente_retomada_1000.json`; bibliotecas com versões diferentes podem alterar resultados ou impedir a leitura de modelos serializados.
