"""
Configuration Template Manager

Manages configuration templates for different model types.
Provides template inheritance and customization capabilities.

Implements the template management layer of the configuration
architecture as defined in the architecture document.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from npu_converter.core.exceptions.config_errors import ConfigError


@dataclass
class TemplateMetadata:
    """Template metadata information."""
    name: str
    description: str
    model_type: str
    version: str
    author: str
    created_at: str
    tags: List[str]


@dataclass
class TemplateInfo:
    """Template information."""
    metadata: TemplateMetadata
    template_data: Dict[str, Any]
    file_path: Path


class ConfigTemplateManager:
    """
    Configuration template management system.

    Manages templates for different model types, supports inheritance
    and customization of configuration templates.
    """

    def __init__(self, templates_dir: Optional[Path] = None, lazy_load: bool = True):
        """
        Initialize template manager.

        Args:
            templates_dir: Directory containing template files
            lazy_load: Whether to lazily load templates for performance
        """
        self.templates_dir = templates_dir or Path(__file__).parent
        self._templates: Dict[str, TemplateInfo] = {}
        self._templates_loaded = False
        self._lazy_load = lazy_load

        if not lazy_load:
            self._load_templates()

    def _load_templates(self) -> None:
        """Load all available templates from templates directory."""
        if self._templates_loaded:
            return

        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            self._templates_loaded = True
            return

        for template_file in self.templates_dir.glob("*.yaml"):
            if template_file.name.startswith("template_"):
                self._load_template_file(template_file)

        self._templates_loaded = True

    def _ensure_templates_loaded(self) -> None:
        """Ensure templates are loaded (for lazy loading)."""
        if self._lazy_load and not self._templates_loaded:
            self._load_templates()

    def _load_template_file(self, template_file: Path) -> None:
        """Load a single template file."""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)

            if not isinstance(template_data, dict):
                print(f"Warning: Template file {template_file} does not contain valid YAML dictionary")
                return

            # Extract metadata
            metadata_section = template_data.get("_metadata", {})
            template_name = metadata_section.get("name", template_file.stem)

            # Create metadata
            metadata = TemplateMetadata(
                name=template_name,
                description=metadata_section.get("description", ""),
                model_type=metadata_section.get("model_type", ""),
                version=metadata_section.get("version", "1.0.0"),
                author=metadata_section.get("author", ""),
                created_at=metadata_section.get("created_at", ""),
                tags=metadata_section.get("tags", [])
            )

            # Remove metadata from template data
            clean_template_data = {k: v for k, v in template_data.items() if not k.startswith("_")}

            # Store template
            self._templates[template_name] = TemplateInfo(
                metadata=metadata,
                template_data=clean_template_data,
                file_path=template_file
            )

        except Exception as e:
            print(f"Error loading template {template_file}: {e}")

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get template by name.

        Args:
            template_name: Name of the template

        Returns:
            Template dictionary or None if not found
        """
        template_info = self._templates.get(template_name)
        return template_info.template_data.copy() if template_info else None

    def list_templates(self) -> List[TemplateMetadata]:
        """
        List all available templates.

        Returns:
            List of template metadata
        """
        self._ensure_templates_loaded()
        return [template.metadata for template in self._templates.values()]

    def get_templates_by_model_type(self, model_type: str) -> List[TemplateMetadata]:
        """
        Get templates filtered by model type.

        Args:
            model_type: Model type to filter by

        Returns:
            List of matching template metadata
        """
        return [
            template.metadata
            for template in self._templates.values()
            if template.metadata.model_type == model_type
        ]

    def create_template(self, template_name: str, template_data: Dict[str, Any],
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new template.

        Args:
            template_name: Name of the template
            template_data: Template configuration data
            metadata: Optional metadata

        Returns:
            True if template was created successfully
        """
        template_file = self.templates_dir / f"template_{template_name}.yaml"

        # Prepare full template data
        full_template_data = template_data.copy()
        if metadata:
            full_template_data["_metadata"] = metadata
        else:
            full_template_data["_metadata"] = {
                "name": template_name,
                "description": f"Template for {template_name}",
                "version": "1.0.0",
                "author": "Configuration Manager",
                "created_at": "",
                "tags": []
            }

        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(full_template_data, f, default_flow_style=False, indent=2)

            # Reload templates
            self._load_template_file(template_file)
            return True

        except Exception as e:
            print(f"Error creating template {template_name}: {e}")
            return False

    def delete_template(self, template_name: str) -> bool:
        """
        Delete a template.

        Args:
            template_name: Name of the template to delete

        Returns:
            True if template was deleted successfully
        """
        if template_name not in self._templates:
            return False

        template_info = self._templates[template_name]

        try:
            template_info.file_path.unlink()
            del self._templates[template_name]
            return True
        except Exception as e:
            print(f"Error deleting template {template_name}: {e}")
            return False

    def apply_template(self, template_name: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply template with optional overrides.

        Args:
            template_name: Name of the template
            overrides: Optional override values

        Returns:
            Resulting configuration dictionary
        """
        template_data = self.get_template(template_name)
        if not template_data:
            raise ConfigError(f"Template not found: {template_name}")

        result = template_data.copy()

        # Apply overrides
        if overrides:
            result = self._deep_merge(result, overrides)

        return result

    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_default_template_for_model(self, model_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the default template for a model type.

        Args:
            model_type: Model type ('sensevoice' or 'piper_vits')

        Returns:
            Default template dictionary or None
        """
        templates = self.get_templates_by_model_type(model_type)
        if not templates:
            return None

        # Look for a template marked as default
        for template in templates:
            if "default" in template.tags:
                return self.get_template(template.name)

        # If no default template, return the first one
        return self.get_template(templates[0].name)

    def validate_template(self, template_data: Dict[str, Any]) -> List[str]:
        """
        Validate template structure.

        Args:
            template_data: Template data to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Check required sections
        required_sections = ["project", "hardware", "conversion_params"]
        for section in required_sections:
            if section not in template_data:
                errors.append(f"Missing required section: {section}")

        # Validate project section
        if "project" in template_data:
            project = template_data["project"]
            if "model_type" not in project:
                errors.append("Missing model_type in project section")
            elif project["model_type"] not in ["sensevoice", "piper_vits"]:
                errors.append(f"Invalid model_type: {project['model_type']}")

        return errors

    def export_template(self, template_name: str, output_path: Path) -> bool:
        """
        Export template to a file.

        Args:
            template_name: Name of the template
            output_path: Output file path

        Returns:
            True if export was successful
        """
        template_data = self.get_template(template_name)
        if not template_data:
            return False

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting template {template_name}: {e}")
            return False

    def import_template(self, template_path: Path, template_name: Optional[str] = None) -> bool:
        """
        Import template from a file.

        Args:
            template_path: Path to template file
            template_name: Optional name for the template

        Returns:
            True if import was successful
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)

            if not isinstance(template_data, dict):
                print(f"Invalid template file: {template_path}")
                return False

            name = template_name or template_path.stem
            return self.create_template(name, template_data)

        except Exception as e:
            print(f"Error importing template from {template_path}: {e}")
            return False