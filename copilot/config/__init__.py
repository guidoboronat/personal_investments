"""
Configuration loader for the trading toolkit.
"""

import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Load and manage configuration."""

    @staticmethod
    def load_json(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to JSON config file

        Returns:
            Configuration dictionary
        """
        with open(config_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def load_yaml(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML config file

        Returns:
            Configuration dictionary
        """
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    @staticmethod
    def load(config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file, auto-detecting format.

        Args:
            config_path: Path to config file (JSON or YAML)

        Returns:
            Configuration dictionary
        """
        if config_path is None:
            # Load default config
            config_dir = Path(__file__).parent
            config_path = str(config_dir / 'default_config.yaml')

        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if path.suffix in ['.yaml', '.yml']:
            return ConfigLoader.load_yaml(str(path))
        elif path.suffix == '.json':
            return ConfigLoader.load_json(str(path))
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

    @staticmethod
    def save_json(config: Dict[str, Any], output_path: str):
        """
        Save configuration to JSON file.

        Args:
            config: Configuration dictionary
            output_path: Path to output file
        """
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)

    @staticmethod
    def save_yaml(config: Dict[str, Any], output_path: str):
        """
        Save configuration to YAML file.

        Args:
            config: Configuration dictionary
            output_path: Path to output file
        """
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
