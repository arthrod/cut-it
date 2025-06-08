"""Configuration management for cut-it."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Config:
    """Configuration settings for cut-it."""
    
    chunk_size_min: int = 300
    chunk_size_max: int = 500
    model: str = "gpt-4"
    pt_br: bool = False
    cli_mode: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)


class ConfigManager:
    """Manages configuration file operations."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".cut-it" / "config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Config:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                return Config.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Return default config if file doesn't exist or is corrupted
        return Config()
    
    def save(self, config: Config) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
    
    def update(self, **kwargs) -> Config:
        """Update configuration with new values."""
        config = self.load()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save(config)
        return config