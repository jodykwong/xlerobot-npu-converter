"""
算法注册管理器

提供算法动态注册、发现和元数据管理功能。
"""

import logging
from typing import Dict, List, Optional, Type, Any
from threading import Lock
from datetime import datetime
import inspect


logger = logging.getLogger(__name__)


class AlgorithmRegistry:
    """
    算法注册表

    管理算法的注册、发现和元数据信息。
    """

    def __init__(self):
        """初始化算法注册表"""
        self._algorithms: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

        logger.info("算法注册表已初始化")

    def register(
        self,
        algorithm_id: str,
        algorithm_class: Type,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        注册算法

        Args:
            algorithm_id: 算法唯一标识符
            algorithm_class: 算法类
            metadata: 算法元数据

        Returns:
            注册是否成功

        Raises:
            ValueError: 如果算法ID已存在或参数无效
        """
        with self._lock:
            try:
                # 验证参数
                if not algorithm_id or not isinstance(algorithm_id, str):
                    raise ValueError("算法ID不能为空")

                if not inspect.isclass(algorithm_class):
                    raise ValueError("algorithm_class必须是类")

                # 检查算法ID是否已存在
                if algorithm_id in self._algorithms:
                    logger.warning(f"算法 {algorithm_id} 已存在，将被覆盖")

                # 生成元数据
                algorithm_metadata = self._generate_metadata(
                    algorithm_class,
                    metadata or {}
                )

                # 注册算法
                self._algorithms[algorithm_id] = {
                    'class': algorithm_class,
                    'metadata': algorithm_metadata,
                    'registered_at': datetime.now(),
                    'instance': None  # 延迟实例化
                }

                logger.info(f"算法 {algorithm_id} 注册成功")
                return True

            except Exception as e:
                logger.error(f"算法 {algorithm_id} 注册失败: {e}")
                return False

    def _generate_metadata(
        self,
        algorithm_class: Type,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成算法元数据"""
        default_metadata = {
            'name': algorithm_class.__name__,
            'module': algorithm_class.__module__,
            'doc': algorithm_class.__doc__ or '',
            'version': getattr(algorithm_class, 'VERSION', '1.0.0'),
            'description': getattr(algorithm_class, 'DESCRIPTION', ''),
            'author': getattr(algorithm_class, 'AUTHOR', ''),
            'dependencies': getattr(algorithm_class, 'DEPENDENCIES', []),
            'supported_formats': getattr(algorithm_class, 'SUPPORTED_FORMATS', []),
            'parameters': getattr(algorithm_class, 'PARAMETERS', {}),
        }

        # 合并用户提供的元数据
        default_metadata.update(metadata)

        return default_metadata

    def unregister(self, algorithm_id: str) -> bool:
        """
        注销算法

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            注销是否成功
        """
        with self._lock:
            try:
                if algorithm_id not in self._algorithms:
                    logger.warning(f"算法 {algorithm_id} 不存在")
                    return False

                # 删除算法
                del self._algorithms[algorithm_id]

                logger.info(f"算法 {algorithm_id} 注销成功")
                return True

            except Exception as e:
                logger.error(f"算法 {algorithm_id} 注销失败: {e}")
                return False

    def get_algorithm(self, algorithm_id: str):
        """
        获取算法实例

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            算法实例，如果不存在则返回 None

        Raises:
            Exception: 如果算法实例化失败
        """
        with self._lock:
            try:
                if algorithm_id not in self._algorithms:
                    return None

                algorithm_info = self._algorithms[algorithm_id]

                # 如果已有实例，直接返回
                if algorithm_info['instance'] is not None:
                    return algorithm_info['instance']

                # 创建新实例
                algorithm_class = algorithm_info['class']
                instance = algorithm_class()
                algorithm_info['instance'] = instance

                logger.debug(f"算法 {algorithm_id} 实例化成功")
                return instance

            except Exception as e:
                logger.error(f"算法 {algorithm_id} 实例化失败: {e}")
                raise

    def get_algorithm_info(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """
        获取算法信息

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            算法信息字典，如果不存在则返回 None
        """
        with self._lock:
            algorithm_info = self._algorithms.get(algorithm_id)
            if not algorithm_info:
                return None

            # 返回元数据副本（不包含类引用）
            return algorithm_info['metadata'].copy()

    def list_algorithms(self) -> List[str]:
        """
        列出所有已注册的算法

        Returns:
            算法ID列表
        """
        with self._lock:
            return list(self._algorithms.keys())

    def get_algorithm_count(self) -> int:
        """
        获取已注册算法数量

        Returns:
            算法数量
        """
        with self._lock:
            return len(self._algorithms)

    def search_algorithms(
        self,
        query: str,
        search_fields: Optional[List[str]] = None
    ) -> List[str]:
        """
        搜索算法

        Args:
            query: 搜索关键词
            search_fields: 搜索字段列表，默认为 ['name', 'description']

        Returns:
            匹配算法ID列表
        """
        if not search_fields:
            search_fields = ['name', 'description']

        with self._lock:
            results = []
            query_lower = query.lower()

            for algorithm_id, algorithm_info in self._algorithms.items():
                metadata = algorithm_info['metadata']

                # 在指定字段中搜索
                for field in search_fields:
                    if field in metadata:
                        value = str(metadata[field]).lower()
                        if query_lower in value:
                            results.append(algorithm_id)
                            break

            return results

    def get_algorithms_by_category(self, category: str) -> List[str]:
        """
        按类别获取算法

        Args:
            category: 类别名称

        Returns:
            属于该类别的算法ID列表
        """
        with self._lock:
            results = []

            for algorithm_id, algorithm_info in self._algorithms.items():
                metadata = algorithm_info['metadata']
                algorithm_category = metadata.get('category', '')

                if algorithm_category.lower() == category.lower():
                    results.append(algorithm_id)

            return results

    def get_algorithm_dependencies(self, algorithm_id: str) -> List[str]:
        """
        获取算法依赖

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            依赖列表
        """
        with self._lock:
            if algorithm_id not in self._algorithms:
                return []

            metadata = self._algorithms[algorithm_id]['metadata']
            return metadata.get('dependencies', [])

    def check_dependencies(self, algorithm_id: str) -> Dict[str, bool]:
        """
        检查算法依赖

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            依赖检查结果字典 {依赖名: 是否满足}
        """
        with self._lock:
            dependencies = self.get_algorithm_dependencies(algorithm_id)
            results = {}

            # 这里可以实现依赖检查逻辑
            # 例如检查Python包、模型文件等是否存在
            for dep in dependencies:
                # 默认假设依赖满足，实际应用中需要实现具体检查逻辑
                results[dep] = True

            return results

    def validate_algorithm(self, algorithm_id: str) -> Dict[str, Any]:
        """
        验证算法

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            验证结果字典
        """
        with self._lock:
            result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }

            try:
                if algorithm_id not in self._algorithms:
                    result['valid'] = False
                    result['errors'].append(f"算法 {algorithm_id} 不存在")
                    return result

                algorithm_info = self._algorithms[algorithm_id]
                metadata = algorithm_info['metadata']

                # 检查必需字段
                required_fields = ['name', 'version']
                for field in required_fields:
                    if field not in metadata or not metadata[field]:
                        result['warnings'].append(f"缺少推荐字段: {field}")

                # 检查依赖
                dependencies = metadata.get('dependencies', [])
                if dependencies:
                    dep_results = self.check_dependencies(algorithm_id)
                    missing_deps = [dep for dep, satisfied in dep_results.items() if not satisfied]
                    if missing_deps:
                        result['valid'] = False
                        result['errors'].append(f"缺少依赖: {', '.join(missing_deps)}")

                # 尝试实例化
                try:
                    instance = self.get_algorithm(algorithm_id)
                    if instance is None:
                        result['valid'] = False
                        result['errors'].append("算法实例化失败")
                except Exception as e:
                    result['valid'] = False
                    result['errors'].append(f"实例化异常: {str(e)}")

            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"验证异常: {str(e)}")

            return result

    def get_registry_status(self) -> Dict[str, Any]:
        """
        获取注册表状态

        Returns:
            状态字典
        """
        with self._lock:
            return {
                'total_algorithms': len(self._algorithms),
                'algorithms': list(self._algorithms.keys()),
                'categories': list(set(
                    info['metadata'].get('category', '')
                    for info in self._algorithms.values()
                )),
                'timestamp': datetime.now().isoformat()
            }

    def clear(self) -> None:
        """清空注册表"""
        with self._lock:
            self._algorithms.clear()
            logger.info("算法注册表已清空")
