from django.urls import path

from booking import views

urlpatterns = [
    path('users/', views.CustomUsersList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.CustomUserDetail.as_view(), name='user-detail'),
    path('halls/', views.HallsList.as_view(), name='hall-list'),
    path('halls/<int:pk>', views.HallsDetail.as_view(), name='hall-list'),
]
