"""
Agente Extrator/Validador - Sistema de Processamento VR
Responsável por extrair e validar dados dos arquivos Excel de entrada
Autor: Manus AI
Data: 27/08/2025
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np
from datetime import datetime
import os

from utils.config_loader import get_config_loader
from utils.logger import VRLogger


class ExtratorValidador:
    """Agente responsável pela extração e validação de dados"""
    
    def __init__(self, logger: VRLogger):
        """Inicializa o agente extrator/validador"""
        self.logger = logger
        self.config_loader = get_config_loader()
        self.config = self.config_loader.get_config()
        
        # Esquemas de validação para cada arquivo
        self.schemas = self._definir_schemas()
        
        # Dados extraídos e validados
        self.dados_validados = {}
        
    def _definir_schemas(self) -> Dict[str, Dict]:
        """Define esquemas de validação para cada arquivo"""
        return {
            'ativos': {
                'colunas_obrigatorias': ['MATRICULA', 'EMPRESA', 'TITULO DO CARGO', 'DESC. SITUACAO', 'Sindicato'],
                'tipos': {
                    'MATRICULA': 'int64',
                    'EMPRESA': 'int64',
                    'TITULO DO CARGO': 'object',
                    'DESC. SITUACAO': 'object',
                    'Sindicato': 'object'
                }
            },
            'admissoes': {
                'colunas_obrigatorias': ['MATRICULA', 'Admissão', 'Cargo'],
                'tipos': {
                    'MATRICULA': 'int64',
                    'Admissão': 'datetime64[ns]',
                    'Cargo': 'object'
                }
            },
            'afastamentos': {
                'colunas_obrigatorias': ['MATRICULA', 'DESC. SITUACAO'],
                'tipos': {
                    'MATRICULA': 'int64',
                    'DESC. SITUACAO': 'object'
                }
            },
            'aprendizes': {
                'colunas_obrigatorias': ['MATRICULA', 'TITULO DO CARGO'],
                'tipos': {
                    'MATRICULA': 'int64',
                    'TITULO DO CARGO': 'object'
                }
            },
            'dias_uteis': {
                'colunas_obrigatorias': ['SINDICADO', 'DIAS UTEIS'],
                'tipos': {
                    'SINDICADO': 'object',
                    'DIAS UTEIS': 'int64'
                }
            },
            'sindicato_valor': {
                'colunas_obrigatorias': ['ESTADO', 'VALOR'],
                'tipos': {
                    'ESTADO': 'object',
                    'VALOR': 'float64'
                }
            },
            'desligados': {
                'colunas_obrigatorias': ['MATRICULA', 'DATA DEMISSÃO', 'COMUNICADO DE DESLIGAMENTO'],
                'tipos': {
                    'MATRICULA': 'int64',
                    'DATA DEMISSÃO': 'datetime64[ns]',
                    'COMUNICADO DE DESLIGAMENTO': 'object'
                }
            },
            'estagios': {
                'colunas_obrigatorias': ['MATRICULA', 'TITULO DO CARGO'],
                'tipos': {
                    'MATRICULA': 'int64',
                    'TITULO DO CARGO': 'object'
                }
            },
            'exterior': {
                'colunas_obrigatorias': ['MATRICULA', 'Valor'],
                'tipos': {
                    'MATRICULA': 'int64',
                    'Valor': 'float64'
                }
            },
            'ferias': {
                'colunas_obrigatorias': ['MATRICULA', 'DESC. SITUACAO', 'DIAS DE FÉRIAS'],
                'tipos': {
                    'MATRICULA': 'int64',
                    'DESC. SITUACAO': 'object',
                    'DIAS DE FÉRIAS': 'int64'
                }
            }
        }
    
    def executar(self) -> Dict[str, pd.DataFrame]:
        """Executa o processo de extração e validação"""
        self.logger.log_info("Iniciando processo de extração e validação de dados")
        
        # Validar existência dos arquivos
        self._validar_existencia_arquivos()
        
        # Processar cada arquivo
        arquivos_para_processar = [
            'ativos', 'admissoes', 'afastamentos', 'aprendizes',
            'dias_uteis', 'sindicato_valor', 'desligados', 
            'estagios', 'exterior', 'ferias'
        ]
        
        for arquivo_key in arquivos_para_processar:
            try:
                df = self._processar_arquivo(arquivo_key)
                if df is not None:
                    self.dados_validados[arquivo_key] = df
                    self.logger.log_arquivo_processado(
                        self.config['arquivos_entrada'][arquivo_key], 
                        len(df)
                    )
            except Exception as e:
                self.logger.log_error(f"Erro ao processar arquivo {arquivo_key}: {str(e)}")
                raise
        
        # Validações cruzadas
        self._executar_validacoes_cruzadas()
        
        self.logger.log_info("Processo de extração e validação concluído com sucesso")
        return self.dados_validados
    
    def _validar_existencia_arquivos(self):
        """Valida se todos os arquivos necessários existem"""
        arquivos_obrigatorios = ['ativos', 'sindicato_valor', 'dias_uteis']
        
        for arquivo_key in arquivos_obrigatorios:
            file_path = self.config_loader.get_file_path(arquivo_key)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {file_path}")
        
        self.logger.log_validacao("Existência de arquivos obrigatórios", True, "Todos os arquivos obrigatórios encontrados")
    
    def _processar_arquivo(self, arquivo_key: str) -> pd.DataFrame:
        """Processa um arquivo específico"""
        file_path = self.config_loader.get_file_path(arquivo_key)
        
        if not os.path.exists(file_path):
            self.logger.log_warning(f"Arquivo opcional não encontrado: {file_path}")
            return None
        
        try:
            # Ler arquivo Excel
            df = pd.read_excel(file_path)
            
            # Aplicar limpeza e normalização primeiro
            df = self._limpar_dados(df, arquivo_key)
            
            # Depois aplicar validações específicas do arquivo
            df = self._validar_estrutura_arquivo(df, arquivo_key)
            df = self._converter_tipos(df, arquivo_key)
            
            return df
            
        except Exception as e:
            self.logger.log_error(f"Erro ao processar {file_path}: {str(e)}")
            raise
    
    def _validar_estrutura_arquivo(self, df: pd.DataFrame, arquivo_key: str) -> pd.DataFrame:
        """Valida a estrutura de um arquivo"""
        schema = self.schemas.get(arquivo_key, {})
        colunas_obrigatorias = schema.get('colunas_obrigatorias', [])
        
        # Verificar colunas obrigatórias
        colunas_faltantes = set(colunas_obrigatorias) - set(df.columns)
        if colunas_faltantes:
            raise ValueError(f"Colunas obrigatórias faltantes em {arquivo_key}: {colunas_faltantes}")
        
        # Verificar se há dados
        if df.empty:
            self.logger.log_warning(f"Arquivo {arquivo_key} está vazio")
            return df
        
        # Remover linhas completamente vazias
        df = df.dropna(how='all')
        
        self.logger.log_validacao(f"Estrutura do arquivo {arquivo_key}", True, f"{len(df)} registros válidos")
        return df
    
    def _limpar_dados(self, df: pd.DataFrame, arquivo_key: str) -> pd.DataFrame:
        """Limpa e normaliza os dados"""
        df_limpo = df.copy()
        
        # Limpar nomes das colunas (remover espaços extras)
        df_limpo.columns = df_limpo.columns.str.strip()
        
        # Limpar strings (remover espaços extras, etc.)
        for col in df_limpo.select_dtypes(include=['object']).columns:
            df_limpo[col] = df_limpo[col].astype(str).str.strip()
            df_limpo[col] = df_limpo[col].replace('nan', np.nan)
        
        # Tratamentos específicos por arquivo
        if arquivo_key == 'exterior':
            # Renomear coluna Cadastro para MATRICULA para padronização
            if 'Cadastro' in df_limpo.columns:
                df_limpo = df_limpo.rename(columns={'Cadastro': 'MATRICULA'})
        
        elif arquivo_key == 'dias_uteis':
            # Tratar estrutura específica do arquivo de dias úteis
            if 'BASE DIAS UTEIS' in str(df_limpo.columns[0]):
                # A primeira linha contém os cabeçalhos reais
                new_columns = df_limpo.iloc[0].tolist()
                df_limpo.columns = new_columns
                df_limpo = df_limpo.iloc[1:].reset_index(drop=True)
                
            # Renomear colunas se necessário
            if 'Unnamed: 1' in df_limpo.columns:
                df_limpo = df_limpo.rename(columns={'Unnamed: 1': 'DIAS UTEIS'})
            
            # Garantir que temos as colunas corretas
            if 'SINDICADO' not in df_limpo.columns and df_limpo.columns[0] != 'SINDICADO':
                df_limpo = df_limpo.rename(columns={df_limpo.columns[0]: 'SINDICADO'})
            if 'DIAS UTEIS' not in df_limpo.columns and len(df_limpo.columns) > 1:
                df_limpo = df_limpo.rename(columns={df_limpo.columns[1]: 'DIAS UTEIS'})
        
        elif arquivo_key == 'sindicato_valor':
            # Limpar nome da coluna ESTADO que tem espaços extras
            for col in df_limpo.columns:
                if 'ESTADO' in col:
                    df_limpo = df_limpo.rename(columns={col: 'ESTADO'})
                    break
            
            # Remover linhas vazias ou com valores inválidos
            df_limpo = df_limpo.dropna(subset=['ESTADO', 'VALOR'])
            df_limpo = df_limpo[df_limpo['ESTADO'].str.strip() != '']
        
        return df_limpo
    
    def _converter_tipos(self, df: pd.DataFrame, arquivo_key: str) -> pd.DataFrame:
        """Converte tipos de dados conforme schema"""
        schema = self.schemas.get(arquivo_key, {})
        tipos = schema.get('tipos', {})
        
        df_convertido = df.copy()
        
        for coluna, tipo in tipos.items():
            if coluna in df_convertido.columns:
                try:
                    if tipo == 'datetime64[ns]':
                        df_convertido[coluna] = pd.to_datetime(df_convertido[coluna], errors='coerce')
                    elif tipo == 'int64':
                        df_convertido[coluna] = pd.to_numeric(df_convertido[coluna], errors='coerce').astype('Int64')
                    elif tipo == 'float64':
                        df_convertido[coluna] = pd.to_numeric(df_convertido[coluna], errors='coerce')
                    
                    # Verificar se houve muitas conversões falhadas
                    if df_convertido[coluna].isna().sum() > len(df_convertido) * 0.5:
                        self.logger.log_warning(f"Muitos valores inválidos na coluna {coluna} do arquivo {arquivo_key}")
                        
                except Exception as e:
                    self.logger.log_warning(f"Erro ao converter coluna {coluna} em {arquivo_key}: {str(e)}")
        
        return df_convertido
    
    def _executar_validacoes_cruzadas(self):
        """Executa validações que dependem de múltiplos arquivos"""
        
        # Validar consistência de matrículas
        self._validar_consistencia_matriculas()
        
        # Validar valores de sindicatos
        self._validar_valores_sindicatos()
        
        # Validar dias úteis
        self._validar_dias_uteis()
    
    def _validar_consistencia_matriculas(self):
        """Valida consistência de matrículas entre arquivos"""
        if 'ativos' not in self.dados_validados:
            return
        
        matriculas_ativas = set(self.dados_validados['ativos']['MATRICULA'].dropna())
        
        # Verificar se matrículas em outros arquivos existem na base de ativos
        arquivos_para_verificar = ['admissoes', 'afastamentos', 'desligados', 'ferias']
        
        for arquivo_key in arquivos_para_verificar:
            if arquivo_key in self.dados_validados:
                df = self.dados_validados[arquivo_key]
                col_matricula = 'MATRICULA' if 'MATRICULA' in df.columns else 'Cadastro'
                
                if col_matricula in df.columns:
                    matriculas_arquivo = set(df[col_matricula].dropna())
                    matriculas_inexistentes = matriculas_arquivo - matriculas_ativas
                    
                    if matriculas_inexistentes:
                        self.logger.log_warning(
                            f"Matrículas em {arquivo_key} não encontradas na base de ativos: {matriculas_inexistentes}"
                        )
        
        self.logger.log_validacao("Consistência de matrículas", True, "Validação de matrículas concluída")
    
    def _validar_valores_sindicatos(self):
        """Valida se todos os sindicatos têm valores definidos"""
        if 'ativos' not in self.dados_validados or 'sindicato_valor' not in self.dados_validados:
            return
        
        sindicatos_ativos = set(self.dados_validados['ativos']['Sindicato'].dropna().unique())
        sindicatos_com_valor = set(self.dados_validados['sindicato_valor']['ESTADO'].dropna().unique())
        
        # Aplicar mapeamento de sindicatos
        sindicatos_mapeados = set()
        for sindicato in sindicatos_ativos:
            sindicato_normalizado = self.config_loader.get_sindicato_normalizado(sindicato)
            sindicatos_mapeados.add(sindicato_normalizado)
        
        sindicatos_sem_valor = sindicatos_mapeados - sindicatos_com_valor
        
        if sindicatos_sem_valor:
            self.logger.log_error(f"Sindicatos sem valor definido: {sindicatos_sem_valor}")
            raise ValueError(f"Sindicatos sem valor definido: {sindicatos_sem_valor}")
        
        self.logger.log_validacao("Valores de sindicatos", True, "Todos os sindicatos possuem valores definidos")
    
    def _validar_dias_uteis(self):
        """Valida configuração de dias úteis"""
        if 'dias_uteis' not in self.dados_validados:
            return
        
        df_dias = self.dados_validados['dias_uteis']
        
        # Verificar se há dias úteis válidos
        dias_invalidos = df_dias[
            (df_dias['DIAS UTEIS'] < self.config['validacoes']['dias_uteis_minimo']) |
            (df_dias['DIAS UTEIS'] > self.config['validacoes']['dias_uteis_maximo'])
        ]
        
        if not dias_invalidos.empty:
            self.logger.log_warning(f"Dias úteis fora da faixa esperada: {dias_invalidos.to_dict('records')}")
        
        self.logger.log_validacao("Dias úteis", True, f"Configuração de dias úteis validada para {len(df_dias)} sindicatos")
    
    def get_dados_validados(self) -> Dict[str, pd.DataFrame]:
        """Retorna os dados validados"""
        return self.dados_validados
    
    def get_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas dos dados processados"""
        stats = {}
        
        for arquivo_key, df in self.dados_validados.items():
            stats[arquivo_key] = {
                'total_registros': len(df),
                'colunas': list(df.columns),
                'registros_com_dados_faltantes': df.isnull().any(axis=1).sum(),
                'memoria_utilizada': df.memory_usage(deep=True).sum()
            }
        
        return stats

