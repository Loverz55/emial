import json
import time
from .models import SystemLog
from django.core.serializers.json import DjangoJSONEncoder

def log_action(request, type, action, content='', level='info', status='success', 
               response_code=None, response_body=None, execution_time=None):
    """
    记录用户操作日志
    :param request: HTTP请求对象
    :param type: 日志类型
    :param action: 操作行为
    :param content: 详细内容
    :param level: 日志级别
    :param status: 操作状态
    :param response_code: 响应状态码
    :param response_body: 响应内容
    :param execution_time: 执行时间(毫秒)
    """
    try:
        # 获取用户IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # 创建日志记录
        SystemLog.objects.create(
            user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
            type=type,
            level=level,
            status=status,
            action=action,
            content=content,
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_method=request.method,
            request_path=request.get_full_path(),
            response_code=response_code,
            response_body=response_body,
            execution_time=execution_time
        )
    except Exception as e:
        print(f"记录日志失败: {str(e)}")  # 在实际生产环境中应该使用proper logging

class LoggerContextManager:
    """
    日志上下文管理器，用于记录API请求的执行时间和响应信息
    使用方式：
    with LoggerContextManager(request, type='api', action='获取用户列表') as logger:
        # 你的代码
        response = ...
        logger.response = response
    """
    def __init__(self, request, type, action, content='', level='info'):
        self.request = request
        self.type = type
        self.action = action
        self.content = content
        self.level = level
        self.start_time = None
        self.response = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = (time.time() - self.start_time) * 1000  # 转换为毫秒
        
        if exc_type is not None:
            # 发生异常
            log_action(
                request=self.request,
                type=self.type,
                action=self.action,
                content=f"{self.content}\n错误: {str(exc_val)}",
                level='error',
                status='failed',
                execution_time=execution_time
            )
        else:
            # 正常响应
            status = 'success' if self.response and 200 <= self.response.status_code < 300 else 'failed'
            response_code = getattr(self.response, 'status_code', None)
            try:
                response_body = self.response.data if hasattr(self.response, 'data') else None
            except:
                response_body = None

            log_action(
                request=self.request,
                type=self.type,
                action=self.action,
                content=self.content,
                level=self.level,
                status=status,
                response_code=response_code,
                response_body=response_body,
                execution_time=execution_time
            )