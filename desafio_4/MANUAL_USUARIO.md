# Manual do Usuário - Sistema de Processamento VR

**Versão:** 1.0  
**Data:** 27 de agosto de 2025  
**Autor:** Manus AI  

## Introdução

Este manual foi desenvolvido especificamente para a equipe de Recursos Humanos e operadores do sistema de processamento de vale-refeição. O objetivo é fornecer instruções claras e detalhadas para operação do sistema, interpretação dos resultados e resolução de problemas comuns.

O Sistema de Processamento VR automatiza completamente o cálculo de vale-refeição, aplicando todas as regras de negócio de forma consistente e gerando relatórios detalhados para auditoria. O sistema foi projetado para ser intuitivo e seguro, minimizando a possibilidade de erros humanos e garantindo total rastreabilidade das operações realizadas.

## Preparação dos Dados de Entrada

### Arquivos Obrigatórios

Antes de executar o sistema, certifique-se de que os seguintes arquivos estão disponíveis e atualizados:

**ATIVOS.xlsx** - Base principal de colaboradores
Este arquivo deve conter todos os colaboradores ativos na competência a ser processada. As colunas obrigatórias são:
- MATRICULA: Número único de identificação do colaborador
- EMPRESA: Código da empresa
- TITULO DO CARGO: Cargo atual do colaborador
- DESC. SITUACAO: Situação atual (Trabalhando, Férias, etc.)
- Sindicato: Nome completo do sindicato ao qual o colaborador pertence

**Base sindicato x valor.xlsx** - Valores de VR por sindicato
Este arquivo define o valor diário do vale-refeição para cada sindicato. As colunas obrigatórias são:
- ESTADO: Nome do sindicato (deve corresponder aos nomes no arquivo ATIVOS)
- VALOR: Valor diário do vale-refeição em reais

**Base dias uteis.xlsx** - Dias úteis por sindicato
Este arquivo define quantos dias úteis cada sindicato trabalha no período de referência. As colunas obrigatórias são:
- SINDICADO: Nome do sindicato
- DIAS UTEIS: Número de dias úteis no período

### Arquivos Opcionais

Os seguintes arquivos são opcionais, mas quando fornecidos, permitem aplicação de regras específicas:

**ADMISSÃO ABRIL.xlsx** - Colaboradores admitidos no mês
Para colaboradores admitidos durante o mês da competência, permitindo cálculo proporcional.

**AFASTAMENTOS.xlsx** - Colaboradores afastados
Lista colaboradores em licença maternidade, auxílio doença ou outros afastamentos que impedem o recebimento de VR.

**APRENDIZ.xlsx** - Lista de aprendizes
Colaboradores com contrato de aprendizagem, que são automaticamente excluídos do VR.

**DESLIGADOS.xlsx** - Colaboradores desligados
Lista colaboradores desligados no mês, com aplicação da regra de corte no dia 15.

**ESTÁGIO.xlsx** - Lista de estagiários
Estagiários são automaticamente excluídos do vale-refeição.

**EXTERIOR.xlsx** - Colaboradores no exterior
Colaboradores trabalhando no exterior podem ter valores especiais ou serem excluídos.

**FÉRIAS.xlsx** - Colaboradores em férias
Lista colaboradores em férias com o número de dias, para cálculo proporcional.

### Verificação da Qualidade dos Dados

Antes de processar, verifique se:

1. **Não há linhas vazias** no início dos arquivos Excel
2. **Os cabeçalhos estão corretos** e correspondem aos esperados pelo sistema
3. **As matrículas são únicas** dentro de cada arquivo
4. **Os nomes dos sindicatos são consistentes** entre os arquivos
5. **As datas estão no formato correto** (DD/MM/AAAA)
6. **Os valores numéricos não contêm caracteres especiais** (exceto vírgula decimal)

## Execução do Sistema

### Passo a Passo para Processamento

**Passo 1: Preparar o Ambiente**
1. Abra o terminal WSL2 ou Linux
2. Navegue até o diretório do sistema: `cd /caminho/para/sistema_vr`
3. Verifique se todos os arquivos de entrada estão no diretório `dados_entrada/`

**Passo 2: Executar o Processamento**
```bash
python3 main.py
```

**Passo 3: Acompanhar a Execução**
O sistema exibirá mensagens de progresso em tempo real:
- FASE 1: Preparação do ambiente
- FASE 2: Extração e validação de dados
- FASE 3: Consolidação e aplicação de regras
- FASE 4: Geração de relatórios
- FASE 5: Finalização

**Passo 4: Verificar os Resultados**
Ao final, o sistema exibirá um resumo com:
- Número de colaboradores processados
- Valor total calculado
- Localização dos arquivos gerados

### Interpretação das Mensagens do Sistema

**Mensagens de Sucesso:**
- "✓ Validação [nome]: [descrição]" - Validação passou com sucesso
- "Arquivo processado: [nome] - [X] registros" - Arquivo lido corretamente
- "PROCESSAMENTO CONCLUÍDO COM SUCESSO!" - Execução finalizada

**Mensagens de Aviso:**
- "⚠ [descrição]" - Situação que requer atenção mas não impede o processamento
- "Arquivo opcional não encontrado" - Arquivo não obrigatório ausente

**Mensagens de Erro:**
- "ERRO: [descrição]" - Problema que impede a continuação do processamento
- "Arquivo obrigatório não encontrado" - Falta arquivo essencial
- "Colunas obrigatórias faltantes" - Estrutura do arquivo incorreta

## Interpretação dos Resultados

### Planilha Principal (VR_MENSAL_AAAA_MM.xlsx)

A planilha principal contém os seguintes campos:

**Matricula**: Número de identificação do colaborador
**Admissão**: Data de admissão do colaborador
**Sindicato do Colaborador**: Nome completo do sindicato
**Competência**: Mês/ano de referência do processamento
**Dias**: Número de dias efetivos para cálculo (já descontadas férias, afastamentos, etc.)
**VALOR DIÁRIO VR**: Valor diário do vale-refeição conforme sindicato
**TOTAL**: Valor total do VR para o colaborador (Dias × VALOR DIÁRIO VR)
**Custo empresa**: Valor pago pela empresa (80% do total)
**Desconto profissional**: Valor descontado do colaborador (20% do total)
**OBS GERAL**: Observações sobre cálculos especiais ou situações específicas

### Aba Validações

A aba "Validações" contém verificações de consistência:

**Resumo Estatístico**: Totais gerais do processamento
**Exclusões por Categoria**: Quantos colaboradores foram excluídos e por quê
**Validações de Consistência**: Verificações matemáticas e lógicas

### Relatório de Exclusões

O arquivo `colaboradores_excluidos.xlsx` lista todos os colaboradores que não receberam VR, com:
- Matrícula e cargo do colaborador
- Motivo específico da exclusão
- Sindicato ao qual pertence

### Log de Auditoria

O arquivo de auditoria (formato .txt) fornece um relatório completo em linguagem natural, incluindo:

**Resumo Geral**: Estatísticas principais do processamento
**Exclusões por Categoria**: Detalhamento das exclusões aplicadas
**Cálculos Especiais**: Lista de situações especiais processadas
**Validações Realizadas**: Todas as verificações executadas
**Arquivos Processados**: Confirmação dos arquivos lidos
**Avisos**: Inconsistências encontradas que merecem atenção

## Regras de Negócio Aplicadas

### Regra de Férias Proporcionais

Quando um colaborador está de férias durante parte do mês, o sistema calcula o VR proporcionalmente aos dias trabalhados. Por exemplo:
- Mês com 22 dias úteis
- Colaborador com 10 dias de férias
- VR calculado para 12 dias (22 - 10)

### Regra de Desligamento (Corte Dia 15)

A regra de desligamento é aplicada com base na data de comunicação:
- **Comunicado até dia 15**: Colaborador não recebe VR do mês
- **Comunicado após dia 15**: Colaborador recebe VR integral do mês

### Exclusões Automáticas

Os seguintes tipos de colaboradores são automaticamente excluídos:
- Aprendizes (contrato de aprendizagem)
- Estagiários
- Diretores e cargos de alta direção
- Colaboradores em licença maternidade
- Colaboradores em auxílio doença
- Colaboradores no exterior (conforme situação específica)

### Cálculos por Sindicato

Cada sindicato possui:
- Valor diário específico de VR
- Número de dias úteis específico para o período
- Regras particulares que podem afetar o cálculo

### Divisão Empresa/Colaborador

O valor total do VR é dividido conforme definido na configuração:
- **80% pago pela empresa** (custo empresa)
- **20% descontado do colaborador** (desconto profissional)

## Resolução de Problemas Comuns

### Problema: "Arquivo obrigatório não encontrado"

**Causa**: Um dos três arquivos obrigatórios não está no diretório dados_entrada/
**Solução**: 
1. Verificar se os arquivos ATIVOS.xlsx, Base sindicato x valor.xlsx e Base dias uteis.xlsx estão presentes
2. Confirmar que os nomes dos arquivos estão exatamente como esperado
3. Verificar permissões de acesso aos arquivos

### Problema: "Colunas obrigatórias faltantes"

**Causa**: A estrutura do arquivo Excel não corresponde ao esperado
**Solução**:
1. Abrir o arquivo Excel e verificar os cabeçalhos das colunas
2. Comparar com a lista de colunas obrigatórias para cada arquivo
3. Corrigir nomes das colunas ou adicionar colunas faltantes
4. Remover linhas vazias no início do arquivo

### Problema: "Matrículas não encontradas na base de ativos"

**Causa**: Arquivos auxiliares contêm matrículas que não existem na base de ativos
**Solução**:
1. Verificar se a base de ativos está atualizada
2. Confirmar se as matrículas nos arquivos auxiliares estão corretas
3. Remover registros de colaboradores que não estão mais ativos

### Problema: "Sindicatos sem valor definido"

**Causa**: Colaboradores ativos pertencem a sindicatos não listados na base de valores
**Solução**:
1. Verificar nomes dos sindicatos na base de ativos
2. Adicionar valores para sindicatos faltantes na base de valores
3. Corrigir inconsistências nos nomes dos sindicatos

### Problema: Valores incorretos na planilha final

**Causa**: Configuração incorreta de percentuais ou valores base
**Solução**:
1. Verificar arquivo config/config.yaml
2. Confirmar percentuais de empresa/colaborador
3. Validar valores diários por sindicato
4. Verificar dias úteis configurados

## Manutenção e Atualizações

### Atualizações Mensais

Para cada nova competência:
1. Atualizar arquivos de entrada com dados do novo mês
2. Verificar se há mudanças nas regras de negócio
3. Ajustar configuração se necessário (config/config.yaml)
4. Executar processamento e validar resultados

### Mudanças nas Regras de Negócio

Quando houver alterações nas regras:
1. Editar arquivo config/config.yaml
2. Atualizar listas de cargos excluídos se necessário
3. Modificar percentuais empresa/colaborador se aplicável
4. Testar com dados de exemplo antes do processamento oficial

### Backup e Histórico

Recomenda-se manter:
- Backup dos arquivos de entrada utilizados
- Cópia das planilhas geradas
- Logs de auditoria para histórico
- Versões do arquivo de configuração

## Contatos e Suporte

### Suporte Técnico

Para questões técnicas relacionadas ao funcionamento do sistema:
- Consultar logs de auditoria para entender decisões automáticas
- Verificar logs técnicos para detalhes de erros
- Revisar arquivo de configuração para ajustes necessários

### Suporte Funcional

Para questões sobre regras de negócio ou interpretação de resultados:
- Consultar este manual para esclarecimentos
- Analisar relatório de auditoria para justificativas
- Verificar relatório de exclusões para casos específicos

### Documentação Adicional

- README.md: Visão geral técnica do sistema
- Arquitetura_sistema_agentes.md: Documentação técnica detalhada
- Logs de auditoria: Histórico de processamentos anteriores

## Glossário

**Agente**: Componente especializado do sistema responsável por uma função específica
**Competência**: Mês/ano de referência para o cálculo do vale-refeição
**Idempotência**: Capacidade de executar múltiplas vezes com o mesmo resultado
**Log de Auditoria**: Relatório em linguagem natural das operações realizadas
**Matrícula**: Identificador único do colaborador no sistema
**Pipeline**: Sequência ordenada de processamento pelos agentes
**Sindicato**: Entidade que define valores e regras específicas de VR
**VR**: Vale-refeição ou auxílio alimentação

Este manual deve ser consultado sempre que houver dúvidas sobre a operação do sistema ou interpretação dos resultados. Para situações não cobertas neste documento, consulte a documentação técnica ou entre em contato com o suporte.

