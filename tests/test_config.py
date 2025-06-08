"""Tests for the configuration module."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from cut_it.config import Config, ConfigManager


class TestConfig:
    """Test cases for Config class."""

    def test_init_default(self):
        """Test Config initialization with default values."""
        config = Config()
        assert config.chunk_size_min == 300
        assert config.chunk_size_max == 500
        assert config.model == "gpt-4"
        assert config.pt_br is False
        assert config.cli_mode is True

    def test_init_custom(self):
        """Test Config initialization with custom values."""
        config = Config(
            chunk_size_min=200,
            chunk_size_max=800,
            model="gpt-3.5-turbo",
            pt_br=True,
            cli_mode=False
        )
        assert config.chunk_size_min == 200
        assert config.chunk_size_max == 800
        assert config.model == "gpt-3.5-turbo"
        assert config.pt_br is True
        assert config.cli_mode is False

    def test_from_dict(self):
        """Test Config creation from dictionary."""
        data = {
            "chunk_size_min": 400,
            "chunk_size_max": 600,
            "model": "gpt-4",
            "pt_br": True,
            "cli_mode": False,
            "extra_field": "ignored"  # Should be ignored
        }
        config = Config.from_dict(data)
        assert config.chunk_size_min == 400
        assert config.chunk_size_max == 600
        assert config.model == "gpt-4"
        assert config.pt_br is True
        assert config.cli_mode is False

    def test_from_dict_partial(self):
        """Test Config creation from partial dictionary."""
        data = {"chunk_size_min": 250, "pt_br": True}
        config = Config.from_dict(data)
        assert config.chunk_size_min == 250
        assert config.chunk_size_max == 500  # Default
        assert config.pt_br is True
        assert config.model == "gpt-4"  # Default

    def test_to_dict(self):
        """Test Config conversion to dictionary."""
        config = Config(chunk_size_min=350, pt_br=True)
        data = config.to_dict()
        
        expected = {
            "chunk_size_min": 350,
            "chunk_size_max": 500,
            "model": "gpt-4",
            "pt_br": True,
            "cli_mode": True
        }
        assert data == expected


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def test_init_default_path(self):
        """Test ConfigManager initialization with default path."""
        with patch('cut_it.config.Path.home') as mock_home:
            mock_home.return_value = Path("/home/user")
            manager = ConfigManager()
            expected_path = Path("/home/user/.cut-it/config.json")
            assert manager.config_path == expected_path

    def test_init_custom_path(self):
        """Test ConfigManager initialization with custom path."""
        custom_path = Path("/custom/config.json")
        manager = ConfigManager(custom_path)
        assert manager.config_path == custom_path

    @patch('cut_it.config.Path.mkdir')
    def test_init_creates_directory(self, mock_mkdir):
        """Test that ConfigManager creates config directory."""
        with patch('cut_it.config.Path.home') as mock_home:
            mock_home.return_value = Path("/home/user")
            ConfigManager()
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_load_file_not_exists(self):
        """Test loading config when file doesn't exist."""
        manager = ConfigManager(Path("/nonexistent/config.json"))
        with patch.object(manager.config_path, 'exists', return_value=False):
            config = manager.load()
            # Should return default config
            assert isinstance(config, Config)
            assert config.chunk_size_min == 300

    def test_load_file_exists_valid(self):
        """Test loading config from valid file."""
        config_data = {
            "chunk_size_min": 400,
            "chunk_size_max": 600,
            "model": "gpt-3.5-turbo",
            "pt_br": True,
            "cli_mode": False
        }
        
        manager = ConfigManager(Path("/fake/config.json"))
        
        with patch.object(manager.config_path, 'exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            
            config = manager.load()
            assert config.chunk_size_min == 400
            assert config.chunk_size_max == 600
            assert config.model == "gpt-3.5-turbo"
            assert config.pt_br is True
            assert config.cli_mode is False

    def test_load_file_exists_invalid_json(self):
        """Test loading config from file with invalid JSON."""
        manager = ConfigManager(Path("/fake/config.json"))
        
        with patch.object(manager.config_path, 'exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="invalid json")):
            
            config = manager.load()
            # Should return default config
            assert isinstance(config, Config)
            assert config.chunk_size_min == 300

    def test_load_file_exists_missing_keys(self):
        """Test loading config from file with missing keys."""
        config_data = {"chunk_size_min": 400}  # Missing other keys
        
        manager = ConfigManager(Path("/fake/config.json"))
        
        with patch.object(manager.config_path, 'exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            
            config = manager.load()
            # Should still work, using defaults for missing keys
            assert config.chunk_size_min == 400
            assert config.chunk_size_max == 500  # Default

    def test_save(self):
        """Test saving config to file."""
        config = Config(chunk_size_min=350, pt_br=True)
        manager = ConfigManager(Path("/fake/config.json"))
        
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            manager.save(config)
            
            # Check that file was opened for writing
            mock_file.assert_called_once_with(manager.config_path, 'w')
            
            # Check that JSON was written
            written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
            parsed_data = json.loads(written_data)
            
            assert parsed_data["chunk_size_min"] == 350
            assert parsed_data["pt_br"] is True

    def test_update(self):
        """Test updating configuration."""
        manager = ConfigManager(Path("/fake/config.json"))
        
        # Mock load to return existing config
        existing_config = Config(chunk_size_min=300, pt_br=False)
        
        with patch.object(manager, 'load', return_value=existing_config), \
             patch.object(manager, 'save') as mock_save:
            
            updated_config = manager.update(chunk_size_min=400, pt_br=True)
            
            assert updated_config.chunk_size_min == 400
            assert updated_config.pt_br is True
            assert updated_config.chunk_size_max == 500  # Unchanged
            
            mock_save.assert_called_once_with(updated_config)

    def test_update_invalid_attribute(self):
        """Test updating with invalid attribute."""
        manager = ConfigManager(Path("/fake/config.json"))
        
        existing_config = Config()
        
        with patch.object(manager, 'load', return_value=existing_config), \
             patch.object(manager, 'save') as mock_save:
            
            # Should ignore invalid attributes
            updated_config = manager.update(
                chunk_size_min=400, 
                invalid_attr="ignored"
            )
            
            assert updated_config.chunk_size_min == 400
            assert not hasattr(updated_config, 'invalid_attr')
            
            mock_save.assert_called_once()

    def test_update_no_changes(self):
        """Test updating with no actual changes."""
        manager = ConfigManager(Path("/fake/config.json"))
        
        existing_config = Config()
        
        with patch.object(manager, 'load', return_value=existing_config), \
             patch.object(manager, 'save') as mock_save:
            
            updated_config = manager.update()
            
            # Should still save even with no changes
            assert updated_config.chunk_size_min == existing_config.chunk_size_min
            mock_save.assert_called_once()