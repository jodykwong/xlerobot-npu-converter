"""
算法生命周期管理

提供算法生命周期钩子和事件处理功能。
"""

import logging
from typing import Dict, List, Callable, Any, Optional
from threading import Lock
from datetime import datetime
from enum import Enum
import weakref


logger = logging.getLogger(__name__)


class LifecycleEvent(Enum):
    """生命周期事件枚举"""
    # 初始化事件
    BEFORE_INITIALIZE = "before_initialize"
    AFTER_INITIALIZE = "after_initialize"

    # 配置事件
    BEFORE_CONFIGURE = "before_configure"
    AFTER_CONFIGURE = "after_configure"

    # 执行事件
    BEFORE_EXECUTE = "before_execute"
    AFTER_EXECUTE = "after_execute"
    EXECUTE_FAILED = "execute_failed"

    # 注销事件
    BEFORE_UNREGISTER = "before_unregister"
    AFTER_UNREGISTER = "after_unregister"

    # 关闭事件
    BEFORE_SHUTDOWN = "before_shutdown"
    AFTER_SHUTDOWN = "after_shutdown"

    # 自定义事件
    CUSTOM_EVENT = "custom_event"


class AlgorithmLifecycle:
    """
    算法生命周期管理器

    管理算法的生命周期事件和钩子。
    提供事件监听、触发和处理功能。
    """

    def __init__(self):
        """初始化生命周期管理器"""
        self._listeners: Dict[str, List[Callable]] = {}
        self._lock = Lock()
        self._initialized = False
        self._event_history: List[Dict[str, Any]] = []

        # 注册默认事件
        self._register_default_events()

        logger.info("算法生命周期管理器已初始化")

    def _register_default_events(self) -> None:
        """注册默认事件"""
        default_events = [
            event.value for event in LifecycleEvent
        ]
        for event in default_events:
            self._listeners[event] = []

    def initialize(self) -> None:
        """初始化生命周期管理器"""
        with self._lock:
            if self._initialized:
                logger.warning("生命周期管理器已经初始化")
                return

            self._initialized = True
            logger.info("算法生命周期管理器初始化完成")

    def add_listener(self, event: str, listener: Callable) -> bool:
        """
        添加事件监听器

        Args:
            event: 事件名称
            listener: 监听器函数

        Returns:
            添加是否成功
        """
        with self._lock:
            try:
                # 确保事件已注册
                if event not in self._listeners:
                    self._listeners[event] = []

                # 添加监听器（使用弱引用避免循环引用）
                self._listeners[event].append(weakref.WeakMethod(listener) if callable(listener) else listener)

                logger.debug(f"事件 {event} 监听器已添加")
                return True

            except Exception as e:
                logger.error(f"添加事件 {event} 监听器失败: {e}")
                return False

    def remove_listener(self, event: str, listener: Callable) -> bool:
        """
        移除事件监听器

        Args:
            event: 事件名称
            listener: 监听器函数

        Returns:
            移除是否成功
        """
        with self._lock:
            try:
                if event not in self._listeners:
                    logger.warning(f"事件 {event} 不存在")
                    return False

                # 尝试移除监听器
                listeners = self._listeners[event]
                for i, l in enumerate(listeners):
                    # 比较监听器
                    if (hasattr(l, '__self__') and hasattr(listener, '__self__') and
                        l.__self__ is listener.__self__ and
                        hasattr(l, '__func__') and hasattr(listener, '__func__') and
                        l.__func__ is listener.__func__):
                        listeners.pop(i)
                        logger.debug(f"事件 {event} 监听器已移除")
                        return True

                logger.warning(f"未找到要移除的事件 {event} 监听器")
                return False

            except Exception as e:
                logger.error(f"移除事件 {event} 监听器失败: {e}")
                return False

    def emit_event(self, event: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        触发事件

        Args:
            event: 事件名称
            context: 事件上下文

        Note:
            如果事件监听器执行失败，不会阻止其他监听器执行
        """
        if not self._initialized:
            logger.warning("生命周期管理器未初始化，无法触发事件")
            return

        event_context = context or {}
        event_context['event'] = event
        event_context['timestamp'] = datetime.now().isoformat()

        # 记录事件历史
        with self._lock:
            self._event_history.append(event_context.copy())
            # 保留最近1000个事件
            if len(self._event_history) > 1000:
                self._event_history = self._event_history[-1000:]

        # 触发监听器
        with self._lock:
            listeners = self._listeners.get(event, [])

        for listener in listeners:
            try:
                # 处理弱引用
                if hasattr(listener, '__call__'):
                    listener(event_context)
            except Exception as e:
                logger.error(f"事件 {event} 监听器执行失败: {e}")

        logger.debug(f"事件 {event} 已触发，{len(listeners)} 个监听器执行")

    def get_listeners(self, event: str) -> List[Callable]:
        """
        获取事件监听器列表

        Args:
            event: 事件名称

        Returns:
            监听器列表
        """
        with self._lock:
            return self._listeners.get(event, []).copy()

    def get_listener_count(self) -> int:
        """
        获取监听器总数

        Returns:
            监听器数量
        """
        with self._lock:
            return sum(len(listeners) for listeners in self._listeners.values())

    def get_events(self) -> List[str]:
        """
        获取所有已注册的事件

        Returns:
            事件列表
        """
        with self._lock:
            return list(self._listeners.keys())

    def get_event_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取事件历史

        Args:
            limit: 返回记录数量限制

        Returns:
            事件历史列表
        """
        with self._lock:
            history = self._event_history.copy()
            if limit:
                history = history[-limit:]
            return history

    def clear_event_history(self) -> None:
        """清空事件历史"""
        with self._lock:
            self._event_history.clear()
            logger.info("事件历史已清空")

    def create_event_hook(self, event: str) -> Callable:
        """
        创建事件钩子装饰器

        Args:
            event: 事件名称

        Returns:
            装饰器函数

        Example:
            @lifecycle.create_event_hook('before_execute')
            def my_hook(context):
                print(f"执行前钩子: {context}")
        """
        def decorator(func: Callable) -> Callable:
            self.add_listener(event, func)
            return func
        return decorator

    def wait_for_event(self, event: str, timeout: Optional[float] = None) -> bool:
        """
        等待事件触发（简单实现）

        Args:
            event: 事件名称
            timeout: 超时时间（秒）

        Returns:
            是否在超时前触发

        Note:
            这是一个简单实现，实际应用中可能需要更复杂的同步机制
        """
        import time
        start_time = time.time()

        # 记录当前事件数量
        with self._lock:
            current_count = len(self._event_history)

        while True:
            # 检查是否触发
            with self._lock:
                if len(self._event_history) > current_count:
                    # 检查最新事件是否为目标事件
                    latest_event = self._event_history[-1]
                    if latest_event.get('event') == event:
                        return True

            # 检查超时
            if timeout and (time.time() - start_time) >= timeout:
                return False

            # 短暂休眠
            time.sleep(0.1)

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取生命周期统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            return {
                'initialized': self._initialized,
                'total_events': len(self._listeners),
                'total_listeners': self.get_listener_count(),
                'event_history_count': len(self._event_history),
                'events': list(self._listeners.keys()),
                'timestamp': datetime.now().isoformat()
            }

    def shutdown(self) -> None:
        """关闭生命周期管理器"""
        with self._lock:
            if not self._initialized:
                return

            # 触发关闭事件
            self.emit_event(LifecycleEvent.AFTER_SHUTDOWN.value, {})

            # 清空监听器
            self._listeners.clear()

            self._initialized = False
            logger.info("算法生命周期管理器已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.shutdown()
