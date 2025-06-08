"""Localization support for cut-it CLI messages."""

from typing import Dict


def get_messages(pt_br: bool = False) -> Dict[str, str]:
    """Get localized messages based on language preference.
    
    Args:
        pt_br: Whether to use Portuguese (Brazil) localization
        
    Returns:
        Dictionary of localized messages
    """
    
    if pt_br:
        return {
            # File operations
            "file_not_found": "Arquivo não encontrado",
            "encoding_error": "Erro de codificação do arquivo. Certifique-se de que o arquivo está em UTF-8.",
            "reading_file": "Lendo arquivo...",
            "saving_file": "Salvando arquivo...",
            
            # Processing
            "splitting_text": "Dividindo texto em blocos semânticos...",
            "formatting_tasks": "Formatando como lista de tarefas...",
            
            # Results
            "success": "✅ Processamento concluído com sucesso!",
            "chunks_created": "Blocos de tarefa criados",
            
            # Configuration
            "config_updated": "Configuração atualizada com sucesso",
            "checking_updates": "Verificando atualizações...",
            "up_to_date": "cut-it está atualizado",
            
            # Errors
            "error": "Erro",
            "warning": "Aviso",
            "info": "Informação",
            
            # Status
            "pending": "Pendente",
            "started": "Iniciado", 
            "completed": "Concluído",
            
            # Tasks
            "task": "TAREFA",
            "progress": "Progresso",
            
            # Help
            "help_description": "Ferramenta de divisão semântica de texto que converte documentos em listas organizadas de tarefas",
            "help_file": "Caminho para o arquivo de texto a ser processado",
            "help_output": "Caminho do arquivo de saída (opcional)",
            "help_size": "Faixa de tamanho do bloco (min,max)",
            "help_model": "Modelo tiktoken a ser usado",
            "help_type": "Forçar tipo de arquivo (text, markdown, code)",
            "help_config_show": "Mostrar configuração atual",
            "help_config_ptbr": "Ativar/desativar localização em Português (Brasil)",
            "help_config_cli": "Ativar/desativar modo CLI",
            "help_config_model": "Definir modelo tiktoken padrão",
            "help_config_size": "Definir faixa de tamanho de bloco padrão"
        }
    
    else:
        return {
            # File operations
            "file_not_found": "File not found",
            "encoding_error": "File encoding error. Please ensure the file is in UTF-8 format.",
            "reading_file": "Reading file...",
            "saving_file": "Saving file...",
            
            # Processing
            "splitting_text": "Splitting text into semantic chunks...",
            "formatting_tasks": "Formatting as task list...",
            
            # Results
            "success": "✅ Processing completed successfully!",
            "chunks_created": "Task chunks created",
            
            # Configuration
            "config_updated": "Configuration updated successfully",
            "checking_updates": "Checking for updates...",
            "up_to_date": "cut-it is up to date",
            
            # Errors
            "error": "Error",
            "warning": "Warning",
            "info": "Info",
            
            # Status
            "pending": "Pending",
            "started": "Started",
            "completed": "Completed",
            
            # Tasks
            "task": "TASK",
            "progress": "Progress",
            
            # Help
            "help_description": "Semantic text chunking tool that converts documents into organized task lists",
            "help_file": "Path to the text file to process",
            "help_output": "Output file path (optional)",
            "help_size": "Chunk size range (min,max)",
            "help_model": "Tiktoken model to use",
            "help_type": "Force file type (text, markdown, code)",
            "help_config_show": "Show current configuration",
            "help_config_ptbr": "Enable/disable Portuguese (Brazil) localization",
            "help_config_cli": "Enable/disable CLI mode",
            "help_config_model": "Set default tiktoken model",
            "help_config_size": "Set default chunk size range"
        }