from django.urls import path
from . import views

urlpatterns = [
  
    path("", views.dashboard, name='dashboard'),
    path("home/", views.home, name='home'),
    path('terms/', views.terms, name='terms'),
    path('about/', views.about, name='about'),

    
    path('admin/logout/', views.logout_view, name='logout'),
     
    
]
