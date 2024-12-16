import time
import json
from .utils import log_action
from django.utils.deprecation import MiddlewareMixin

class APILoggingMiddleware(MiddlewareMixin):
    """API请求日志中间件"""

    def should_log(self, request):
        """判断是否需要记录日志"""
        # 排除静态文件和管理员页面
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return False
            
        # 排除健康检查等接口
        if request.path in ['/health/', '/ping/']:
            return False
            
        return True

    def process_request(self, request):
        if not self.should_log(request):
            return None

        # 保存原始请求体
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = request.body
                request._body = body
                request._body_content = body.decode('utf-8')
            except Exception:
                request._body_content = ''
        return None

    def process_response(self, request, response):
        if not self.should_log(request):
            return response

        try:
            # 获取请求体内容
            request_body = ''
            if hasattr(request, '_body_content'):
                request_body = request._body_content
                try:
                    body_data = json.loads(request_body)
                    # 过滤敏感信息
                    sensitive_fields = ['password', 'token', 'access', 'refresh']
                    for field in sensitive_fields:
                        if field in body_data:
                            body_data[field] = '******'
                    request_body = json.dumps(body_data)
                except:
                    pass

            # 获取响应内容
            try:
                if hasattr(response, 'data'):
                    response_body = response.data
                else:
                    response_body = None
            except:
                response_body = None

            # 记录日志
            log_action(
                request=request,
                type='api',
                action=f"{request.method} {request.path}",
                content=request_body,
                level='info' if 200 <= response.status_code < 400 else 'error',
                status='success' if 200 <= response.status_code < 400 else 'failed',
                response_code=response.status_code,
                response_body=response_body,
                execution_time=0  # 暂时不计算执行时间
            )
        except Exception as e:
            print(f"记录日志失败: {str(e)}")

        return response