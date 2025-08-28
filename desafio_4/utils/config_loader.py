"""
Utilitário para Carregamento de Configurações
Autor: Manus AI
Data: 27/08/2025
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import os


class ConfigLoader:
    """Carregador de configurações com validação"""
    
    def __init__(self, config_path: str = None):
        """Inicializa o carregador de configurações"""
        if config_path is None:
            # Buscar config.yaml no diretório do projeto
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_and_validate_config()
        
    def _load_and_validate_config(self) -> Dict[str, Any]:
        """Carrega e valida o arquivo de configuração"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Erro ao carregar configuração YAML: {e}")
        
        # Validar estrutura básica
        self._validate_config_structure(config)
        
        # Resolver caminhos relativos
        config = self._resolve_paths(config)
        
        return config
    
    def _validate_config_structure(self, config: Dict[str, Any]):
        """Valida a estrutura básica do arquivo de configuração"""
        required_sections = [
            'sistema', 'arquivos', 'arquivos_entrada', 
            'regras_negocio', 'exclusoes', 'logging'
        ]
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Seção obrigatória '{section}' não encontrada na configuração")
        
        # Validar arquivos de entrada obrigatórios
        required_files = [
            'ativos', 'sindicato_valor', 'dias_uteis'
        ]
        
        for file_key in required_files:
            if file_key not in config['arquivos_entrada']:
                raise ValueError(f"Arquivo obrigatório '{file_key}' não definido na configuração")
    
    def _resolve_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve caminhos relativos para absolutos"""
        project_root = self.config_path.parent.parent
        
        # Resolver diretórios
        for dir_key in ['diretorio_entrada', 'diretorio_saida', 'diretorio_logs']:
            if dir_key in config['arquivos']:
                path = config['arquivos'][dir_key]
                if not os.path.isabs(path):
                    config['arquivos'][dir_key] = str(project_root / path.lstrip('./'))
        
        return config
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna a configuração carregada"""
        return self.config
    
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Retorna uma seção específica da configuração"""
        if section_name not in self.config:
            raise KeyError(f"Seção '{section_name}' não encontrada na configuração")
        return self.config[section_name]
    
    def get_file_path(self, file_key: str) -> str:
        """Retorna o caminho completo de um arquivo de entrada"""
        if file_key not in self.config['arquivos_entrada']:
            raise KeyError(f"Arquivo '{file_key}' não definido na configuração")
        
        filename = self.config['arquivos_entrada'][file_key]
        base_dir = self.config['arquivos']['diretorio_entrada']
        
        return os.path.join(base_dir, filename)
    
    def get_output_path(self, filename: str = None) -> str:
        """Retorna o caminho de saída para um arquivo"""
        base_dir = self.config['arquivos']['diretorio_saida']
        
        if filename is None:
            # Usar template padrão
            competencia = self.config['regras_negocio']['competencia_referencia']
            filename = self.config['arquivos']['template_saida'].format(
                competencia=competencia.replace('-', '_')
            )
        
        return os.path.join(base_dir, filename)
    
    def is_cargo_excluido(self, cargo: str) -> bool:
        """Verifica se um cargo está na lista de exclusões"""
        cargos_excluidos = self.config['exclusoes']['cargos_nao_elegiveis']
        return cargo.upper().strip() in [c.upper().strip() for c in cargos_excluidos]
    
    def is_afastamento_excluido(self, tipo_afastamento: str) -> bool:
        """Verifica se um tipo de afastamento está na lista de exclusões"""
        afastamentos_excluidos = self.config['exclusoes']['tipos_afastamento_excluidos']
        return tipo_afastamento in afastamentos_excluidos
    
    def get_sindicato_normalizado(self, sindicato_original: str) -> str:
        """Retorna o nome normalizado do sindicato"""
        mapeamento = self.config.get('mapeamento_sindicatos', {})
        return mapeamento.get(sindicato_original, sindicato_original)
    
    def validate_directories(self):
        """Valida e cria diretórios necessários"""
        directories = [
            self.config['arquivos']['diretorio_entrada'],
            self.config['arquivos']['diretorio_saida'],
            self.config['arquivos']['diretorio_logs']
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def reload_config(self):
        """Recarrega a configuração do arquivo"""
        self.config = self._load_and_validate_config()


# Instância global para facilitar acesso
_config_loader = None

def get_config_loader(config_path: str = None) -> ConfigLoader:
    """Retorna instância singleton do carregador de configurações"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader

def get_config() -> Dict[str, Any]:
    """Shortcut para obter configuração"""
    return get_config_loader().get_config()

