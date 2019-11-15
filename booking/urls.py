from django.urls import path

from booking import views

urlpatterns = [
    path('users/', views.CustomUsersList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.CustomUserDetailed.as_view(), name='user-detail')
]
