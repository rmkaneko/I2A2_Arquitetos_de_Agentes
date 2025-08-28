"""
Agente Orquestrador - Sistema de Processamento VR
Responsável por coordenar todo o fluxo de trabalho
Autor: Manus AI
Data: 27/08/2025
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import traceback

# Adicionar o diretório pai ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_loader import get_config_loader
from utils.logger import VRLogger
from agentes.extrator_validador import ExtratorValidador
from agentes.consolidador_regras import ConsolidadorRegras
from agentes.gerador_relatorio import GeradorRelatorio


class OrquestradorVR:
    """Agente orquestrador principal do sistema de processamento VR"""
    
    def __init__(self, config_path: str = None):
        """Inicializa o orquestrador"""
        
        # Carregar configurações
        self.config_loader = get_config_loader(config_path)
        self.config = self.config_loader.get_config()
        
        # Inicializar logger
        self.logger = VRLogger(config_path or self._get_default_config_path())
        
        # Inicializar agentes especializados
        self.extrator_validador = ExtratorValidador(self.logger)
        self.consolidador_regras = ConsolidadorRegras(self.logger)
        self.gerador_relatorio = GeradorRelatorio(self.logger)
        
        # Estado do processamento
        self.dados_validados = None
        self.dados_consolidados = None
        self.arquivo_relatorio_gerado = None
        
    def _get_default_config_path(self) -> str:
        """Retorna o caminho padrão do arquivo de configuração"""
        return str(Path(__file__).parent.parent / "config" / "config.yaml")
    
    def executar_processamento_completo(self) -> Dict[str, Any]:
        """Executa o processamento completo do VR"""
        
        try:
            self.logger.log_info("=== INICIANDO PROCESSAMENTO COMPLETO VR ===")
            self.logger.log_info(f"Sistema: {self.config['sistema']['nome']} v{self.config['sistema']['versao']}")
            self.logger.log_info(f"Competência: {self.config['regras_negocio']['competencia_referencia']}")
            
            # Fase 1: Validar ambiente e preparar diretórios
            self._fase_1_preparacao()
            
            # Fase 2: Extração e validação de dados
            self._fase_2_extracao_validacao()
            
            # Fase 3: Consolidação e aplicação de regras
            self._fase_3_consolidacao_regras()
            
            # Fase 4: Geração de relatórios
            self._fase_4_geracao_relatorios()
            
            # Fase 5: Finalização e estatísticas
            resultado = self._fase_5_finalizacao()
            
            self.logger.log_info("=== PROCESSAMENTO CONCLUÍDO COM SUCESSO ===")
            return resultado
            
        except Exception as e:
            self.logger.log_error(f"Erro durante o processamento: {str(e)}")
            self.logger.log_error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _fase_1_preparacao(self):
        """Fase 1: Preparação do ambiente"""
        self.logger.log_info("FASE 1: Preparação do ambiente")
        
        # Validar e criar diretórios necessários
        self.config_loader.validate_directories()
        self.logger.log_validacao("Criação de diretórios", True, "Todos os diretórios criados/validados")
        
        # Verificar arquivos obrigatórios
        arquivos_obrigatorios = ['ativos', 'sindicato_valor', 'dias_uteis']
        for arquivo_key in arquivos_obrigatorios:
            file_path = self.config_loader.get_file_path(arquivo_key)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {file_path}")
        
        self.logger.log_validacao("Arquivos obrigatórios", True, "Todos os arquivos obrigatórios encontrados")
        
        # Limpar arquivos de execuções anteriores (garantir idempotência)
        self._limpar_arquivos_anteriores()
        
        self.logger.log_info("Fase 1 concluída: Ambiente preparado")
    
    def _limpar_arquivos_anteriores(self):
        """Limpa arquivos de execuções anteriores para garantir idempotência"""
        diretorio_saida = Path(self.config['arquivos']['diretorio_saida'])
        
        # Listar arquivos existentes
        arquivos_existentes = list(diretorio_saida.glob("*.xlsx"))
        
        if arquivos_existentes:
            self.logger.log_info(f"Removendo {len(arquivos_existentes)} arquivos de execuções anteriores")
            for arquivo in arquivos_existentes:
                try:
                    arquivo.unlink()
                except Exception as e:
                    self.logger.log_warning(f"Não foi possível remover {arquivo}: {e}")
    
    def _fase_2_extracao_validacao(self):
        """Fase 2: Extração e validação de dados"""
        self.logger.log_info("FASE 2: Extração e validação de dados")
        
        # Executar extração e validação
        self.dados_validados = self.extrator_validador.executar()
        
        # Verificar se dados essenciais foram carregados
        if not self.dados_validados:
            raise ValueError("Nenhum dado foi carregado durante a extração")
        
        if 'ativos' not in self.dados_validados:
            raise ValueError("Base de colaboradores ativos não foi carregada")
        
        # Log de estatísticas da extração
        stats_extracao = self.extrator_validador.get_estatisticas()
        self.logger.log_info(f"Estatísticas de extração: {stats_extracao}")
        
        self.logger.log_info("Fase 2 concluída: Dados extraídos e validados")
    
    def _fase_3_consolidacao_regras(self):
        """Fase 3: Consolidação e aplicação de regras de negócio"""
        self.logger.log_info("FASE 3: Consolidação e aplicação de regras de negócio")
        
        # Executar consolidação e regras
        self.dados_consolidados = self.consolidador_regras.executar(self.dados_validados)
        
        # Verificar se consolidação foi bem-sucedida
        if self.dados_consolidados is None or self.dados_consolidados.empty:
            raise ValueError("Falha na consolidação dos dados")
        
        # Log de estatísticas da consolidação
        stats_consolidacao = self.consolidador_regras.get_estatisticas()
        self.logger.log_info(f"Estatísticas de consolidação: {stats_consolidacao}")
        
        self.logger.log_info("Fase 3 concluída: Dados consolidados e regras aplicadas")
    
    def _fase_4_geracao_relatorios(self):
        """Fase 4: Geração de relatórios"""
        self.logger.log_info("FASE 4: Geração de relatórios")
        
        # Obter estatísticas para o relatório
        stats_consolidacao = self.consolidador_regras.get_estatisticas()
        
        # Gerar relatório principal
        self.arquivo_relatorio_gerado = self.gerador_relatorio.executar(
            self.dados_consolidados, 
            stats_consolidacao
        )
        
        # Gerar relatório de exclusões (opcional)
        try:
            arquivo_exclusoes = self.gerador_relatorio.gerar_relatorio_exclusoes(self.dados_consolidados)
            if arquivo_exclusoes:
                self.logger.log_info(f"Relatório de exclusões gerado: {arquivo_exclusoes}")
        except Exception as e:
            self.logger.log_warning(f"Erro ao gerar relatório de exclusões: {e}")
        
        self.logger.log_info("Fase 4 concluída: Relatórios gerados")
    
    def _fase_5_finalizacao(self) -> Dict[str, Any]:
        """Fase 5: Finalização e geração de estatísticas"""
        self.logger.log_info("FASE 5: Finalização do processamento")
        
        # Obter estatísticas finais
        stats_finais = self.consolidador_regras.get_estatisticas()
        
        # Finalizar logs
        self.logger.finalizar_processamento(
            stats_finais['colaboradores_elegiveis'],
            stats_finais['valor_total']
        )
        
        # Preparar resultado final
        resultado = {
            'sucesso': True,
            'timestamp': datetime.now().isoformat(),
            'competencia': self.config['regras_negocio']['competencia_referencia'],
            'arquivo_relatorio': self.arquivo_relatorio_gerado,
            'arquivos_log': self.logger.get_log_files(),
            'estatisticas': stats_finais,
            'resumo': {
                'total_colaboradores': stats_finais['total_colaboradores'],
                'colaboradores_elegiveis': stats_finais['colaboradores_elegiveis'],
                'colaboradores_excluidos': stats_finais['colaboradores_excluidos'],
                'valor_total': stats_finais['valor_total'],
                'custo_empresa': stats_finais['custo_total_empresa'],
                'desconto_colaboradores': stats_finais['desconto_total_colaboradores']
            }
        }
        
        self.logger.log_info("Fase 5 concluída: Processamento finalizado")
        return resultado
    
    def executar_apenas_validacao(self) -> Dict[str, Any]:
        """Executa apenas a validação dos dados sem processamento completo"""
        
        try:
            self.logger.log_info("=== EXECUTANDO APENAS VALIDAÇÃO ===")
            
            # Preparar ambiente
            self._fase_1_preparacao()
            
            # Executar validação
            self._fase_2_extracao_validacao()
            
            # Retornar estatísticas de validação
            stats_validacao = self.extrator_validador.get_estatisticas()
            
            resultado = {
                'sucesso': True,
                'tipo': 'validacao_apenas',
                'timestamp': datetime.now().isoformat(),
                'estatisticas_validacao': stats_validacao,
                'arquivos_processados': list(self.dados_validados.keys()),
                'total_registros': sum(len(df) for df in self.dados_validados.values())
            }
            
            self.logger.log_info("=== VALIDAÇÃO CONCLUÍDA ===")
            return resultado
            
        except Exception as e:
            self.logger.log_error(f"Erro durante a validação: {str(e)}")
            raise
    
    def get_configuracao_atual(self) -> Dict[str, Any]:
        """Retorna a configuração atual do sistema"""
        return self.config
    
    def atualizar_configuracao(self, nova_config: Dict[str, Any]):
        """Atualiza configuração do sistema"""
        # Validar nova configuração
        # (implementar validações específicas se necessário)
        
        # Recarregar configuração
        self.config_loader.reload_config()
        self.config = self.config_loader.get_config()
        
        self.logger.log_info("Configuração atualizada com sucesso")
    
    def verificar_integridade_dados(self) -> Dict[str, Any]:
        """Verifica integridade dos dados de entrada"""
        
        resultado_integridade = {
            'arquivos_encontrados': {},
            'arquivos_faltantes': [],
            'problemas_estrutura': [],
            'warnings': []
        }
        
        # Verificar cada arquivo
        for arquivo_key, nome_arquivo in self.config['arquivos_entrada'].items():
            file_path = self.config_loader.get_file_path(arquivo_key)
            
            if os.path.exists(file_path):
                try:
                    # Tentar ler arquivo para verificar integridade
                    import pandas as pd
                    df = pd.read_excel(file_path)
                    
                    resultado_integridade['arquivos_encontrados'][arquivo_key] = {
                        'nome': nome_arquivo,
                        'caminho': file_path,
                        'linhas': len(df),
                        'colunas': list(df.columns),
                        'tamanho_mb': os.path.getsize(file_path) / (1024 * 1024)
                    }
                    
                except Exception as e:
                    resultado_integridade['problemas_estrutura'].append({
                        'arquivo': arquivo_key,
                        'erro': str(e)
                    })
            else:
                resultado_integridade['arquivos_faltantes'].append({
                    'arquivo': arquivo_key,
                    'caminho_esperado': file_path
                })
        
        return resultado_integridade


def main():
    """Função principal para execução via linha de comando"""
    
    print("=== Sistema de Processamento VR ===")
    print("Autor: Manus AI")
    print("Data: 27/08/2025")
    print()
    
    try:
        # Inicializar orquestrador
        orquestrador = OrquestradorVR()
        
        # Executar processamento completo
        resultado = orquestrador.executar_processamento_completo()
        
        # Exibir resumo
        print("PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print(f"Arquivo gerado: {resultado['arquivo_relatorio']}")
        print(f"Colaboradores elegíveis: {resultado['resumo']['colaboradores_elegiveis']}")
        print(f"Valor total: R$ {resultado['resumo']['valor_total']:,.2f}")
        print(f"Logs disponíveis em: {resultado['arquivos_log']['audit']}")
        
    except Exception as e:
        print(f"ERRO: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

