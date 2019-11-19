from django.urls import path

from booking import views

urlpatterns = [
    path('users/', views.CustomListByUser.as_view(), name='user-list'),
    path('users/<int:pk>/', views.CustomUserDetail.as_view(), name='user-detail'),
    path('halls/', views.HallsList.as_view(), name='hall-list'),
    path('halls/<int:pk>/', views.HallsDetail.as_view(), name='hall-list'),
    path('movies/', views.MoviesListView.as_view(), name='movie-list'),
    path('movies/<int:pk>/', views.MoviesDetail.as_view(), name='movie-list'),
    path('showings/', views.ShowingsListView.as_view(), name='showing-list'),
    path('showings/<int:pk>/', views.ShowingsDetail.as_view(), name='showing-detail'),
    path('tickets/', views.TicketsListView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.TicketsDetail.as_view(), name='ticket-detail'),
    path('tickets/<int:pk>/pay/', views.PayForTicket.as_view(), name='pay'),
]
