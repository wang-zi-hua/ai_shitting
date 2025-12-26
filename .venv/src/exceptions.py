"""
自定义异常类
"""

class UserCancelException(Exception):
    """用户取消操作异常"""
    pass

class UserRollBackException(Exception):
    """用户请求回滚异常"""
    pass

class RetryGenerationException(Exception):
    """请求重新生成异常"""
    pass