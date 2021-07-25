from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('two-factor-Authenticaton-verification/', views.two_fa, name='two_fa'),
    path('verification-for-two-factor-Authenticaton-verification/', views.verify_two_fa, name='verify_two_fa'),

    path('logout/', views.logout, name='logout'),
]