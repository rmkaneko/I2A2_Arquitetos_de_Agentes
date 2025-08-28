#!/usr/bin/env python3
"""
Script principal do Sistema de Processamento VR
Autor: Manus AI
Data: 27/08/2025
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao Python path
sys.path.insert(0, str(Path(__file__).parent))

from agentes.orquestrador import OrquestradorVR


def main():
    """Função principal"""
    
    print("=== Sistema de Processamento VR ===")
    print("Autor: Manus AI")
    print("Data: 27/08/2025")
    print()
    
    try:
        # Inicializar orquestrador
        config_path = Path(__file__).parent / "config" / "config.yaml"
        orquestrador = OrquestradorVR(str(config_path))
        
        # Executar processamento completo
        resultado = orquestrador.executar_processamento_completo()
        
        # Exibir resumo
        print("\n" + "="*50)
        print("PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("="*50)
        print(f"Arquivo gerado: {resultado['arquivo_relatorio']}")
        print(f"Colaboradores elegíveis: {resultado['resumo']['colaboradores_elegiveis']}")
        print(f"Colaboradores excluídos: {resultado['resumo']['colaboradores_excluidos']}")
        print(f"Valor total: R$ {resultado['resumo']['valor_total']:,.2f}")
        print(f"Custo empresa: R$ {resultado['resumo']['custo_empresa']:,.2f}")
        print(f"Desconto colaboradores: R$ {resultado['resumo']['desconto_colaboradores']:,.2f}")
        print(f"Log de auditoria: {resultado['arquivos_log']['audit']}")
        print(f"Log técnico: {resultado['arquivos_log']['technical']}")
        print("="*50)
        
        return 0
        
    except Exception as e:
        print(f"\nERRO: {str(e)}")
        import traceback
        print(f"Detalhes: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

