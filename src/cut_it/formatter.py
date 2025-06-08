"""Task formatting functionality for converting text chunks into organized task lists."""

from typing import List, Dict, Any


class TaskFormatter:
    """Formats text chunks into organized task markdown format."""
    
    def __init__(self, pt_br: bool = False):
        """Initialize task formatter.
        
        Args:
            pt_br: Whether to use Portuguese (Brazil) localization
        """
        self.pt_br = pt_br
        self.labels = self._get_labels()
    
    def _get_labels(self) -> Dict[str, str]:
        """Get localized labels based on language setting."""
        if self.pt_br:
            return {
                "task": "TAREFA",
                "progress": "Progresso",
                "pending": "Pendente",
                "started": "Iniciado",
                "completed": "Concluído"
            }
        else:
            return {
                "task": "TASK",
                "progress": "Progress",
                "pending": "Pending",
                "started": "Started", 
                "completed": "Completed"
            }
    
    def format_as_tasks(
        self, 
        chunks: List[str], 
        filename: str,
        initial_status: str = "Pending"
    ) -> str:
        """Format text chunks as organized task list.
        
        Args:
            chunks: List of text chunks
            filename: Original filename
            initial_status: Initial status for all tasks
            
        Returns:
            Formatted markdown string
        """
        if not chunks:
            return f"# {filename}\n\n---\n\nNo content to process.\n\n---\n"
        
        # Build the formatted output
        output_lines = [f"# {filename}", ""]
        
        for i, chunk in enumerate(chunks, 1):
            # Add divider
            output_lines.append("---")
            output_lines.append("")
            
            # Add task header
            task_title = f"## {self.labels['task']} {i}"
            output_lines.append(task_title)
            
            # Add progress status
            progress_line = f"**{self.labels['progress']}:** {self.labels[initial_status.lower()]}"
            output_lines.append(progress_line)
            output_lines.append("")
            
            # Add checkboxes for progress tracking
            checkboxes = self._generate_checkboxes(initial_status)
            output_lines.extend(checkboxes)
            output_lines.append("")
            
            # Add the actual content
            output_lines.append(chunk.strip())
            output_lines.append("")
        
        # Add final divider
        output_lines.append("---")
        
        return "\n".join(output_lines)
    
    def _generate_checkboxes(self, current_status: str) -> List[str]:
        """Generate checkbox list showing current progress.
        
        Args:
            current_status: Current task status (Pending, Started, Completed)
            
        Returns:
            List of checkbox lines
        """
        status_order = ["pending", "started", "completed"]
        current_index = status_order.index(current_status.lower()) if current_status.lower() in status_order else 0
        
        checkboxes = []
        for i, status in enumerate(status_order):
            # Check box if current status or earlier
            checkbox = "☑" if i <= current_index else "☐"
            label = self.labels[status]
            checkboxes.append(f"- {checkbox} {label}")
        
        return checkboxes
    
    def update_task_status(
        self, 
        content: str, 
        task_number: int, 
        new_status: str
    ) -> str:
        """Update status of a specific task in formatted content.
        
        Args:
            content: Existing formatted content
            task_number: Task number to update (1-based)
            new_status: New status (Pending, Started, Completed)
            
        Returns:
            Updated content
        """
        lines = content.split('\n')
        updated_lines = []
        
        task_pattern = f"## {self.labels['task']} {task_number}"
        in_target_task = False
        checkbox_section = False
        
        for line in lines:
            if line.strip() == task_pattern:
                in_target_task = True
                updated_lines.append(line)
                continue
            
            if in_target_task:
                # Update progress line
                if line.startswith(f"**{self.labels['progress']}:**"):
                    updated_lines.append(f"**{self.labels['progress']}:** {self.labels[new_status.lower()]}")
                    continue
                
                # Update checkboxes
                if line.startswith("- ☐") or line.startswith("- ☑"):
                    if not checkbox_section:
                        checkbox_section = True
                        # Replace all checkboxes for this task
                        checkboxes = self._generate_checkboxes(new_status)
                        updated_lines.extend(checkboxes)
                        # Skip original checkboxes
                        continue
                    else:
                        # Skip remaining original checkboxes
                        continue
                
                # If we hit another task or divider, we're done with this task
                if line.startswith("## ") or line.strip() == "---":
                    in_target_task = False
                    checkbox_section = False
            
            updated_lines.append(line)
        
        return "\n".join(updated_lines)
    
    def get_task_count(self, content: str) -> int:
        """Get the total number of tasks in formatted content.
        
        Args:
            content: Formatted content
            
        Returns:
            Number of tasks
        """
        lines = content.split('\n')
        task_count = 0
        
        for line in lines:
            if line.startswith(f"## {self.labels['task']} "):
                task_count += 1
        
        return task_count
    
    def extract_task_content(self, content: str, task_number: int) -> str:
        """Extract content of a specific task.
        
        Args:
            content: Formatted content
            task_number: Task number to extract (1-based)
            
        Returns:
            Task content
        """
        lines = content.split('\n')
        task_pattern = f"## {self.labels['task']} {task_number}"
        
        in_target_task = False
        content_started = False
        task_content = []
        
        for line in lines:
            if line.strip() == task_pattern:
                in_target_task = True
                continue
            
            if in_target_task:
                # Skip progress line and checkboxes
                if (line.startswith(f"**{self.labels['progress']}:**") or 
                    line.startswith("- ☐") or 
                    line.startswith("- ☑") or
                    line.strip() == ""):
                    if content_started and line.strip() == "":
                        # Empty line in content
                        task_content.append(line)
                    continue
                
                # End of task
                if line.strip() == "---" or line.startswith("## "):
                    break
                
                # This is the actual content
                content_started = True
                task_content.append(line)
        
        return "\n".join(task_content).strip()