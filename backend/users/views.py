from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, RegisterSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from logs.utils import log_action

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            log_action(
                request=request,
                type='login',
                action='用户登录',
                content=f'用户 {request.data.get("username")} 登录成功'
            )
        else:
            log_action(
                request=request,
                type='login',
                action='登录失败',
                content=f'用户 {request.data.get("username")} 登录失败',
                level='warning'
            )
        return response

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            log_action(
                request=request,
                type='logout',
                action='用户登出',
                content=f'用户 {request.user.username} 登出系统'
            )
            return Response({
                'detail': '退出成功',
                'code': 200
            })
        except Exception as e:
            log_action(
                request=request,
                type='logout',
                action='登出失败',
                content=f'用户 {request.user.username} 登出失败: {str(e)}',
                level='error'
            )
            return Response({
                'detail': str(e),
                'code': 400
            }, status=400)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'register':
            return [AllowAny()]
        if self.action in ['list', 'retrieve', 'update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def register(self, request):
        """用户注册"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            log_action(
                request=request,
                type='system',
                action='用户注册',
                content=f'新用户 {user.username} 注册成功'
            )
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        log_action(
            request=request,
            type='system',
            action='注册失败',
            content=f'用户注册失败: {serializer.errors}',
            level='warning'
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            log_action(
                request=request,
                type='system',
                action='修改密码失败',
                content='原密码错误',
                level='warning'
            )
            return Response(
                {'error': '原密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        log_action(
            request=request,
            type='system',
            action='修改密码',
            content='密码修改成功'
        )
        return Response({'message': '密码修改成功'}) 