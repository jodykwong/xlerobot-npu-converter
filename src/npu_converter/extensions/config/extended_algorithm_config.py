"""
扩展算法配置系统

提供完整的算法配置管理，包括验证、默认值、约束检查等功能。
"""

import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import yaml


logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """配置验证异常"""
    pass


@dataclass
class ParameterConstraint:
    """参数约束定义"""
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    regex: Optional[str] = None
    custom_validator: Optional[str] = None


@dataclass
class ParameterDefinition:
    """参数定义"""
    name: str
    type: str
    required: bool = False
    default: Any = None
    description: str = ""
    constraints: ParameterConstraint = field(default_factory=ParameterConstraint)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExtendedAlgorithmConfig:
    """
    扩展算法配置类

    提供完整的算法配置管理功能，包括验证、默认值、约束检查等。
    """

    SUPPORTED_TYPES = ['int', 'float', 'str', 'bool', 'list', 'dict', 'path']

    def __init__(self, algorithm_id: str, parameters: List[ParameterDefinition]):
        """
        初始化扩展配置

        Args:
            algorithm_id: 算法唯一标识符
            parameters: 参数定义列表
        """
        self.algorithm_id = algorithm_id
        self.parameters = {p.name: p for p in parameters}
        self._config: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}

        logger.info(f"扩展算法配置已初始化: {algorithm_id}")

    def add_parameter(self, param_def: ParameterDefinition) -> None:
        """
        添加参数定义

        Args:
            param_def: 参数定义
        """
        if param_def.name in self.parameters:
            logger.warning(f"参数 {param_def.name} 已存在，将被覆盖")

        if param_def.type not in self.SUPPORTED_TYPES:
            raise ValueError(f"不支持的参数类型: {param_def.type}")

        self.parameters[param_def.name] = param_def
        logger.debug(f"参数 {param_def.name} 已添加")

    def remove_parameter(self, param_name: str) -> bool:
        """
        移除参数定义

        Args:
            param_name: 参数名

        Returns:
            移除是否成功
        """
        if param_name not in self.parameters:
            logger.warning(f"参数 {param_name} 不存在")
            return False

        del self.parameters[param_name]
        if param_name in self._config:
            del self._config[param_name]

        logger.debug(f"参数 {param_name} 已移除")
        return True

    def configure(self, config: Dict[str, Any], validate: bool = True) -> bool:
        """
        配置算法

        Args:
            config: 配置字典
            validate: 是否验证配置

        Returns:
            配置是否成功

        Raises:
            ConfigValidationError: 如果验证失败且validate=True
        """
        try:
            if validate:
                self.validate_config(config)

            # 应用默认值
            for param_name, param_def in self.parameters.items():
                if param_name not in config:
                    if param_def.default is not None:
                        config[param_name] = param_def.default
                    elif param_def.required:
                        raise ConfigValidationError(f"缺少必需参数: {param_name}")

            # 转换类型
            for param_name, value in config.items():
                if param_name in self.parameters:
                    config[param_name] = self._convert_type(
                        param_name, value, self.parameters[param_name].type
                    )

            # 存储配置
            self._config.update(config)
            self._config['_timestamp'] = None  # 可扩展为实际时间戳

            logger.info(f"算法 {self.algorithm_id} 配置成功")
            return True

        except ConfigValidationError:
            raise
        except Exception as e:
            logger.error(f"算法 {self.algorithm_id} 配置失败: {e}")
            return False

    def validate_config(self, config: Dict[str, Any]) -> None:
        """
        验证配置

        Args:
            config: 配置字典

        Raises:
            ConfigValidationError: 如果验证失败
        """
        # 检查未知参数
        unknown_params = set(config.keys()) - set(self.parameters.keys())
        if unknown_params:
            logger.warning(f"未知参数: {unknown_params}")

        # 检查必需参数
        for param_name, param_def in self.parameters.items():
            if param_def.required and param_name not in config:
                raise ConfigValidationError(f"缺少必需参数: {param_name}")

        # 验证参数值
        for param_name, value in config.items():
            if param_name in self.parameters:
                self._validate_parameter(param_name, value, self.parameters[param_name])

    def _validate_parameter(self, param_name: str, value: Any, param_def: ParameterDefinition) -> None:
        """
        验证单个参数

        Args:
            param_name: 参数名
            value: 参数值
            param_def: 参数定义

        Raises:
            ConfigValidationError: 如果验证失败
        """
        # 类型验证
        if not self._check_type(value, param_def.type):
            raise ConfigValidationError(
                f"参数 {param_name} 类型错误: 期望 {param_def.type}，实际 {type(value).__name__}"
            )

        # 约束验证
        constraints = param_def.constraints
        error_prefix = f"参数 {param_name}"

        # 数值范围验证
        if isinstance(value, (int, float)):
            if constraints.min_value is not None and value < constraints.min_value:
                raise ConfigValidationError(
                    f"{error_prefix} 值 {value} 小于最小值 {constraints.min_value}"
                )
            if constraints.max_value is not None and value > constraints.max_value:
                raise ConfigValidationError(
                    f"{error_prefix} 值 {value} 大于最大值 {constraints.max_value}"
                )

        # 选择列表验证
        if constraints.choices is not None and value not in constraints.choices:
            raise ConfigValidationError(
                f"{error_prefix} 值 {value} 不在可选列表 {constraints.choices} 中"
            )

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        检查值类型

        Args:
            value: 值
            expected_type: 期望类型

        Returns:
            类型是否匹配
        """
        if expected_type == 'path':
            return isinstance(value, (str, Path))

        type_map = {
            'int': int,
            'float': (int, float),
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict
        }

        python_type = type_map.get(expected_type)
        if python_type:
            return isinstance(value, python_type)

        return False

    def _convert_type(self, param_name: str, value: Any, target_type: str) -> Any:
        """
        转换值类型

        Args:
            param_name: 参数名
            value: 值
            target_type: 目标类型

        Returns:
            转换后的值
        """
        try:
            if target_type == 'int':
                return int(value)
            elif target_type == 'float':
                return float(value)
            elif target_type == 'bool':
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif target_type == 'path':
                return Path(value)
            else:
                return value
        except (ValueError, TypeError) as e:
            raise ConfigValidationError(f"参数 {param_name} 类型转换失败: {e}")

    def get_config(self, param_name: Optional[str] = None) -> Any:
        """
        获取配置

        Args:
            param_name: 参数名，如果为None则返回完整配置

        Returns:
            配置值或配置字典
        """
        if param_name is None:
            return self._config.copy()

        return self._config.get(param_name)

    def get_parameter(self, param_name: str) -> Optional[ParameterDefinition]:
        """
        获取参数定义

        Args:
            param_name: 参数名

        Returns:
            参数定义，如果不存在则返回 None
        """
        return self.parameters.get(param_name)

    def list_parameters(self) -> List[str]:
        """
        列出所有参数名

        Returns:
            参数名列表
        """
        return list(self.parameters.keys())

    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置

        Returns:
            默认配置字典
        """
        defaults = {}
        for param_name, param_def in self.parameters.items():
            if param_def.default is not None:
                defaults[param_name] = param_def.default

        return defaults

    def reset_config(self) -> None:
        """重置配置"""
        self._config.clear()
        logger.debug(f"算法 {self.algorithm_id} 配置已重置")

    def export_to_dict(self) -> Dict[str, Any]:
        """
        导出配置为字典

        Returns:
            配置字典
        """
        return {
            'algorithm_id': self.algorithm_id,
            'parameters': {
                name: {
                    'type': param_def.type,
                    'required': param_def.required,
                    'default': param_def.default,
                    'description': param_def.description,
                    'constraints': {
                        'min_value': param_def.constraints.min_value,
                        'max_value': param_def.constraints.max_value,
                        'choices': param_def.constraints.choices,
                    }
                }
                for name, param_def in self.parameters.items()
            },
            'config': self._config
        }

    def import_from_dict(self, data: Dict[str, Any]) -> bool:
        """
        从字典导入配置

        Args:
            data: 配置字典

        Returns:
            导入是否成功
        """
        try:
            if 'parameters' in data:
                # 重建参数定义
                for param_name, param_data in data['parameters'].items():
                    constraints = ParameterConstraint(
                        min_value=param_data.get('constraints', {}).get('min_value'),
                        max_value=param_data.get('constraints', {}).get('max_value'),
                        choices=param_data.get('constraints', {}).get('choices')
                    )

                    param_def = ParameterDefinition(
                        name=param_name,
                        type=param_data['type'],
                        required=param_data.get('required', False),
                        default=param_data.get('default'),
                        description=param_data.get('description', ''),
                        constraints=constraints
                    )

                    self.add_parameter(param_def)

            if 'config' in data:
                # 加载配置
                return self.configure(data['config'])

            return True

        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False

    def validate_config_file(self, config_path: Union[str, Path]) -> bool:
        """
        验证配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            验证是否通过
        """
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                logger.error(f"配置文件不存在: {config_path}")
                return False

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            self.validate_config(config)
            logger.info(f"配置文件 {config_path} 验证通过")
            return True

        except Exception as e:
            logger.error(f"配置文件验证失败: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取配置统计信息

        Returns:
            统计信息字典
        """
        required_count = sum(1 for p in self.parameters.values() if p.required)
        optional_count = len(self.parameters) - required_count
        configured_count = len(self._config)

        return {
            'algorithm_id': self.algorithm_id,
            'total_parameters': len(self.parameters),
            'required_parameters': required_count,
            'optional_parameters': optional_count,
            'configured_parameters': configured_count,
            'completion_rate': configured_count / len(self.parameters) if self.parameters else 0,
            'has_default': sum(1 for p in self.parameters.values() if p.default is not None)
        }

    def __repr__(self) -> str:
        return f"ExtendedAlgorithmConfig(algorithm_id={self.algorithm_id}, parameters={len(self.parameters)})"
