from django.urls import path
from . import views

urlpatterns=[
    path('', views.index),
    path('quick_match/<str:game>/', views.quickMatch),
]