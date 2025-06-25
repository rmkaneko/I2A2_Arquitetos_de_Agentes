# I2A2_Arquitetos_de_Agentes

# Agente Autônomo de Análise de Notas Fiscais com n8n, Ollama e MySQL

Este repositório contém o workflow `notas.json` para o [n8n](https://n8n.io), que automatiza a análise de notas fiscais a partir de arquivos CSV armazenados no Google Drive, utilizando IA local via Ollama e armazenamento estruturado em MySQL.

---

## 📈 Visão Geral

O agente realiza as seguintes etapas:

1. **Recebe perguntas em linguagem natural** do usuário (chat/webhook).
2. **Baixa os arquivos CSV** de notas fiscais (cabeçalho e itens) do Google Drive.
3. **Extrai e combina os dados** dos arquivos CSV.
4. **Insere ou atualiza os dados** na tabela MySQL `notas_fiscais`.
5. **Gera uma consulta SQL** baseada na pergunta do usuário, usando IA local (Ollama/Mistral).
6. **Executa a consulta SQL** no banco de dados.
7. **Transforma o resultado em resposta textual** clara e formatada, novamente via IA local.
8. **Retorna a resposta ao usuário**.

---

## 🙏 Agradecimento e contribuição do apresentador

Este projeto foi desenvolvido com base no tutorial apresentado por Nicolas Spogis em [https://www.youtube.com/live/GSdtHMoyoUs]com o passo a passo como integrar o n8n ao Google Drive, Ollama e MySQL para criar um agente autônomo de análise de dados.  
Sua explicação detalhada sobre a configuração dos nós, integração com IA local e boas práticas de automação foi fundamental para a reprodução e adaptação deste workflow.  
Agradecemos pela didática e pela disponibilização do conhecimento à comunidade.

---

## 🚀 Como usar

### 1. Pré-requisitos

- [n8n](https://n8n.io) instalado (local ou Docker)
- [Ollama](https://ollama.com) rodando localmente com o modelo `mistral` (ou outro LLM compatível)
- Acesso a um banco de dados MySQL com a tabela `notas_fiscais` (veja estrutura abaixo)
- Conta no Google Drive para armazenar os arquivos CSV

### 2. Estrutura da tabela MySQL


CREATE TABLE notas_fiscais (
 chave_acesso VARCHAR(44) NOT NULL PRIMARY KEY,
 modelo VARCHAR(100),
 serie VARCHAR(10),
 numero VARCHAR(20),
 natureza_operacao VARCHAR(100),
 data_emissao DATETIME,
 cpf_cnpj_emitente VARCHAR(14),
 razao_social_emitente VARCHAR(150),
 inscricao_estadual_emitente VARCHAR(20),
 uf_emitente CHAR(2),
 municipio_emitente VARCHAR(100),
 cnpj_destinatario VARCHAR(14),
 nome_destinatario VARCHAR(150),
 uf_destinatario CHAR(2),
 indicador_ie_destinatario VARCHAR(50),
 destino_operacao VARCHAR(50),
 consumidor_final VARCHAR(50),
 presenca_comprador VARCHAR(50),
 numero_produto INT,
 descricao_produto_servico VARCHAR(150),
 codigo_ncm_sh VARCHAR(10),
 ncm_sh_tipo_produto VARCHAR(150),
 cfop VARCHAR(10),
 quantidade DECIMAL(10,2),
 unidade VARCHAR(20),
 valor_unitario DECIMAL(10,2),
 valor_total DECIMAL(10,2),
 evento_mais_recente VARCHAR(100),
 data_hora_evento_mais_recente DATETIME,
 valor_nota_fiscal DECIMAL(10,2)
 );
text

### 3. Configuração

1. **Importe o arquivo `notas.json` no n8n**.
2. **Configure as credenciais**:
   - Google Drive OAuth2
   - MySQL
   - Ollama API (modelo `mistral`)
3. **Atualize os IDs dos arquivos CSV** no Google Drive, se necessário.
4. **Garanta que o Ollama esteja rodando** (por padrão na porta 11434).
5. **Execute o workflow** e envie perguntas em português sobre as notas fiscais.

---

## 💬 Exemplos de perguntas

- "Qual o valor total das notas emitidas?"
- "Quantas notas fiscais foram emitidas?"
- "Qual empresa mais vendeu?"
- "Qual a nota com maior valor?"

---

## 🔒 Segurança

- **Nenhuma API key está exposta** no arquivo `notas.json`. Todas as credenciais são referenciadas pelo sistema seguro do n8n.
- Não compartilhe suas credenciais em campos de parâmetros dos nós.

---

## 📂 Estrutura dos arquivos CSV esperados

- **202401_NFs_Cabecalho.csv**: Dados principais das notas fiscais.
- **202401_NFs_Itens.csv**: Itens detalhados das notas fiscais.

---

## 📷 Fluxo resumido


Usuário → [n8n] → [Google Drive] → [CSV] → [MySQL] → [Ollama] → Resposta
text

---

## 📄 Licença

Este projeto é distribuído sob a licença MIT.

---
https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/34034641/853750c4-d5cc-442c-8fae-61e49785f88f/notas.json
https://www.youtube.com/live/GSdtHMoyoUs
https://n8n.io/integrations/ollama-model/
https://community.n8n.io/t/instructional-video-on-n8n-ollama-ubuntu-installation/54215
https://www.youtube.com/watch?v=VDuA5xbkEjo
https://www.skool.com/ai-automation-society/best-ollama-model-for-complex-tools-support
https://www.reddit.com/r/n8n/comments/1iouzpu/sensitive_document_processing/
https://gist.github.com/erkobridee/6c145edadde3a6a329cd44198ea32ee1


