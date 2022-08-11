from django.urls import path
from . import views

urlpatterns=[
    path('signup/', views.signup),
    path('login/', views.login),
    path('check/', views.check),
    path('logout/', views.logout),
    path('user/', views.user),
    path('record/', views.record),
    path('ranking/', views.ranking),
]