"""
Agente de Consolidação e Regras - Sistema de Processamento VR
Responsável por consolidar dados e aplicar regras de negócio
Autor: Manus AI
Data: 27/08/2025
"""

import pandas as pd
from typing import Dict, List, Tuple, Any
import numpy as np
from datetime import datetime, date
import calendar

from utils.config_loader import get_config_loader
from utils.logger import VRLogger


class ConsolidadorRegras:
    """Agente responsável pela consolidação de dados e aplicação de regras de negócio"""
    
    def __init__(self, logger: VRLogger):
        """Inicializa o agente consolidador de regras"""
        self.logger = logger
        self.config_loader = get_config_loader()
        self.config = self.config_loader.get_config()
        
        # DataFrame consolidado final
        self.df_consolidado = None
        
        # Bases auxiliares
        self.base_sindicatos_valores = None
        self.base_dias_uteis = None
        
    def executar(self, dados_validados: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Executa o processo de consolidação e aplicação de regras"""
        self.logger.log_info("Iniciando processo de consolidação e aplicação de regras de negócio")
        
        # Preparar bases auxiliares
        self._preparar_bases_auxiliares(dados_validados)
        
        # Consolidar dados principais
        self.df_consolidado = self._consolidar_dados_principais(dados_validados)
        
        # Aplicar regras de negócio sequencialmente
        self._aplicar_regras_exclusao_cargo(dados_validados)
        self._aplicar_regras_afastamentos(dados_validados)
        self._aplicar_regras_ferias(dados_validados)
        self._aplicar_regras_desligamento(dados_validados)
        self._aplicar_regras_exterior(dados_validados)
        self._aplicar_regras_admissao(dados_validados)
        
        # Calcular valores de VR
        self._calcular_valores_vr()
        
        # Gerar estatísticas finais
        self._gerar_estatisticas_finais()
        
        self.logger.log_info("Processo de consolidação e regras concluído com sucesso")
        return self.df_consolidado
    
    def _preparar_bases_auxiliares(self, dados_validados: Dict[str, pd.DataFrame]):
        """Prepara bases auxiliares para cálculos"""
        
        # Base de valores por sindicato
        if 'sindicato_valor' in dados_validados:
            self.base_sindicatos_valores = dados_validados['sindicato_valor'].copy()
            self.logger.log_info(f"Base de valores carregada: {len(self.base_sindicatos_valores)} sindicatos")
        
        # Base de dias úteis por sindicato
        if 'dias_uteis' in dados_validados:
            self.base_dias_uteis = dados_validados['dias_uteis'].copy()
            # Normalizar nomes de sindicatos
            self.base_dias_uteis['SINDICADO_NORMALIZADO'] = self.base_dias_uteis['SINDICADO'].apply(
                lambda x: self.config_loader.get_sindicato_normalizado(x)
            )
            self.logger.log_info(f"Base de dias úteis carregada: {len(self.base_dias_uteis)} sindicatos")
    
    def _consolidar_dados_principais(self, dados_validados: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Consolida dados principais dos colaboradores ativos"""
        
        if 'ativos' not in dados_validados:
            raise ValueError("Base de colaboradores ativos não encontrada")
        
        # Começar com base de ativos
        df = dados_validados['ativos'].copy()
        
        # Adicionar informações de admissão se disponível
        if 'admissoes' in dados_validados:
            df_admissoes = dados_validados['admissoes'][['MATRICULA', 'Admissão']].copy()
            df = df.merge(df_admissoes, on='MATRICULA', how='left')
        
        # Inicializar colunas de controle
        df['elegivel'] = True
        df['motivo_exclusao'] = ''
        df['dias_ferias'] = 0
        df['dias_afastamento'] = 0
        df['data_demissao'] = pd.NaT
        df['comunicado_desligamento'] = ''
        df['valor_exterior'] = 0.0
        df['observacoes'] = ''
        
        # Normalizar nomes de sindicatos
        df['sindicato_normalizado'] = df['Sindicato'].apply(
            lambda x: self.config_loader.get_sindicato_normalizado(x)
        )
        
        # Adicionar informações de valores e dias úteis por sindicato
        df = self._adicionar_info_sindicatos(df)
        
        self.logger.log_info(f"Dados principais consolidados: {len(df)} colaboradores")
        return df
    
    def _adicionar_info_sindicatos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona informações de valores e dias úteis por sindicato"""
        
        # Merge com valores de sindicatos
        if self.base_sindicatos_valores is not None:
            df = df.merge(
                self.base_sindicatos_valores[['ESTADO', 'VALOR']],
                left_on='sindicato_normalizado',
                right_on='ESTADO',
                how='left'
            )
            df = df.rename(columns={'VALOR': 'valor_diario_vr'})
            df = df.drop(columns=['ESTADO'], errors='ignore')
        
        # Merge com dias úteis
        if self.base_dias_uteis is not None:
            df = df.merge(
                self.base_dias_uteis[['SINDICADO_NORMALIZADO', 'DIAS UTEIS']],
                left_on='sindicato_normalizado',
                right_on='SINDICADO_NORMALIZADO',
                how='left'
            )
            df = df.rename(columns={'DIAS UTEIS': 'dias_uteis_sindicato'})
            df = df.drop(columns=['SINDICADO_NORMALIZADO'], errors='ignore')
        
        # Verificar se há colaboradores sem informações de sindicato
        sem_valor = df['valor_diario_vr'].isna().sum()
        sem_dias = df['dias_uteis_sindicato'].isna().sum()
        
        if sem_valor > 0:
            self.logger.log_warning(f"{sem_valor} colaboradores sem valor de VR definido")
        if sem_dias > 0:
            self.logger.log_warning(f"{sem_dias} colaboradores sem dias úteis definidos")
        
        return df
    
    def _aplicar_regras_exclusao_cargo(self, dados_validados: Dict[str, pd.DataFrame]):
        """Aplica regras de exclusão por cargo"""
        
        # Excluir aprendizes
        if 'aprendizes' in dados_validados:
            matriculas_aprendizes = set(dados_validados['aprendizes']['MATRICULA'].dropna())
            mask_aprendizes = self.df_consolidado['MATRICULA'].isin(matriculas_aprendizes)
            
            count_aprendizes = mask_aprendizes.sum()
            self.df_consolidado.loc[mask_aprendizes, 'elegivel'] = False
            self.df_consolidado.loc[mask_aprendizes, 'motivo_exclusao'] = 'Aprendiz'
            
            for matricula in self.df_consolidado[mask_aprendizes]['MATRICULA']:
                self.logger.log_exclusao(matricula, 'Aprendiz', 'Aprendizes')
            
            self.logger.log_info(f"Excluídos {count_aprendizes} aprendizes")
        
        # Excluir estagiários
        if 'estagios' in dados_validados:
            matriculas_estagios = set(dados_validados['estagios']['MATRICULA'].dropna())
            mask_estagios = self.df_consolidado['MATRICULA'].isin(matriculas_estagios)
            
            count_estagios = mask_estagios.sum()
            self.df_consolidado.loc[mask_estagios, 'elegivel'] = False
            self.df_consolidado.loc[mask_estagios, 'motivo_exclusao'] = 'Estagiário'
            
            for matricula in self.df_consolidado[mask_estagios]['MATRICULA']:
                self.logger.log_exclusao(matricula, 'Estagiário', 'Estagiários')
            
            self.logger.log_info(f"Excluídos {count_estagios} estagiários")
        
        # Excluir cargos específicos da configuração
        cargos_excluidos = self.config['exclusoes']['cargos_nao_elegiveis']
        for cargo in cargos_excluidos:
            mask_cargo = self.df_consolidado['TITULO DO CARGO'].str.upper().str.contains(cargo.upper(), na=False)
            
            count_cargo = mask_cargo.sum()
            if count_cargo > 0:
                self.df_consolidado.loc[mask_cargo, 'elegivel'] = False
                self.df_consolidado.loc[mask_cargo, 'motivo_exclusao'] = f'Cargo: {cargo}'
                
                for matricula in self.df_consolidado[mask_cargo]['MATRICULA']:
                    self.logger.log_exclusao(matricula, f'Cargo: {cargo}', 'Cargos excluídos')
                
                self.logger.log_info(f"Excluídos {count_cargo} colaboradores com cargo {cargo}")
    
    def _aplicar_regras_afastamentos(self, dados_validados: Dict[str, pd.DataFrame]):
        """Aplica regras de afastamentos"""
        
        if 'afastamentos' not in dados_validados:
            return
        
        df_afastamentos = dados_validados['afastamentos']
        tipos_excluidos = self.config['exclusoes']['tipos_afastamento_excluidos']
        
        for _, row in df_afastamentos.iterrows():
            matricula = row['MATRICULA']
            tipo_afastamento = row['DESC. SITUACAO']
            
            # Verificar se é um tipo de afastamento que exclui do VR
            if tipo_afastamento in tipos_excluidos:
                mask = self.df_consolidado['MATRICULA'] == matricula
                
                if mask.any():
                    self.df_consolidado.loc[mask, 'elegivel'] = False
                    self.df_consolidado.loc[mask, 'motivo_exclusao'] = f'Afastamento: {tipo_afastamento}'
                    
                    self.logger.log_exclusao(matricula, f'Afastamento: {tipo_afastamento}', 'Afastamentos')
        
        count_afastamentos = len(df_afastamentos[df_afastamentos['DESC. SITUACAO'].isin(tipos_excluidos)])
        self.logger.log_info(f"Processados {count_afastamentos} afastamentos que excluem do VR")
    
    def _aplicar_regras_ferias(self, dados_validados: Dict[str, pd.DataFrame]):
        """Aplica regras de férias (cálculo proporcional)"""
        
        if 'ferias' not in dados_validados:
            return
        
        df_ferias = dados_validados['ferias']
        
        for _, row in df_ferias.iterrows():
            matricula = row['MATRICULA']
            dias_ferias = row['DIAS DE FÉRIAS']
            
            mask = self.df_consolidado['MATRICULA'] == matricula
            
            if mask.any():
                self.df_consolidado.loc[mask, 'dias_ferias'] = dias_ferias
                
                # Log do cálculo especial
                self.logger.log_calculo_especial(
                    matricula, 
                    'Férias proporcionais', 
                    f'{dias_ferias} dias de férias'
                )
        
        self.logger.log_info(f"Processadas férias para {len(df_ferias)} colaboradores")
    
    def _aplicar_regras_desligamento(self, dados_validados: Dict[str, pd.DataFrame]):
        """Aplica regras de desligamento (corte dia 15)"""
        
        if 'desligados' not in dados_validados:
            return
        
        df_desligados = dados_validados['desligados']
        dia_corte = self.config['regras_negocio']['dia_corte_desligamento']
        
        for _, row in df_desligados.iterrows():
            matricula = row['MATRICULA']
            data_demissao = row['DATA DEMISSÃO']
            comunicado = row['COMUNICADO DE DESLIGAMENTO']
            
            mask = self.df_consolidado['MATRICULA'] == matricula
            
            if mask.any():
                self.df_consolidado.loc[mask, 'data_demissao'] = data_demissao
                self.df_consolidado.loc[mask, 'comunicado_desligamento'] = comunicado
                
                # Aplicar regra do dia 15
                if isinstance(data_demissao, pd.Timestamp):
                    dia_demissao = data_demissao.day
                    
                    if dia_demissao <= dia_corte:
                        # Desligamento antes do dia 15 - VR proporcional
                        self.df_consolidado.loc[mask, 'elegivel'] = False
                        self.df_consolidado.loc[mask, 'motivo_exclusao'] = f'Desligado antes do dia {dia_corte}'
                        
                        self.logger.log_exclusao(
                            matricula, 
                            f'Desligado dia {dia_demissao} (antes do corte dia {dia_corte})', 
                            'Desligados antes do dia 15'
                        )
                    else:
                        # Desligamento após o dia 15 - VR integral
                        self.logger.log_calculo_especial(
                            matricula, 
                            'Desligado após dia 15 (VR integral)', 
                            f'Desligado dia {dia_demissao}'
                        )
        
        self.logger.log_info(f"Processados {len(df_desligados)} desligamentos")
    
    def _aplicar_regras_exterior(self, dados_validados: Dict[str, pd.DataFrame]):
        """Aplica regras para colaboradores no exterior"""
        
        if 'exterior' not in dados_validados:
            return
        
        df_exterior = dados_validados['exterior']
        
        for _, row in df_exterior.iterrows():
            matricula = row['MATRICULA']  # Já foi renomeado de 'Cadastro'
            valor = row['Valor']
            observacao = row.get('Unnamed: 2', '')
            
            mask = self.df_consolidado['MATRICULA'] == matricula
            
            if mask.any():
                # Verificar se deve ser excluído ou tem valor especial
                if pd.notna(observacao) and ('desligado' in str(observacao).lower() or 'removido' in str(observacao).lower()):
                    self.df_consolidado.loc[mask, 'elegivel'] = False
                    self.df_consolidado.loc[mask, 'motivo_exclusao'] = f'Exterior: {observacao}'
                    
                    self.logger.log_exclusao(matricula, f'Exterior: {observacao}', 'Colaboradores no exterior')
                else:
                    # Valor especial para exterior
                    self.df_consolidado.loc[mask, 'valor_exterior'] = valor
                    
                    self.logger.log_calculo_especial(
                        matricula, 
                        'Valor especial exterior', 
                        f'Valor: R$ {valor:.2f}'
                    )
        
        self.logger.log_info(f"Processados {len(df_exterior)} colaboradores no exterior")
    
    def _aplicar_regras_admissao(self, dados_validados: Dict[str, pd.DataFrame]):
        """Aplica regras para admissões no mês (VR proporcional)"""
        
        if 'admissoes' not in dados_validados:
            return
        
        df_admissoes = dados_validados['admissoes']
        competencia = self.config['regras_negocio']['competencia_referencia']
        
        # Extrair ano e mês da competência
        ano, mes = map(int, competencia.split('-'))
        
        for _, row in df_admissoes.iterrows():
            matricula = row['MATRICULA']
            data_admissao = row['Admissão']
            
            mask = self.df_consolidado['MATRICULA'] == matricula
            
            if mask.any() and isinstance(data_admissao, pd.Timestamp):
                # Verificar se admissão foi no mês da competência
                if data_admissao.year == ano and data_admissao.month == mes:
                    # Calcular dias proporcionais
                    dias_no_mes = calendar.monthrange(ano, mes)[1]
                    dias_trabalhados = dias_no_mes - data_admissao.day + 1
                    
                    self.logger.log_calculo_especial(
                        matricula, 
                        'Admitido no mês (VR proporcional)', 
                        f'Admitido dia {data_admissao.day}, {dias_trabalhados} dias trabalhados'
                    )
        
        self.logger.log_info(f"Processadas {len(df_admissoes)} admissões")
    
    def _calcular_valores_vr(self):
        """Calcula valores de VR para colaboradores elegíveis"""
        
        # Filtrar apenas colaboradores elegíveis
        mask_elegiveis = self.df_consolidado['elegivel'] == True
        
        for idx in self.df_consolidado[mask_elegiveis].index:
            row = self.df_consolidado.loc[idx]
            
            # Obter dias úteis do sindicato
            dias_uteis_base = row.get('dias_uteis_sindicato', 22)  # Default 22 dias
            
            # Calcular dias efetivos (descontar férias)
            dias_efetivos = dias_uteis_base - row.get('dias_ferias', 0)
            
            # Garantir que não seja negativo
            dias_efetivos = max(0, dias_efetivos)
            
            # Obter valor diário
            valor_diario = row.get('valor_diario_vr', 0)
            
            # Verificar se há valor especial para exterior
            if row.get('valor_exterior', 0) > 0:
                valor_total = row['valor_exterior']
                self.df_consolidado.loc[idx, 'observacoes'] = 'Valor especial - Exterior'
            else:
                valor_total = dias_efetivos * valor_diario
            
            # Calcular divisão empresa/colaborador
            percentual_empresa = self.config['regras_negocio']['percentual_empresa']
            percentual_colaborador = self.config['regras_negocio']['percentual_colaborador']
            
            custo_empresa = valor_total * percentual_empresa
            desconto_colaborador = valor_total * percentual_colaborador
            
            # Atualizar DataFrame
            self.df_consolidado.loc[idx, 'dias_calculados'] = dias_efetivos
            self.df_consolidado.loc[idx, 'valor_total_vr'] = valor_total
            self.df_consolidado.loc[idx, 'custo_empresa'] = custo_empresa
            self.df_consolidado.loc[idx, 'desconto_colaborador'] = desconto_colaborador
        
        # Zerar valores para não elegíveis
        mask_nao_elegiveis = self.df_consolidado['elegivel'] == False
        colunas_zerar = ['dias_calculados', 'valor_total_vr', 'custo_empresa', 'desconto_colaborador']
        
        for coluna in colunas_zerar:
            self.df_consolidado.loc[mask_nao_elegiveis, coluna] = 0
        
        total_elegiveis = mask_elegiveis.sum()
        valor_total_processado = self.df_consolidado[mask_elegiveis]['valor_total_vr'].sum()
        
        self.logger.log_info(f"Valores calculados para {total_elegiveis} colaboradores elegíveis")
        self.logger.log_info(f"Valor total processado: R$ {valor_total_processado:,.2f}")
    
    def _gerar_estatisticas_finais(self):
        """Gera estatísticas finais do processamento"""
        
        total_colaboradores = len(self.df_consolidado)
        colaboradores_elegiveis = (self.df_consolidado['elegivel'] == True).sum()
        colaboradores_excluidos = (self.df_consolidado['elegivel'] == False).sum()
        valor_total = self.df_consolidado[self.df_consolidado['elegivel'] == True]['valor_total_vr'].sum()
        
        # Estatísticas por categoria de exclusão
        exclusoes_por_motivo = self.df_consolidado[
            self.df_consolidado['elegivel'] == False
        ]['motivo_exclusao'].value_counts().to_dict()
        
        self.logger.log_info(f"Estatísticas finais:")
        self.logger.log_info(f"- Total de colaboradores: {total_colaboradores}")
        self.logger.log_info(f"- Colaboradores elegíveis: {colaboradores_elegiveis}")
        self.logger.log_info(f"- Colaboradores excluídos: {colaboradores_excluidos}")
        self.logger.log_info(f"- Valor total: R$ {valor_total:,.2f}")
        self.logger.log_info(f"- Exclusões por motivo: {exclusoes_por_motivo}")
    
    def get_dados_consolidados(self) -> pd.DataFrame:
        """Retorna os dados consolidados"""
        return self.df_consolidado
    
    def get_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do processamento"""
        if self.df_consolidado is None:
            return {}
        
        mask_elegiveis = self.df_consolidado['elegivel'] == True
        
        return {
            'total_colaboradores': len(self.df_consolidado),
            'colaboradores_elegiveis': mask_elegiveis.sum(),
            'colaboradores_excluidos': (~mask_elegiveis).sum(),
            'valor_total': self.df_consolidado[mask_elegiveis]['valor_total_vr'].sum(),
            'custo_total_empresa': self.df_consolidado[mask_elegiveis]['custo_empresa'].sum(),
            'desconto_total_colaboradores': self.df_consolidado[mask_elegiveis]['desconto_colaborador'].sum(),
            'exclusoes_por_motivo': self.df_consolidado[~mask_elegiveis]['motivo_exclusao'].value_counts().to_dict(),
            'colaboradores_com_ferias': (self.df_consolidado['dias_ferias'] > 0).sum(),
            'colaboradores_exterior': (self.df_consolidado['valor_exterior'] > 0).sum()
        }

