from django.urls import path
from .views import (
    DashboardStatsView, 
    RecentTasksView, 
    WeeklyStatsView,
    AdminDashboardStatsView,
    AdminChartDataView,
    SystemActivitiesView,
    RecentUsersView,
    PopularTemplatesView
)

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('recent-tasks/', RecentTasksView.as_view(), name='recent-tasks'),
    path('weekly-stats/', WeeklyStatsView.as_view(), name='weekly-stats'),
    
    # 管理后台接口
    path('admin/stats/', AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('admin/chart/', AdminChartDataView.as_view(), name='admin-chart-data'),
    path('admin/activities/', SystemActivitiesView.as_view(), name='system-activities'),
    path('admin/recent-users/', RecentUsersView.as_view(), name='recent-users'),
    path('admin/popular-templates/', PopularTemplatesView.as_view(), name='popular-templates'),
] 