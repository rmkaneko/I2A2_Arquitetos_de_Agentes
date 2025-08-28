# Guia de Instalação - Sistema de Processamento VR

**Versão:** 1.0  
**Data:** 27 de agosto de 2025  
**Autor:** Manus AI  

## Visão Geral da Instalação

Este guia fornece instruções detalhadas para instalação e configuração inicial do Sistema de Processamento VR em ambiente WSL2 Ubuntu 24.04. O processo de instalação foi projetado para ser simples e direto, minimizando a complexidade técnica e garantindo que o sistema esteja operacional rapidamente.

O sistema foi especificamente otimizado para execução em ambiente WSL2, aproveitando a integração entre Windows e Linux para oferecer a melhor experiência possível. Todas as dependências são padrão e amplamente suportadas, garantindo estabilidade e compatibilidade a longo prazo.

## Pré-requisitos do Sistema

### Ambiente Operacional

**Sistema Operacional Requerido:**
- Windows 10 versão 2004 ou superior, ou Windows 11
- WSL2 (Windows Subsystem for Linux 2) habilitado
- Ubuntu 22.04 LTS ou Ubuntu 24.04 LTS instalado no WSL2

**Recursos de Hardware Mínimos:**
- 4 GB de RAM disponível
- 2 GB de espaço livre em disco
- Processador dual-core ou superior

**Recursos de Hardware Recomendados:**
- 8 GB de RAM ou superior
- 5 GB de espaço livre em disco
- Processador quad-core ou superior
- SSD para melhor performance de I/O

### Software Base

**Python e Dependências:**
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Acesso à internet para download de dependências

**Bibliotecas Python Necessárias:**
- pandas (manipulação de dados)
- openpyxl (leitura/escrita de arquivos Excel)
- pyyaml (processamento de arquivos YAML)
- numpy (operações numéricas)

## Preparação do Ambiente WSL2

### Instalação do WSL2

Se o WSL2 ainda não estiver instalado, siga estes passos:

**Passo 1: Habilitar WSL**
1. Abra o PowerShell como Administrador
2. Execute: `wsl --install`
3. Reinicie o computador quando solicitado

**Passo 2: Instalar Ubuntu**
1. Abra a Microsoft Store
2. Procure por "Ubuntu 22.04 LTS" ou "Ubuntu 24.04 LTS"
3. Clique em "Instalar"
4. Aguarde a conclusão da instalação

**Passo 3: Configurar Ubuntu**
1. Abra o Ubuntu pelo menu Iniciar
2. Crie um usuário e senha quando solicitado
3. Aguarde a configuração inicial

### Atualização do Sistema

Após a instalação do Ubuntu, atualize o sistema:

```bash
# Atualizar lista de pacotes
sudo apt update

# Atualizar pacotes instalados
sudo apt upgrade -y

# Instalar ferramentas essenciais
sudo apt install -y curl wget git unzip
```

### Verificação do Python

Verifique se o Python está instalado corretamente:

```bash
# Verificar versão do Python
python3 --version

# Verificar se pip está disponível
pip3 --version

# Se pip não estiver instalado
sudo apt install -y python3-pip
```

## Instalação do Sistema

### Método 1: Instalação Manual

**Passo 1: Criar Diretório de Instalação**
```bash
# Criar diretório para o sistema
mkdir -p ~/sistema_vr
cd ~/sistema_vr
```

**Passo 2: Copiar Arquivos do Sistema**
```bash
# Copiar todos os arquivos do sistema para o diretório
# (assumindo que os arquivos estão em um diretório fonte)
cp -r /caminho/fonte/sistema_vr/* ~/sistema_vr/
```

**Passo 3: Instalar Dependências Python**
```bash
# Instalar bibliotecas necessárias
pip3 install pandas openpyxl pyyaml numpy

# Verificar instalação
python3 -c "import pandas, openpyxl, yaml; print('Dependências instaladas com sucesso')"
```

### Método 2: Instalação via Script

Crie um script de instalação automatizada:

```bash
#!/bin/bash
# install.sh - Script de instalação automatizada

echo "=== Instalação do Sistema de Processamento VR ==="

# Verificar se está no Ubuntu/WSL2
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "ERRO: Este script deve ser executado no Ubuntu/WSL2"
    exit 1
fi

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Python e pip se necessário
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    sudo apt install -y python3 python3-pip
fi

# Instalar dependências Python
echo "Instalando dependências Python..."
pip3 install pandas openpyxl pyyaml numpy

# Criar estrutura de diretórios
echo "Criando estrutura de diretórios..."
mkdir -p ~/sistema_vr/{agentes,config,utils,dados_entrada,dados_saida,logs,tests}

# Verificar instalação
echo "Verificando instalação..."
python3 -c "import pandas, openpyxl, yaml; print('✓ Dependências OK')"

echo "=== Instalação concluída com sucesso! ==="
echo "Diretório: ~/sistema_vr"
```

Para usar o script:
```bash
chmod +x install.sh
./install.sh
```

## Configuração Inicial

### Estrutura de Diretórios

Após a instalação, verifique se a estrutura está correta:

```bash
cd ~/sistema_vr
tree
```

Estrutura esperada:
```
sistema_vr/
├── agentes/
│   ├── __init__.py
│   ├── extrator_validador.py
│   ├── consolidador_regras.py
│   ├── gerador_relatorio.py
│   └── orquestrador.py
├── config/
│   └── config.yaml
├── utils/
│   ├── __init__.py
│   ├── config_loader.py
│   └── logger.py
├── dados_entrada/
├── dados_saida/
├── logs/
├── tests/
├── main.py
├── README.md
├── MANUAL_USUARIO.md
└── INSTALACAO.md
```

### Configuração do Arquivo config.yaml

Edite o arquivo de configuração principal:

```bash
nano config/config.yaml
```

Verifique e ajuste as seguintes seções:

**Configurações Gerais:**
```yaml
sistema:
  nome: "Sistema de Processamento VR"
  versao: "1.0"
  ambiente: "producao"
```

**Regras de Negócio:**
```yaml
regras_negocio:
  dia_corte_desligamento: 15
  percentual_empresa: 0.80
  percentual_colaborador: 0.20
  competencia_referencia: "2025-05"  # Ajustar conforme necessário
```

**Cargos Excluídos:**
```yaml
exclusoes:
  cargos_nao_elegiveis:
    - "APRENDIZ"
    - "ESTAGIARIO"
    - "DIRETOR"
    - "DIRETOR EXECUTIVO"
    - "PRESIDENTE"
    # Adicionar outros cargos conforme necessário
```

### Permissões de Arquivos

Configure as permissões adequadas:

```bash
# Tornar o script principal executável
chmod +x main.py

# Definir permissões para diretórios
chmod 755 dados_entrada dados_saida logs

# Proteger arquivo de configuração
chmod 644 config/config.yaml
```

## Teste da Instalação

### Teste Básico de Funcionamento

Execute um teste básico para verificar se o sistema está funcionando:

```bash
cd ~/sistema_vr

# Teste de importação dos módulos
python3 -c "
from agentes.orquestrador import OrquestradorVR
from utils.config_loader import get_config_loader
from utils.logger import VRLogger
print('✓ Todos os módulos importados com sucesso')
"
```

### Teste de Configuração

Verifique se a configuração está sendo carregada corretamente:

```bash
python3 -c "
from utils.config_loader import get_config_loader
config = get_config_loader().get_config()
print(f'✓ Configuração carregada: {config[\"sistema\"][\"nome\"]}')
print(f'✓ Versão: {config[\"sistema\"][\"versao\"]}')
"
```

### Teste de Criação de Logs

Verifique se o sistema de logs está funcionando:

```bash
python3 -c "
from utils.logger import VRLogger
logger = VRLogger('config/config.yaml')
logger.log_info('Teste de instalação')
print('✓ Sistema de logs funcionando')
"
```

### Teste com Dados de Exemplo

Se você tiver dados de exemplo, execute um teste completo:

```bash
# Copiar dados de exemplo para dados_entrada/
# cp /caminho/dados/exemplo/* dados_entrada/

# Executar processamento de teste
python3 main.py
```

## Configuração de Ambiente de Produção

### Configurações de Segurança

**Backup Automático:**
```bash
# Criar script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_$DATE"
mkdir -p ~/backups/$BACKUP_DIR
cp -r ~/sistema_vr/config ~/backups/$BACKUP_DIR/
cp -r ~/sistema_vr/dados_entrada ~/backups/$BACKUP_DIR/
cp -r ~/sistema_vr/logs ~/backups/$BACKUP_DIR/
echo "Backup criado em ~/backups/$BACKUP_DIR"
EOF

chmod +x backup.sh
```

**Monitoramento de Logs:**
```bash
# Criar alias para visualizar logs
echo 'alias vr-logs="tail -f ~/sistema_vr/logs/*.log"' >> ~/.bashrc
echo 'alias vr-audit="cat ~/sistema_vr/logs/auditoria_vr_*.txt | tail -50"' >> ~/.bashrc
source ~/.bashrc
```

### Otimizações de Performance

**Configuração de Memória:**
```yaml
# Em config/config.yaml
performance:
  chunk_size: 1000
  max_memory_usage: "512MB"
  enable_cache: true
```

**Configuração de Logs:**
```yaml
# Para ambiente de produção
logging:
  nivel: "INFO"  # Reduzir verbosidade
  arquivo_log: "processamento_vr_{timestamp}.log"
  arquivo_auditoria: "auditoria_vr_{timestamp}.txt"
```

## Solução de Problemas de Instalação

### Problemas Comuns

**Erro: "ModuleNotFoundError: No module named 'pandas'"**
```bash
# Solução: Reinstalar dependências
pip3 install --upgrade pandas openpyxl pyyaml numpy
```

**Erro: "Permission denied"**
```bash
# Solução: Ajustar permissões
chmod +x main.py
chmod -R 755 ~/sistema_vr
```

**Erro: "FileNotFoundError: config.yaml"**
```bash
# Solução: Verificar estrutura de diretórios
ls -la config/
# Se necessário, recriar arquivo de configuração
```

**Erro: "WSL2 não encontrado"**
```bash
# Solução: Verificar instalação do WSL2
wsl --list --verbose
# Se necessário, reinstalar WSL2
```

### Verificação de Integridade

Execute uma verificação completa da instalação:

```bash
#!/bin/bash
# check_installation.sh

echo "=== Verificação de Integridade da Instalação ==="

# Verificar Python
if python3 --version; then
    echo "✓ Python instalado"
else
    echo "✗ Python não encontrado"
fi

# Verificar dependências
for module in pandas openpyxl yaml numpy; do
    if python3 -c "import $module" 2>/dev/null; then
        echo "✓ $module instalado"
    else
        echo "✗ $module não encontrado"
    fi
done

# Verificar estrutura de diretórios
for dir in agentes config utils dados_entrada dados_saida logs; do
    if [ -d "$dir" ]; then
        echo "✓ Diretório $dir existe"
    else
        echo "✗ Diretório $dir não encontrado"
    fi
done

# Verificar arquivos principais
for file in main.py config/config.yaml; do
    if [ -f "$file" ]; then
        echo "✓ Arquivo $file existe"
    else
        echo "✗ Arquivo $file não encontrado"
    fi
done

echo "=== Verificação concluída ==="
```

## Manutenção da Instalação

### Atualizações Regulares

**Atualização do Sistema Ubuntu:**
```bash
# Executar mensalmente
sudo apt update && sudo apt upgrade -y
```

**Atualização das Dependências Python:**
```bash
# Executar trimestralmente
pip3 install --upgrade pandas openpyxl pyyaml numpy
```

### Limpeza de Logs

```bash
# Script para limpeza de logs antigos
cat > cleanup_logs.sh << 'EOF'
#!/bin/bash
# Manter apenas logs dos últimos 30 dias
find ~/sistema_vr/logs -name "*.log" -mtime +30 -delete
find ~/sistema_vr/logs -name "*.txt" -mtime +30 -delete
echo "Logs antigos removidos"
EOF

chmod +x cleanup_logs.sh
```

### Monitoramento de Espaço

```bash
# Verificar uso de espaço
du -sh ~/sistema_vr/*
df -h
```

## Desinstalação

Se necessário remover o sistema:

```bash
#!/bin/bash
# uninstall.sh

echo "=== Desinstalação do Sistema de Processamento VR ==="
read -p "Tem certeza que deseja remover o sistema? (s/N): " confirm

if [[ $confirm == [sS] ]]; then
    # Fazer backup final
    DATE=$(date +%Y%m%d_%H%M%S)
    tar -czf ~/sistema_vr_backup_$DATE.tar.gz ~/sistema_vr/
    
    # Remover diretório
    rm -rf ~/sistema_vr
    
    # Remover dependências (opcional)
    read -p "Remover dependências Python? (s/N): " remove_deps
    if [[ $remove_deps == [sS] ]]; then
        pip3 uninstall -y pandas openpyxl pyyaml numpy
    fi
    
    echo "Sistema removido. Backup salvo em ~/sistema_vr_backup_$DATE.tar.gz"
else
    echo "Desinstalação cancelada"
fi
```

## Suporte Pós-Instalação

### Recursos de Ajuda

- **README.md**: Visão geral do sistema
- **MANUAL_USUARIO.md**: Guia de operação
- **Logs de auditoria**: Histórico de operações
- **Arquivo de configuração**: Personalização de regras

### Contatos

Para suporte técnico relacionado à instalação:
- Consultar logs de erro em `~/sistema_vr/logs/`
- Verificar configuração em `~/sistema_vr/config/config.yaml`
- Revisar este guia de instalação

A instalação do Sistema de Processamento VR foi projetada para ser robusta e confiável. Seguindo este guia, você terá um sistema totalmente funcional e pronto para uso em ambiente de produção.

