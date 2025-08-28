"""
Sistema de Logging Estruturado para Processamento VR
Autor: Manus AI
Data: 27/08/2025
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import yaml


class VRLogger:
    """Sistema de logging estruturado com suporte a auditoria"""
    
    def __init__(self, config_path: str):
        """Inicializa o sistema de logging"""
        self.config = self._load_config(config_path)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configurar diretório de logs
        self.log_dir = Path(self.config['arquivos']['diretorio_logs'])
        self.log_dir.mkdir(exist_ok=True)
        
        # Inicializar loggers
        self._setup_technical_logger()
        self._setup_audit_logger()
        
        # Estatísticas de processamento
        self.stats = {
            'inicio_processamento': datetime.now(),
            'arquivos_processados': 0,
            'colaboradores_processados': 0,
            'colaboradores_elegiveis': 0,
            'colaboradores_excluidos': 0,
            'exclusoes_por_categoria': {},
            'calculos_especiais': {},
            'validacoes_realizadas': [],
            'warnings': [],
            'errors': []
        }
        
    def _load_config(self, config_path: str) -> Dict:
        """Carrega configuração do arquivo YAML"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_technical_logger(self):
        """Configura logger técnico (formato estruturado)"""
        log_file = self.log_dir / self.config['logging']['arquivo_log'].format(
            timestamp=self.timestamp
        )
        
        self.technical_logger = logging.getLogger('vr_technical')
        self.technical_logger.setLevel(getattr(logging, self.config['logging']['nivel']))
        
        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(self.config['logging']['formato'])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.technical_logger.addHandler(file_handler)
        self.technical_logger.addHandler(console_handler)
        
    def _setup_audit_logger(self):
        """Configura logger de auditoria (formato legível)"""
        self.audit_file = self.log_dir / self.config['logging']['arquivo_auditoria'].format(
            timestamp=self.timestamp
        )
        
        # Inicializar arquivo de auditoria
        with open(self.audit_file, 'w', encoding='utf-8') as f:
            f.write(f"=== RELATÓRIO DE PROCESSAMENTO VR ===\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Competência: {self.config['regras_negocio']['competencia_referencia']}\n\n")
    
    def log_info(self, message: str, extra_data: Dict = None):
        """Log de informação"""
        self.technical_logger.info(message)
        if extra_data:
            try:
                # Converter datetime para string antes de serializar
                serializable_data = self._make_json_serializable(extra_data)
                self.technical_logger.debug(f"Dados extras: {json.dumps(serializable_data, ensure_ascii=False)}")
            except Exception as e:
                self.technical_logger.debug(f"Dados extras (não serializável): {str(extra_data)}")
    
    def _make_json_serializable(self, obj):
        """Converte objetos para formato serializável em JSON"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'item'):  # numpy types
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy arrays
            return obj.tolist()
        else:
            return obj
    
    def log_warning(self, message: str, extra_data: Dict = None):
        """Log de warning"""
        self.technical_logger.warning(message)
        self.stats['warnings'].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'data': extra_data
        })
        
    def log_error(self, message: str, extra_data: Dict = None):
        """Log de erro"""
        self.technical_logger.error(message)
        self.stats['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'data': extra_data
        })
    
    def log_debug(self, message: str, extra_data: Dict = None):
        """Log de debug"""
        self.technical_logger.debug(message)
        if extra_data:
            self.technical_logger.debug(f"Debug data: {json.dumps(extra_data, ensure_ascii=False)}")
    
    def log_arquivo_processado(self, nome_arquivo: str, num_registros: int):
        """Log específico para arquivo processado"""
        self.stats['arquivos_processados'] += 1
        message = f"Arquivo processado: {nome_arquivo} - {num_registros} registros"
        self.log_info(message)
        
    def log_exclusao(self, matricula: int, motivo: str, categoria: str):
        """Log específico para exclusão de colaborador"""
        self.stats['colaboradores_excluidos'] += 1
        
        if categoria not in self.stats['exclusoes_por_categoria']:
            self.stats['exclusoes_por_categoria'][categoria] = 0
        self.stats['exclusoes_por_categoria'][categoria] += 1
        
        message = f"Colaborador excluído - Matrícula: {matricula}, Motivo: {motivo}, Categoria: {categoria}"
        self.log_info(message)
        
    def log_calculo_especial(self, matricula: int, tipo: str, detalhes: str):
        """Log específico para cálculos especiais"""
        if tipo not in self.stats['calculos_especiais']:
            self.stats['calculos_especiais'][tipo] = 0
        self.stats['calculos_especiais'][tipo] += 1
        
        message = f"Cálculo especial - Matrícula: {matricula}, Tipo: {tipo}, Detalhes: {detalhes}"
        self.log_info(message)
        
    def log_validacao(self, tipo_validacao: str, resultado: bool, detalhes: str = ""):
        """Log específico para validações"""
        self.stats['validacoes_realizadas'].append({
            'tipo': tipo_validacao,
            'resultado': resultado,
            'detalhes': detalhes,
            'timestamp': datetime.now().isoformat()
        })
        
        status = "✓" if resultado else "✗"
        message = f"Validação {status} {tipo_validacao}: {detalhes}"
        self.log_info(message)
        
    def finalizar_processamento(self, colaboradores_elegiveis: int, valor_total: float):
        """Finaliza o processamento e gera relatório de auditoria"""
        self.stats['fim_processamento'] = datetime.now()
        self.stats['colaboradores_elegiveis'] = colaboradores_elegiveis
        self.stats['colaboradores_processados'] = colaboradores_elegiveis + self.stats['colaboradores_excluidos']
        
        # Gerar relatório de auditoria legível
        self._gerar_relatorio_auditoria(valor_total)
        
        # Log final técnico
        self.log_info("Processamento finalizado com sucesso", self.stats)
        
    def _gerar_relatorio_auditoria(self, valor_total: float):
        """Gera relatório de auditoria em formato legível"""
        duracao = self.stats['fim_processamento'] - self.stats['inicio_processamento']
        
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write("RESUMO GERAL:\n")
            f.write(f"- Total de colaboradores processados: {self.stats['colaboradores_processados']}\n")
            f.write(f"- Colaboradores elegíveis para VR: {self.stats['colaboradores_elegiveis']}\n")
            f.write(f"- Colaboradores excluídos: {self.stats['colaboradores_excluidos']}\n")
            f.write(f"- Valor total processado: R$ {valor_total:,.2f}\n")
            f.write(f"- Tempo de processamento: {duracao}\n\n")
            
            if self.stats['exclusoes_por_categoria']:
                f.write("EXCLUSÕES POR CATEGORIA:\n")
                for categoria, count in self.stats['exclusoes_por_categoria'].items():
                    f.write(f"- {categoria}: {count} colaboradores\n")
                f.write("\n")
            
            if self.stats['calculos_especiais']:
                f.write("CÁLCULOS ESPECIAIS:\n")
                for tipo, count in self.stats['calculos_especiais'].items():
                    f.write(f"- {tipo}: {count} colaboradores\n")
                f.write("\n")
            
            f.write("VALIDAÇÕES REALIZADAS:\n")
            for validacao in self.stats['validacoes_realizadas']:
                status = "✓" if validacao['resultado'] else "⚠"
                f.write(f"{status} {validacao['tipo']}")
                if validacao['detalhes']:
                    f.write(f": {validacao['detalhes']}")
                f.write("\n")
            f.write("\n")
            
            f.write("ARQUIVOS PROCESSADOS:\n")
            for arquivo in self.config['arquivos_entrada'].values():
                f.write(f"✓ {arquivo}\n")
            f.write("\n")
            
            if self.stats['warnings']:
                f.write("AVISOS:\n")
                for warning in self.stats['warnings']:
                    f.write(f"⚠ {warning['message']}\n")
                f.write("\n")
            
            if self.stats['errors']:
                f.write("ERROS:\n")
                for error in self.stats['errors']:
                    f.write(f"✗ {error['message']}\n")
                f.write("\n")
            
            f.write("=== FIM DO RELATÓRIO ===\n")
    
    def get_log_files(self) -> Dict[str, str]:
        """Retorna caminhos dos arquivos de log gerados"""
        return {
            'technical': str(self.log_dir / self.config['logging']['arquivo_log'].format(
                timestamp=self.timestamp
            )),
            'audit': str(self.audit_file)
        }

