"""
Configuration Template Manager

Provides template management functionality for the configuration system.
Supports multiple model types and configuration inheritance.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..core.models.config_model import ConfigModel


@dataclass
class TemplateInfo:
    """Template metadata information."""
    name: str
    model_type: str
    description: str
    version: str
    file_path: Path


class ConfigTemplateManager:
    """
    Configuration template manager.

    Provides functionality to create, retrieve, and manage configuration templates
    for different model types and use cases.
    """

    def __init__(self, template_dir: Optional[Path] = None, lazy_load: bool = True):
        """
        Initialize template manager.

        Args:
            template_dir: Directory containing template files
            lazy_load: Whether to lazily load templates
        """
        self.template_dir = template_dir or Path("templates")
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._template_info: Dict[str, TemplateInfo] = {}
        self._lazy_load = lazy_load
        self._loaded = False

        # Default templates directory
        self.templates_dir = Path(__file__).parent.parent.parent.parent / "docs" / "examples" / "templates"

        if not self._lazy_load:
            self._load_all_templates()

    def _load_all_templates(self) -> None:
        """Load all available templates from template directory."""
        if self._loaded:
            return

        self._loaded = True

        # Load built-in templates
        self._load_builtin_templates()

        # Load templates from filesystem
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.yaml"):
                try:
                    with open(template_file, 'r') as f:
                        template = yaml.safe_load(f)
                    template_name = template_file.stem
                    self._templates[template_name] = template

                    # Extract template info
                    info = TemplateInfo(
                        name=template_name,
                        model_type=template.get('project', {}).get('model_type', 'unknown'),
                        description=template.get('project', {}).get('description', ''),
                        version=template.get('project', {}).get('version', '1.0.0'),
                        file_path=template_file
                    )
                    self._template_info[template_name] = info

                except Exception as e:
                    print(f"Warning: Failed to load template {template_file}: {e}")

    def _load_builtin_templates(self) -> None:
        """Load built-in templates."""
        # SenseVoice template
        sensevoice_template = {
            "project": {
                "name": "sensevoice_model",
                "version": "1.0.0",
                "model_type": "sensevoice",
                "description": "SenseVoice ASR model configuration"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2"
            },
            "conversion_params": {
                "quantization": {
                    "enabled": True,
                    "precision": "int8"
                }
            },
            "model_config": {
                "model_type": "sensevoice",
                "input_format": "onnx",
                "output_format": "bpu"
            }
        }
        self._templates["sensevoice_default"] = sensevoice_template

        # VITS-Cantonese template
        vits_cantonese_template = {
            "project": {
                "name": "vits_cantonese_model",
                "version": "1.0.0",
                "model_type": "vits_cantonese",
                "description": "VITS Cantonese TTS model configuration"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2"
            },
            "conversion_params": {
                "quantization": {
                    "enabled": True,
                    "precision": "int8"
                }
            },
            "model_config": {
                "model_type": "vits_cantonese",
                "input_format": "onnx",
                "output_format": "bpu"
            }
        }
        self._templates["vits_cantonese_default"] = vits_cantonese_template

        # Piper VITS template
        piper_vits_template = {
            "project": {
                "name": "piper_vits_model",
                "version": "1.0.0",
                "model_type": "piper_vits",
                "description": "Piper VITS TTS model configuration"
            },
            "hardware": {
                "target_device": "horizon_x5",
                "optimization_level": "O2"
            },
            "conversion_params": {
                "quantization": {
                    "enabled": True,
                    "precision": "int8"
                }
            },
            "model_config": {
                "model_type": "piper_vits",
                "input_format": "onnx",
                "output_format": "bpu"
            }
        }
        self._templates["piper_vits_default"] = piper_vits_template

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by name.

        Args:
            template_name: Name of the template

        Returns:
            Template configuration dictionary or None if not found
        """
        if not self._loaded:
            self._load_all_templates()

        return self._templates.get(template_name)

    def create_template(self, name: str, model_type: str, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new configuration template.

        Args:
            name: Template name
            model_type: Model type (sensevoice, vits_cantonese, piper_vits)
            base_config: Base configuration

        Returns:
            Created template
        """
        template = base_config.copy()
        template["project"] = template.get("project", {})
        template["project"]["name"] = name
        template["project"]["model_type"] = model_type

        self._templates[name] = template
        return template

    def list_templates(self) -> List[str]:
        """List all available template names."""
        if not self._loaded:
            self._load_all_templates()

        return list(self._templates.keys())

    def get_templates_by_model_type(self, model_type: str) -> List[str]:
        """
        Get templates for a specific model type.

        Args:
            model_type: Model type to filter by

        Returns:
            List of template names for the model type
        """
        if not self._loaded:
            self._load_all_templates()

        matching_templates = []
        for name, template in self._templates.items():
            if template.get("project", {}).get("model_type") == model_type:
                matching_templates.append(name)

        return matching_templates

    def get_template_info(self, template_name: str) -> Optional[TemplateInfo]:
        """
        Get template metadata information.

        Args:
            template_name: Template name

        Returns:
            TemplateInfo object or None if not found
        """
        if not self._loaded:
            self._load_all_templates()

        return self._template_info.get(template_name)

    def apply_template_overrides(self, template: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply configuration overrides to a template.

        Args:
            template: Base template
            overrides: Configuration overrides

        Returns:
            Merged configuration
        """
        result = template.copy()
        self._deep_merge(result, overrides)
        return result

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Deep merge override dictionary into base dictionary.

        Args:
            base: Base dictionary (will be modified)
            override: Override dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value