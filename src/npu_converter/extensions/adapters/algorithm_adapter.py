"""
算法适配器基类

定义统一的算法适配器接口，所有算法扩展都必须继承此类。
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class BaseAlgorithmAdapter(ABC):
    """
    算法适配器基类

    所有算法扩展都必须继承此类并实现抽象方法。
    提供统一的算法接口，包括初始化、执行、配置、验证等功能。
    """

    # 算法元数据（子类可覆盖）
    VERSION = "1.0.0"
    DESCRIPTION = "基础算法适配器"
    AUTHOR = ""
    CATEGORY = "general"
    DEPENDENCIES = []
    SUPPORTED_FORMATS = []
    PARAMETERS = {}

    def __init__(self):
        """初始化算法适配器"""
        self._initialized = False
        self._configured = False
        self._config: Dict[str, Any] = {}
        self._metadata = self._collect_metadata()

        logger.debug(f"算法适配器 {self.__class__.__name__} 已创建")

    def _collect_metadata(self) -> Dict[str, Any]:
        """收集算法元数据"""
        return {
            'name': self.__class__.__name__,
            'version': self.VERSION,
            'description': self.DESCRIPTION,
            'author': self.AUTHOR,
            'category': self.CATEGORY,
            'dependencies': self.DEPENDENCIES,
            'supported_formats': self.SUPPORTED_FORMATS,
            'parameters': self.PARAMETERS,
            'initialized_at': None,
            'executed_count': 0
        }

    @abstractmethod
    def initialize(self, **kwargs) -> bool:
        """
        初始化算法

        Args:
            **kwargs: 初始化参数

        Returns:
            初始化是否成功

        Raises:
            AlgorithmError: 如果初始化失败
        """
        pass

    @abstractmethod
    def execute(self, input_data: Any, **kwargs) -> Any:
        """
        执行算法

        Args:
            input_data: 输入数据
            **kwargs: 执行参数

        Returns:
            算法执行结果

        Raises:
            AlgorithmError: 如果执行失败
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """
        验证输入数据

        Args:
            input_data: 输入数据

        Returns:
            验证是否通过
        """
        pass

    @abstractmethod
    def validate_output(self, output_data: Any) -> bool:
        """
        验证输出数据

        Args:
            output_data: 输出数据

        Returns:
            验证是否通过
        """
        pass

    def configure(self, config: Dict[str, Any]) -> bool:
        """
        配置算法

        Args:
            config: 配置参数

        Returns:
            配置是否成功
        """
        try:
            # 验证配置
            if not self._validate_config(config):
                logger.error(f"算法 {self.__class__.__name__} 配置验证失败")
                return False

            # 应用配置
            self._config.update(config)
            self._configured = True

            logger.debug(f"算法 {self.__class__.__name__} 配置成功")
            return True

        except Exception as e:
            logger.error(f"算法 {self.__class__.__name__} 配置失败: {e}")
            return False

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置参数

        Args:
            config: 配置参数

        Returns:
            验证是否通过

        Note:
            子类可覆盖此方法以实现自定义验证逻辑
        """
        # 基础验证：检查必需参数
        required_params = self.PARAMETERS.get('required', [])
        for param in required_params:
            if param not in config:
                logger.error(f"缺少必需参数: {param}")
                return False

        return True

    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置

        Returns:
            当前配置字典
        """
        return self._config.copy()

    def reset_config(self) -> None:
        """重置配置"""
        self._config.clear()
        self._configured = False
        logger.debug(f"算法 {self.__class__.__name__} 配置已重置")

    def get_metadata(self) -> Dict[str, Any]:
        """
        获取算法元数据

        Returns:
            元数据字典
        """
        return self._metadata.copy()

    def get_parameter_info(self, param_name: str) -> Optional[Dict[str, Any]]:
        """
        获取参数信息

        Args:
            param_name: 参数名

        Returns:
            参数信息字典，如果不存在则返回 None
        """
        return self.PARAMETERS.get(param_name)

    def list_parameters(self) -> List[str]:
        """
        列出所有参数名

        Returns:
            参数名列表
        """
        return list(self.PARAMETERS.keys())

    def is_initialized(self) -> bool:
        """
        检查是否已初始化

        Returns:
            是否已初始化
        """
        return self._initialized

    def is_configured(self) -> bool:
        """
        检查是否已配置

        Returns:
            是否已配置
        """
        return self._configured

    def set_initialized(self, initialized: bool = True) -> None:
        """
        设置初始化状态

        Args:
            initialized: 是否已初始化
        """
        self._initialized = initialized
        if initialized:
            self._metadata['initialized_at'] = datetime.now().isoformat()

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取算法统计信息

        Returns:
            统计信息字典
        """
        return {
            'name': self.__class__.__name__,
            'version': self.VERSION,
            'initialized': self._initialized,
            'configured': self._configured,
            'execution_count': self._metadata.get('executed_count', 0),
            'last_executed': self._metadata.get('last_executed'),
            'parameters_count': len(self.PARAMETERS),
            'supported_formats_count': len(self.SUPPORTED_FORMATS)
        }

    def preprocess_input(self, input_data: Any, **kwargs) -> Any:
        """
        预处理输入数据

        Args:
            input_data: 输入数据
            **kwargs: 预处理参数

        Returns:
            预处理后的数据

        Note:
            子类可覆盖此方法以实现自定义预处理逻辑
        """
        # 默认实现：直接返回输入数据
        return input_data

    def postprocess_output(self, output_data: Any, **kwargs) -> Any:
        """
        后处理输出数据

        Args:
            output_data: 输出数据
            **kwargs: 后处理参数

        Returns:
            后处理后的数据

        Note:
            子类可覆盖此方法以实现自定义后处理逻辑
        """
        # 默认实现：直接返回输出数据
        return output_data

    def cleanup(self) -> None:
        """
        清理资源

        Note:
            子类可覆盖此方法以实现自定义清理逻辑
        """
        logger.debug(f"算法 {self.__class__.__name__} 资源清理完成")

    def get_health_status(self) -> Dict[str, Any]:
        """
        获取健康状态

        Returns:
            健康状态字典
        """
        return {
            'status': 'healthy' if self._initialized else 'not_initialized',
            'initialized': self._initialized,
            'configured': self._configured,
            'last_check': datetime.now().isoformat()
        }

    def __enter__(self):
        """上下文管理器入口"""
        if not self._initialized:
            self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()


class AlgorithmError(Exception):
    """算法执行异常"""
    pass


class AlgorithmInitializationError(AlgorithmError):
    """算法初始化异常"""
    pass


class AlgorithmExecutionError(AlgorithmError):
    """算法执行异常"""
    pass


class AlgorithmValidationError(AlgorithmError):
    """算法验证异常"""
    pass


class AlgorithmConfigurationError(AlgorithmError):
    """算法配置异常"""
    pass
