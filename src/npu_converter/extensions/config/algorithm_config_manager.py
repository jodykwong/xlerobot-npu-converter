"""
算法配置管理器

提供算法配置加载、验证、更新和管理功能。
"""

import logging
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from threading import Lock
from datetime import datetime
import copy


logger = logging.getLogger(__name__)


class AlgorithmConfigManager:
    """
    算法配置管理器

    管理算法的配置加载、验证、更新和持久化。
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_dir: 配置目录路径，如果为None则使用默认目录
        """
        self._config_dir = Path(config_dir) if config_dir else Path("config/extensions")
        self._config_dir.mkdir(parents=True, exist_ok=True)

        self._configs: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._initialized = False

        logger.info(f"算法配置管理器已初始化，配置目录: {self._config_dir}")

    def initialize(self) -> None:
        """初始化配置管理器"""
        with self._lock:
            if self._initialized:
                logger.warning("配置管理器已经初始化，跳过重复初始化")
                return

            try:
                # 加载默认配置
                self._load_default_configs()

                # 加载所有算法配置
                self._load_all_algorithm_configs()

                self._initialized = True
                logger.info("算法配置管理器初始化完成")

            except Exception as e:
                logger.error(f"配置管理器初始化失败: {e}")
                raise

    def _load_default_configs(self) -> None:
        """加载默认配置"""
        default_config = {
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'algorithms': {}
        }

        default_config_path = self._config_dir / 'default.yaml'
        if default_config_path.exists():
            try:
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config)
                logger.info(f"默认配置已从 {default_config_path} 加载")
            except Exception as e:
                logger.error(f"加载默认配置失败: {e}")

        self._configs['default'] = default_config

    def _load_all_algorithm_configs(self) -> None:
        """加载所有算法配置"""
        try:
            # 遍历配置目录中的所有YAML文件
            for config_file in self._config_dir.glob('*.yaml'):
                if config_file.name == 'default.yaml':
                    continue

                algorithm_id = config_file.stem
                try:
                    self.load_config_from_file(algorithm_id, str(config_file))
                    logger.info(f"算法 {algorithm_id} 配置已加载")
                except Exception as e:
                    logger.error(f"算法 {algorithm_id} 配置加载失败: {e}")

        except Exception as e:
            logger.error(f"加载算法配置失败: {e}")
            raise

    def load_config_from_file(
        self,
        algorithm_id: str,
        config_path: str
    ) -> bool:
        """
        从文件加载配置

        Args:
            algorithm_id: 算法唯一标识符
            config_path: 配置文件路径

        Returns:
            加载是否成功
        """
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {config_path}")

            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.yaml':
                    config = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config = json.load(f)
                else:
                    raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")

            # 验证配置
            if not self.validate_config(config):
                raise ValueError(f"配置文件验证失败: {config_path}")

            # 更新配置
            with self._lock:
                self._configs[algorithm_id] = config
                config['loaded_from'] = str(config_path)
                config['loaded_at'] = datetime.now().isoformat()

            logger.info(f"算法 {algorithm_id} 配置已从 {config_path} 加载")
            return True

        except Exception as e:
            logger.error(f"算法 {algorithm_id} 配置加载失败: {e}")
            return False

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置

        Args:
            config: 配置字典

        Returns:
            验证是否通过
        """
        try:
            # 基础验证
            if not isinstance(config, dict):
                logger.error("配置必须是字典类型")
                return False

            # 验证必需字段
            required_fields = ['algorithm_id', 'parameters']
            for field in required_fields:
                if field not in config:
                    logger.error(f"缺少必需字段: {field}")
                    return False

            # 验证参数
            if not isinstance(config['parameters'], dict):
                logger.error("parameters必须是字典类型")
                return False

            # 验证参数结构
            for param_name, param_config in config['parameters'].items():
                if not isinstance(param_config, dict):
                    logger.error(f"参数 {param_name} 配置必须是字典类型")
                    return False

                # 检查必需字段
                if 'type' not in param_config:
                    logger.error(f"参数 {param_name} 缺少type字段")
                    return False

            return True

        except Exception as e:
            logger.error(f"配置验证异常: {e}")
            return False

    def configure(self, algorithm_id: str, config: Dict[str, Any]) -> bool:
        """
        配置算法

        Args:
            algorithm_id: 算法唯一标识符
            config: 配置参数

        Returns:
            配置是否成功
        """
        with self._lock:
            try:
                # 验证配置
                if not self.validate_config({'algorithm_id': algorithm_id, 'parameters': config}):
                    logger.error(f"算法 {algorithm_id} 配置验证失败")
                    return False

                # 获取或创建算法配置
                if algorithm_id not in self._configs:
                    self._configs[algorithm_id] = {
                        'algorithm_id': algorithm_id,
                        'parameters': {},
                        'created_at': datetime.now().isoformat()
                    }

                # 更新参数
                self._configs[algorithm_id]['parameters'].update(config)
                self._configs[algorithm_id]['updated_at'] = datetime.now().isoformat()

                logger.info(f"算法 {algorithm_id} 配置更新成功")
                return True

            except Exception as e:
                logger.error(f"算法 {algorithm_id} 配置失败: {e}")
                return False

    def get_config(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """
        获取算法配置

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            配置字典，如果不存在则返回 None
        """
        with self._lock:
            config = self._configs.get(algorithm_id)
            if config:
                return copy.deepcopy(config)
            return None

    def get_parameter(self, algorithm_id: str, param_name: str) -> Any:
        """
        获取算法参数值

        Args:
            algorithm_id: 算法唯一标识符
            param_name: 参数名

        Returns:
            参数值，如果不存在则返回 None
        """
        with self._lock:
            config = self._configs.get(algorithm_id)
            if config and 'parameters' in config:
                return config['parameters'].get(param_name)
            return None

    def list_algorithms(self) -> List[str]:
        """
        列出所有已配置的算法

        Returns:
            算法ID列表
        """
        with self._lock:
            return [aid for aid in self._configs.keys() if aid != 'default']

    def delete_config(self, algorithm_id: str) -> bool:
        """
        删除算法配置

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            删除是否成功
        """
        with self._lock:
            if algorithm_id not in self._configs:
                logger.warning(f"算法 {algorithm_id} 配置不存在")
                return False

            del self._configs[algorithm_id]
            logger.info(f"算法 {algorithm_id} 配置已删除")
            return True

    def save_config(self, algorithm_id: str, config_path: Optional[str] = None) -> bool:
        """
        保存配置到文件

        Args:
            algorithm_id: 算法唯一标识符
            config_path: 保存路径，如果为None则使用默认路径

        Returns:
            保存是否成功
        """
        with self._lock:
            if algorithm_id not in self._configs:
                logger.error(f"算法 {algorithm_id} 配置不存在")
                return False

            try:
                if not config_path:
                    config_path = self._config_dir / f"{algorithm_id}.yaml"

                config_path = Path(config_path)
                config_path.parent.mkdir(parents=True, exist_ok=True)

                config_data = self._configs[algorithm_id].copy()

                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

                logger.info(f"算法 {algorithm_id} 配置已保存到 {config_path}")
                return True

            except Exception as e:
                logger.error(f"算法 {algorithm_id} 配置保存失败: {e}")
                return False

    def get_config_count(self) -> int:
        """
        获取已配置算法数量

        Returns:
            配置数量
        """
        with self._lock:
            return len(self._configs) - 1  # 减去default配置

    def get_config_statistics(self) -> Dict[str, Any]:
        """
        获取配置统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            algorithms = self.list_algorithms()
            total_params = sum(
                len(self._configs[aid].get('parameters', {}))
                for aid in algorithms
            )

            return {
                'total_algorithms': len(algorithms),
                'total_parameters': total_params,
                'average_parameters': total_params / len(algorithms) if algorithms else 0,
                'config_dir': str(self._config_dir),
                'timestamp': datetime.now().isoformat()
            }

    def reload_configs(self) -> None:
        """重新加载所有配置"""
        with self._lock:
            try:
                # 清空配置
                self._configs.clear()

                # 重新加载
                self._load_default_configs()
                self._load_all_algorithm_configs()

                logger.info("所有配置已重新加载")

            except Exception as e:
                logger.error(f"重新加载配置失败: {e}")
                raise

    def export_config(self, algorithm_id: str, export_path: str) -> bool:
        """
        导出配置

        Args:
            algorithm_id: 算法唯一标识符
            export_path: 导出路径

        Returns:
            导出是否成功
        """
        with self._lock:
            if algorithm_id not in self._configs:
                logger.error(f"算法 {algorithm_id} 配置不存在")
                return False

            try:
                config_path = Path(export_path)
                config_path.parent.mkdir(parents=True, exist_ok=True)

                config_data = self._configs[algorithm_id].copy()

                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

                logger.info(f"算法 {algorithm_id} 配置已导出到 {export_path}")
                return True

            except Exception as e:
                logger.error(f"算法 {algorithm_id} 配置导出失败: {e}")
                return False

    def import_config(self, import_path: str, algorithm_id: Optional[str] = None) -> bool:
        """
        导入配置

        Args:
            import_path: 导入路径
            algorithm_id: 算法ID，如果为None则从配置文件读取

        Returns:
            导入是否成功
        """
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                logger.error(f"导入文件不存在: {import_path}")
                return False

            with open(import_path, 'r', encoding='utf-8') as f:
                if import_path.suffix.lower() == '.yaml':
                    config = yaml.safe_load(f)
                elif import_path.suffix.lower() == '.json':
                    config = json.load(f)
                else:
                    raise ValueError(f"不支持的文件格式: {import_path.suffix}")

            # 确定算法ID
            if not algorithm_id:
                algorithm_id = config.get('algorithm_id', import_path.stem)

            # 验证配置
            if not self.validate_config(config):
                logger.error(f"导入配置验证失败: {import_path}")
                return False

            # 加载配置
            return self.load_config_from_file(algorithm_id, str(import_path))

        except Exception as e:
            logger.error(f"配置导入失败: {e}")
            return False
