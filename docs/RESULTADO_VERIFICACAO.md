# Verificações desta preparação

Em 24 de novembro de 2026, com o checkpoint identificado em `RASTREABILIDADE.md` e as dependências disponíveis no ambiente de trabalho:

- Foram recalculadas 18 linhas de métricas de teste para nove cenários e dois modelos, usando as previsões arquivadas.
- Foram verificadas a presença e a identificação de 1.000 réplicas em cada um dos nove cenários do protocolo B.
- Foi recalculada uma réplica em cada cenário e comparada à arquivada; a maior diferença absoluta observada foi inferior a 4 × 10⁻⁸.
- As seis tabelas selecionadas foram regeneradas e comparadas numericamente com as incluídas no pacote; a Figura 8 foi gerada novamente.

Essas verificações reutilizam artefatos existentes e não demonstram uma execução completa e independente a partir dos dados originais. Não foi verificada uma instalação limpa das dependências.
