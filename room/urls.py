from django.urls import path
from . import views

urlpatterns=[
    path('', views.index),
    path('<str:code>/', views.update),
    path('quick_match/<str:game>/', views.quickMatch),
]