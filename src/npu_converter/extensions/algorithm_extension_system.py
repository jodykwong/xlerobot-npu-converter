"""
算法扩展系统核心架构

提供统一的算法扩展能力，支持动态算法注册、发现、适配和管理。
"""

import logging
from typing import Dict, List, Optional, Type, Any
from threading import Lock
from datetime import datetime

from .algorithm_registry import AlgorithmRegistry
from .config.algorithm_config_manager import AlgorithmConfigManager
from .lifecycle.algorithm_lifecycle import AlgorithmLifecycle
from .adapters.algorithm_adapter import BaseAlgorithmAdapter


logger = logging.getLogger(__name__)


class AlgorithmExtensionSystem:
    """
    算法扩展系统核心类

    提供统一的算法扩展能力，包括：
    - 动态算法注册和发现
    - 算法适配和集成
    - 算法配置管理
    - 算法生命周期管理
    """

    def __init__(self):
        """初始化算法扩展系统"""
        self._registry = AlgorithmRegistry()
        self._config_manager = AlgorithmConfigManager()
        self._lifecycle = AlgorithmLifecycle()
        self._lock = Lock()
        self._initialized = False

        logger.info("算法扩展系统已初始化")

    def initialize(self) -> None:
        """初始化系统组件"""
        with self._lock:
            if self._initialized:
                logger.warning("算法扩展系统已经初始化，跳过重复初始化")
                return

            try:
                # 初始化配置管理器
                self._config_manager.initialize()
                logger.info("配置管理器初始化完成")

                # 初始化生命周期管理器
                self._lifecycle.initialize()
                logger.info("生命周期管理器初始化完成")

                # 加载已注册的算法
                self._load_registered_algorithms()
                logger.info("已注册算法加载完成")

                self._initialized = True
                logger.info("算法扩展系统初始化完成")

            except Exception as e:
                logger.error(f"算法扩展系统初始化失败: {e}")
                raise

    def _load_registered_algorithms(self) -> None:
        """加载已注册的算法"""
        try:
            algorithms = self._registry.list_algorithms()
            for algorithm_id in algorithms:
                try:
                    self._initialize_algorithm(algorithm_id)
                except Exception as e:
                    logger.error(f"算法 {algorithm_id} 初始化失败: {e}")

        except Exception as e:
            logger.error(f"加载已注册算法失败: {e}")
            raise

    def _initialize_algorithm(self, algorithm_id: str) -> None:
        """初始化单个算法"""
        try:
            # 获取算法信息
            algorithm_info = self._registry.get_algorithm_info(algorithm_id)
            if not algorithm_info:
                logger.warning(f"算法 {algorithm_id} 信息不存在")
                return

            # 触发初始化钩子
            self._lifecycle.emit_event('before_initialize', {
                'algorithm_id': algorithm_id,
                'algorithm_info': algorithm_info
            })

            # 执行初始化逻辑（子类实现）
            self._do_initialize_algorithm(algorithm_id, algorithm_info)

            # 触发初始化完成钩子
            self._lifecycle.emit_event('after_initialize', {
                'algorithm_id': algorithm_id,
                'timestamp': datetime.now()
            })

            logger.info(f"算法 {algorithm_id} 初始化完成")

        except Exception as e:
            logger.error(f"算法 {algorithm_id} 初始化异常: {e}")
            raise

    def _do_initialize_algorithm(self, algorithm_id: str, algorithm_info: Dict[str, Any]) -> None:
        """执行算法初始化逻辑（子类可覆盖）"""
        # 默认实现为空，子类可根据需要覆盖
        pass

    def register_algorithm(
        self,
        algorithm_id: str,
        algorithm_class: Type[BaseAlgorithmAdapter],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        注册算法

        Args:
            algorithm_id: 算法唯一标识符
            algorithm_class: 算法适配器类
            metadata: 算法元数据

        Returns:
            注册是否成功
        """
        with self._lock:
            try:
                # 验证算法类
                if not issubclass(algorithm_class, BaseAlgorithmAdapter):
                    raise ValueError(f"算法类必须继承自 BaseAlgorithmAdapter")

                # 注册算法
                success = self._registry.register(
                    algorithm_id=algorithm_id,
                    algorithm_class=algorithm_class,
                    metadata=metadata or {}
                )

                if success:
                    logger.info(f"算法 {algorithm_id} 注册成功")
                    # 初始化算法（如果系统已初始化）
                    if self._initialized:
                        self._initialize_algorithm(algorithm_id)

                return success

            except Exception as e:
                logger.error(f"算法 {algorithm_id} 注册失败: {e}")
                return False

    def unregister_algorithm(self, algorithm_id: str) -> bool:
        """
        注销算法

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            注销是否成功
        """
        with self._lock:
            try:
                # 触发注销前钩子
                self._lifecycle.emit_event('before_unregister', {
                    'algorithm_id': algorithm_id
                })

                # 执行注销逻辑
                success = self._do_unregister_algorithm(algorithm_id)

                if success:
                    # 从注册表删除
                    self._registry.unregister(algorithm_id)

                    # 触发注销后钩子
                    self._lifecycle.emit_event('after_unregister', {
                        'algorithm_id': algorithm_id,
                        'timestamp': datetime.now()
                    })

                    logger.info(f"算法 {algorithm_id} 注销成功")

                return success

            except Exception as e:
                logger.error(f"算法 {algorithm_id} 注销失败: {e}")
                return False

    def _do_unregister_algorithm(self, algorithm_id: str) -> bool:
        """执行算法注销逻辑（子类可覆盖）"""
        # 默认实现为空，子类可根据需要覆盖
        return True

    def get_algorithm(self, algorithm_id: str) -> Optional[BaseAlgorithmAdapter]:
        """
        获取算法实例

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            算法实例，如果不存在则返回 None
        """
        try:
            return self._registry.get_algorithm(algorithm_id)

        except Exception as e:
            logger.error(f"获取算法 {algorithm_id} 失败: {e}")
            return None

    def list_algorithms(self) -> List[str]:
        """
        列出所有已注册的算法

        Returns:
            算法ID列表
        """
        return self._registry.list_algorithms()

    def get_algorithm_info(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """
        获取算法信息

        Args:
            algorithm_id: 算法唯一标识符

        Returns:
            算法信息字典
        """
        return self._registry.get_algorithm_info(algorithm_id)

    def configure_algorithm(self, algorithm_id: str, config: Dict[str, Any]) -> bool:
        """
        配置算法

        Args:
            algorithm_id: 算法唯一标识符
            config: 配置参数

        Returns:
            配置是否成功
        """
        try:
            # 触发配置前钩子
            self._lifecycle.emit_event('before_configure', {
                'algorithm_id': algorithm_id,
                'config': config
            })

            # 执行配置
            success = self._config_manager.configure(algorithm_id, config)

            if success:
                # 触发配置后钩子
                self._lifecycle.emit_event('after_configure', {
                    'algorithm_id': algorithm_id,
                    'config': config,
                    'timestamp': datetime.now()
                })

                logger.info(f"算法 {algorithm_id} 配置成功")

            return success

        except Exception as e:
            logger.error(f"算法 {algorithm_id} 配置失败: {e}")
            return False

    def execute_algorithm(
        self,
        algorithm_id: str,
        input_data: Any,
        **kwargs
    ) -> Optional[Any]:
        """
        执行算法

        Args:
            algorithm_id: 算法唯一标识符
            input_data: 输入数据
            **kwargs: 其他参数

        Returns:
            算法执行结果
        """
        try:
            # 触发执行前钩子
            self._lifecycle.emit_event('before_execute', {
                'algorithm_id': algorithm_id,
                'input_data': input_data,
                'kwargs': kwargs
            })

            # 获取算法实例
            algorithm = self.get_algorithm(algorithm_id)
            if not algorithm:
                raise ValueError(f"算法 {algorithm_id} 不存在")

            # 执行算法
            result = algorithm.execute(input_data, **kwargs)

            # 触发执行后钩子
            self._lifecycle.emit_event('after_execute', {
                'algorithm_id': algorithm_id,
                'result': result,
                'timestamp': datetime.now()
            })

            logger.info(f"算法 {algorithm_id} 执行成功")
            return result

        except Exception as e:
            logger.error(f"算法 {algorithm_id} 执行失败: {e}")
            self._lifecycle.emit_event('execute_failed', {
                'algorithm_id': algorithm_id,
                'error': str(e),
                'timestamp': datetime.now()
            })
            raise

    def add_lifecycle_listener(self, event: str, listener: callable) -> None:
        """
        添加生命周期事件监听器

        Args:
            event: 事件名称
            listener: 监听器函数
        """
        self._lifecycle.add_listener(event, listener)

    def remove_lifecycle_listener(self, event: str, listener: callable) -> None:
        """
        移除生命周期事件监听器

        Args:
            event: 事件名称
            listener: 监听器函数
        """
        self._lifecycle.remove_listener(event, listener)

    def shutdown(self) -> None:
        """关闭系统"""
        with self._lock:
            if not self._initialized:
                logger.warning("系统未初始化，无需关闭")
                return

            try:
                # 触发关闭前钩子
                self._lifecycle.emit_event('before_shutdown', {
                    'timestamp': datetime.now()
                })

                # 执行关闭逻辑
                self._do_shutdown()

                # 触发关闭后钩子
                self._lifecycle.emit_event('after_shutdown', {
                    'timestamp': datetime.now()
                })

                self._initialized = False
                logger.info("算法扩展系统已关闭")

            except Exception as e:
                logger.error(f"系统关闭失败: {e}")
                raise

    def _do_shutdown(self) -> None:
        """执行关闭逻辑（子类可覆盖）"""
        # 默认实现为空，子类可根据需要覆盖
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取系统统计信息

        Returns:
            统计信息字典
        """
        return {
            'initialized': self._initialized,
            'registered_algorithms': len(self._registry.list_algorithms()),
            'configuration_count': self._config_manager.get_config_count(),
            'lifecycle_listeners': self._lifecycle.get_listener_count(),
            'timestamp': datetime.now().isoformat()
        }
